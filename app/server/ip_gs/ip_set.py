from __future__ import annotations

import sys
import argparse
import time
import logging
from pathlib import Path
from typing import Any

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from Loger import logger

from ip_gs.common import (
    DEFAULT_SETTINGS_PATH,
    IP_GS_DIR,
    IpGsError,
    format_mac,
    iter_profiles,
    load_settings,
    log_ps_failure,
    normalize_ps_list,
    ps_json,
    require_admin,
    run_powershell,
)

class AdapterNotFoundError(IpGsError):
    pass


def ensure_file_logging() -> Path:
    log_path = IP_GS_DIR / "ip_set.log"
    try:
        IP_GS_DIR.mkdir(parents=True, exist_ok=True)
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                try:
                    if Path(getattr(handler, "baseFilename", "")).resolve() == log_path.resolve():
                        return log_path
                except Exception:
                    continue
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
    except Exception:
        pass
    return log_path


def get_ipv4_state(if_index: int) -> dict[str, Any]:
    script = rf"""
$ErrorActionPreference = "Stop"
$if = {if_index}
$ip = Get-NetIPAddress -InterfaceIndex $if -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Where-Object {{ $_.IPAddress -ne "127.0.0.1" }} |
  Select-Object IPAddress, PrefixLength, AddressState, Type
$gw = Get-NetRoute -InterfaceIndex $if -AddressFamily IPv4 -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
  Select-Object -First 1 NextHop
$dns = Get-DnsClientServerAddress -InterfaceIndex $if -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty ServerAddresses
$dhcp = Get-NetIPInterface -InterfaceIndex $if -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Select-Object -First 1 Dhcp
@{{ ip = $ip; gateway = $gw; dns_servers = $dns; dhcp = $dhcp }} | ConvertTo-Json -Depth 6
"""
    data = ps_json(script) or {}
    data["ip"] = [x for x in normalize_ps_list(data.get("ip")) if isinstance(x, dict)]
    dns = normalize_ps_list(data.get("dns_servers"))
    data["dns_servers"] = [x for x in dns if isinstance(x, str) and x]
    dhcp_obj = data.get("dhcp") or {}
    dhcp_raw = dhcp_obj.get("Dhcp") if isinstance(dhcp_obj, dict) else None
    if isinstance(dhcp_raw, bool):
        data["dhcp_enabled"] = dhcp_raw
    elif isinstance(dhcp_raw, int):
        data["dhcp_enabled"] = (dhcp_raw == 1)
    else:
        val = str(dhcp_raw or "").strip().lower()
        if val in {"enabled", "enable", "true", "1"}:
            data["dhcp_enabled"] = True
        elif val in {"disabled", "disable", "false", "0"}:
            data["dhcp_enabled"] = False
        else:
            data["dhcp_enabled"] = None
    return data


def is_profile_already_applied(profile: dict[str, Any], state: dict[str, Any]) -> bool:
    want_dhcp = bool(profile.get("dhcp"))
    dhcp_enabled = state.get("dhcp_enabled")
    if want_dhcp:
        return dhcp_enabled is True

    ipv4 = profile.get("ipv4") or {}
    want_ip = str(ipv4.get("address") or "").strip()
    want_prefix = ipv4.get("prefix_length")
    want_gw = str(ipv4.get("gateway") or "").strip()
    want_dns = [str(x) for x in (profile.get("dns_servers") or []) if str(x).strip()]

    if not want_ip or want_prefix is None:
        return False

    if dhcp_enabled is True:
        return False

    have_ips = state.get("ip") or []
    ip_match = any(
        str(item.get("IPAddress") or "") == want_ip and int(item.get("PrefixLength") or -1) == int(want_prefix)
        for item in have_ips
        if isinstance(item, dict)
    )
    if not ip_match:
        return False

    if want_gw:
        gw_obj = state.get("gateway")
        have_gw = str(gw_obj.get("NextHop") or "") if isinstance(gw_obj, dict) else ""
        if have_gw != want_gw:
            return False

    if want_dns:
        have_dns = [str(x) for x in (state.get("dns_servers") or []) if str(x).strip()]
        if have_dns != want_dns:
            return False

    return True


