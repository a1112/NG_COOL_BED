from __future__ import annotations

import sys
import argparse
import json
from pathlib import Path
from typing import Any

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from Loger import logger

from ip_gs.common import DEFAULT_SETTINGS_PATH, IpGsError, normalize_ps_list, ps_json


def get_adapters() -> list[dict[str, Any]]:
    script = r"""
$ErrorActionPreference = "Stop"
Get-NetAdapter |
  Select-Object Name, InterfaceDescription, MacAddress, ifIndex, Status, LinkSpeed |
  ConvertTo-Json -Depth 4
"""
    return normalize_ps_list(ps_json(script))


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
@{{ ip = $ip; gateway = $gw; dns_servers = $dns }} | ConvertTo-Json -Depth 6
"""
    data = ps_json(script) or {}
    data["ip"] = [x for x in normalize_ps_list(data.get("ip")) if isinstance(x, dict)]
    data["dns_servers"] = [x for x in normalize_ps_list(data.get("dns_servers")) if isinstance(x, str) and x]
    return data


def get_interface_dhcp(if_index: int) -> bool | None:
    script = rf"""
$ErrorActionPreference = "Stop"
$if = {if_index}
$v = (Get-NetIPInterface -InterfaceIndex $if -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -First 1 Dhcp | ConvertTo-Json -Depth 4)
$v
"""
    data = ps_json(script)
    if not data:
        return None
    raw = data.get("Dhcp")
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int):
        if raw == 1:
            return True
        if raw == 0:
            return False
        return None
    dhcp_val = str(raw or "").strip().lower()
    if dhcp_val in {"enabled", "enable", "true", "1"}:
        return True
    if dhcp_val in {"disabled", "disable", "false", "0"}:
        return False
    return None


def export_profile(adapter: dict[str, Any]) -> dict[str, Any]:
    if_index = int(adapter["ifIndex"])
    ipv4_state = get_ipv4_state(if_index)
    dhcp = get_interface_dhcp(if_index)

    ip_items = ipv4_state.get("ip") or []
    first_ip = ip_items[0] if ip_items else {}
    gateway = (ipv4_state.get("gateway") or {}).get("NextHop") if isinstance(ipv4_state.get("gateway"), dict) else None
    dns_servers = ipv4_state.get("dns_servers") or []

    profile: dict[str, Any] = {
        "name": adapter.get("Name") or "default",
        "mac_address": adapter.get("MacAddress") or "",
        "interface_alias": adapter.get("Name") or "",
        "interface_description": adapter.get("InterfaceDescription") or "",
        "dhcp": bool(dhcp) if dhcp is not None else False,
        "ipv4": {
            "address": first_ip.get("IPAddress") or "",
            "prefix_length": first_ip.get("PrefixLength") or 24,
            "gateway": gateway or "",
        },
        "dns_servers": dns_servers,
    }
    return {"version": 1, "profiles": [profile]}


def export_non_dhcp_profiles(adapters: list[dict[str, Any]]) -> dict[str, Any]:
    profiles: list[dict[str, Any]] = []
    for adapter in adapters:
        try:
            if_index = int(adapter["ifIndex"])
        except Exception:
            continue

        dhcp = get_interface_dhcp(if_index)
        if dhcp is not False:
            continue

        exported = export_profile(adapter)
        profile = (exported.get("profiles") or [{}])[0]
        profiles.append(profile)

    return {"version": 1, "profiles": profiles}


def main() -> int:
    parser = argparse.ArgumentParser(description="Get Windows NIC info (by PowerShell NetTCPIP cmdlets).")
    parser.add_argument("--mac", help="Filter by MAC address (AA-BB-CC-DD-EE-FF).")
    parser.add_argument("--details", action="store_true", help="Also query IPv4/gateway/DNS for each adapter.")
    parser.add_argument("--export-profile", metavar="NAME", help="Export one adapter (requires --mac) to settings json schema.")
    parser.add_argument(
        "--export-non-dhcp",
        action="store_true",
        help="Export all non-DHCP adapters to settings json schema (best-effort).",
    )
    parser.add_argument("--out", type=Path, default=None, help="Write output json to file.")
    args = parser.parse_args()

    adapters = get_adapters()
    if args.mac:
        mac = args.mac.strip().upper().replace(":", "-")
        adapters = [a for a in adapters if (a.get("MacAddress") or "").upper() == mac]

    if args.export_profile:
        if not args.mac:
            raise IpGsError("--export-profile requires --mac")
        if not adapters:
            raise IpGsError(f"adapter not found for mac: {args.mac}")
        adapter = adapters[0]
        if args.export_profile:
            adapter = dict(adapter)
            adapter["Name"] = args.export_profile
        payload: dict[str, Any] = export_profile(adapter)
    elif args.export_non_dhcp:
        payload = export_non_dhcp_profiles(adapters)
    else:
        payload = {"adapters": adapters}

    if args.details and not args.export_profile:
        for ad in adapters:
            try:
                if_index = int(ad["ifIndex"])
            except Exception:
                continue
            ad["ipv4_state"] = get_ipv4_state(if_index)

    text = json.dumps(payload, ensure_ascii=True, indent=2)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(text)

    if args.out:
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("wrote: %s", args.out)
    elif args.export_non_dhcp:
        DEFAULT_SETTINGS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("wrote: %s", DEFAULT_SETTINGS_PATH)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IpGsError as exc:
        logger.error("ip_get failed: %s", exc)
        raise SystemExit(1)