def remove_conflicting_ip(ip: str, target_if_index: int, dry_run: bool) -> None:
    ip = str(ip or "").strip()
    if not ip:
        return
    if dry_run:
        logger.info("[dry-run] remove conflicting ip=%s (exclude ifIndex=%s)", ip, target_if_index)
        return

    script = rf"""
$ErrorActionPreference = "Stop"
$target = {target_if_index}
$before = Get-NetIPAddress -AddressFamily IPv4 -IPAddress "{ip}" -ErrorAction SilentlyContinue |
  Where-Object {{ $_.InterfaceIndex -ne $target }} |
  Select-Object InterfaceIndex, InterfaceAlias, IPAddress, PrefixLength, AddressState, Type, PolicyStore
foreach ($o in @($before)) {{
  try {{
    Remove-NetIPAddress -InterfaceIndex $o.InterfaceIndex -IPAddress $o.IPAddress -Confirm:$false -ErrorAction SilentlyContinue
  }} catch {{}}
}}
$after = Get-NetIPAddress -AddressFamily IPv4 -IPAddress "{ip}" -ErrorAction SilentlyContinue |
  Where-Object {{ $_.InterfaceIndex -ne $target }} |
  Select-Object InterfaceIndex, InterfaceAlias, IPAddress, PrefixLength, AddressState, Type, PolicyStore
@{{ before = $before; after = $after }} | ConvertTo-Json -Depth 6
"""
    try:
        data = ps_json(script) or {}
    except IpGsError as exc:
        raise IpGsError(f"failed to remove conflicting ip: {ip} ({exc})") from exc

    after = normalize_ps_list(data.get("after"))
    remaining = [
        o
        for o in after
        if isinstance(o, dict)
        and o.get("IPAddress")
        and o.get("InterfaceIndex") is not None
        and int(o.get("InterfaceIndex")) != int(target_if_index)
    ]
    if remaining:
        logger.error("ip %s still owned by other interfaces: %s", ip, remaining)
        raise IpGsError(f"failed to remove conflicting ip: {ip}")


def _find_ifindex_by_profile(profile: dict[str, Any]) -> int:
    mac = profile.get("mac_address")
    alias = profile.get("interface_alias")
    desc = profile.get("interface_description")

    if mac:
        mac = format_mac(str(mac))
        where = f'$_.MacAddress -eq "{mac}"'
    elif alias:
        where = f'$_.Name -eq "{alias}"'
    elif desc:
        where = f'$_.InterfaceDescription -eq "{desc}"'
    else:
        raise IpGsError("profile must include one of: mac_address/interface_alias/interface_description")
    script = rf"""
$ErrorActionPreference = "Stop"
$ad = Get-NetAdapter -IncludeHidden | Where-Object {{ {where} }} | Select-Object -First 1
if (-not $ad) {{ exit 2 }}
$ad.ifIndex
"""
    res = run_powershell(script)
    if res.returncode == 2:
        raise AdapterNotFoundError(f"adapter not found for profile: {profile.get('name')}")
    if res.returncode != 0:
        log_ps_failure("find adapter", res)
        raise IpGsError("failed to locate adapter")
    try:
        return int(res.stdout.strip())
    except ValueError as exc:
        raise IpGsError(f"invalid ifIndex output: {res.stdout}") from exc


def set_dhcp(if_index: int, dry_run: bool) -> None:
    script = rf"""
$ErrorActionPreference = "Stop"
$if = {if_index}
Get-NetIPAddress -InterfaceIndex $if -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Where-Object {{ $_.IPAddress -ne "127.0.0.1" }} |
  Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
Set-NetIPInterface -InterfaceIndex $if -Dhcp Enabled
Set-DnsClientServerAddress -InterfaceIndex $if -ResetServerAddresses
"""
    if dry_run:
        logger.info("[dry-run] set dhcp on ifIndex=%s", if_index)
        return
    res = run_powershell(script)
    if res.returncode != 0:
        log_ps_failure("set dhcp", res)
        raise IpGsError("failed to set dhcp")


def set_static_ipv4(
    if_index: int,
    address: str,
    prefix_length: int,
    gateway: str | None,
    dns_servers: list[str] | None,
    dry_run: bool,
) -> None:
    gw = gateway or ""
    dns = dns_servers or []
    dns_ps = "@(" + ",".join([f'"{d}"' for d in dns]) + ")"
    gw_part = f'-DefaultGateway "{gw}"' if gw else ""
    script = rf"""
$ErrorActionPreference = "Stop"
$if = {if_index}
Set-NetIPInterface -InterfaceIndex $if -Dhcp Disabled
Get-NetIPAddress -InterfaceIndex $if -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Where-Object {{ $_.IPAddress -ne "127.0.0.1" }} |
  Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
New-NetIPAddress -InterfaceIndex $if -IPAddress "{address}" -PrefixLength {int(prefix_length)} {gw_part}
if ({dns_ps}.Count -gt 0) {{
  Set-DnsClientServerAddress -InterfaceIndex $if -ServerAddresses {dns_ps}
}}
"""
    if dry_run:
        logger.info(
            "[dry-run] set static ifIndex=%s ip=%s/%s gw=%s dns=%s",
            if_index,
            address,
            prefix_length,
            gateway,
            dns_servers,
        )
        return
    res = run_powershell(script)
    if res.returncode != 0:
        log_ps_failure("set static", res)
        raise IpGsError("failed to set static ip")


def apply_profile(profile: dict[str, Any], dry_run: bool) -> None:
    if_index = _find_ifindex_by_profile(profile)
    state = get_ipv4_state(if_index)
    if is_profile_already_applied(profile, state):
        logger.info("skip profile=%s (already applied) ifIndex=%s", profile.get("name"), if_index)
        return
    dhcp = bool(profile.get("dhcp"))
    logger.info("apply profile=%s ifIndex=%s dhcp=%s", profile.get("name"), if_index, dhcp)

    if dhcp:
        set_dhcp(if_index, dry_run=dry_run)
        return

    ipv4 = profile.get("ipv4") or {}
    address = ipv4.get("address")
    prefix_length = ipv4.get("prefix_length")
    gateway = ipv4.get("gateway")
    dns_servers = profile.get("dns_servers") or []
    logger.info("desired profile=%s ip=%s/%s", profile.get("name"), address, prefix_length)

    if not address or prefix_length is None:
        raise IpGsError(f"profile {profile.get('name')} missing ipv4.address/prefix_length")

    remove_conflicting_ip(str(address), target_if_index=if_index, dry_run=dry_run)

    set_static_ipv4(
        if_index=if_index,
        address=str(address),
        prefix_length=int(prefix_length),
        gateway=(str(gateway) if gateway else None),
        dns_servers=[str(x) for x in dns_servers],
        dry_run=dry_run,
    )


def main() -> int:
    ensure_file_logging()
    parser = argparse.ArgumentParser(description="Apply Windows NIC IP settings from json (PowerShell NetTCPIP).")
    parser.add_argument("--config", type=Path, default=DEFAULT_SETTINGS_PATH, help="Settings json path.")
    parser.add_argument("--profile", help="Apply a single profile by name (default: all).")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without applying changes.")
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=60,
        help="Wait up to N seconds for the adapter to appear after boot (default: 60).",
    )
    parser.add_argument(
        "--wait-interval",
        type=float,
        default=2.0,
        help="Retry interval seconds while waiting for adapter (default: 2).",
    )
    args = parser.parse_args()

    settings = load_settings(args.config)
    logger.info("using config: %s", args.config.resolve())
    profiles = list(iter_profiles(settings, args.profile))
    if not profiles:
        raise IpGsError("no profiles found")

    if not args.dry_run:
        require_admin()

    for profile in profiles:
        deadline = time.time() + max(0, int(args.wait_seconds))
        while True:
            try:
                apply_profile(profile, dry_run=args.dry_run)
                break
            except AdapterNotFoundError:
                if time.time() >= deadline:
                    raise
                time.sleep(max(0.2, float(args.wait_interval)))

    return 0


if __name__ == "__main__":
    log_path = ensure_file_logging()
    try:
        raise SystemExit(main())
    except IpGsError as exc:
        logger.error("ip_set failed: %s", exc)
        try:
            log_path.write_text(f"ip_set failed: {exc}\n", encoding="utf-8", errors="replace")
        except Exception:
            pass
        raise SystemExit(1)
    except Exception as exc:
        logger.exception("ip_set unexpected error: %s", exc)
        try:
            with log_path.open("a", encoding="utf-8", errors="replace") as f:
                f.write(f"ip_set unexpected error: {exc}\n")
        except Exception:
            pass
        raise SystemExit(1)
