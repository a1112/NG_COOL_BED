from __future__ import annotations

import sys
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from Loger import logger


IP_GS_DIR = Path(__file__).resolve().parent
DEFAULT_SETTINGS_PATH = IP_GS_DIR / "ip_settings.json"


@dataclass(frozen=True)
class PowerShellResult:
    stdout: str
    stderr: str
    returncode: int


class IpGsError(RuntimeError):
    pass


def _ensure_windows() -> None:
    if os.name != "nt":
        raise IpGsError("ip_gs only supports Windows (requires PowerShell NetTCPIP cmdlets).")


def run_powershell(script: str) -> PowerShellResult:
    _ensure_windows()
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return PowerShellResult(
        stdout=(completed.stdout or "").strip(),
        stderr=(completed.stderr or "").strip(),
        returncode=completed.returncode,
    )


def require_admin() -> None:
    script = "[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) | ConvertTo-Json"
    res = run_powershell(script)
    if res.returncode != 0:
        raise IpGsError(f"failed to check admin privilege: {res.stderr or res.stdout}")
    try:
        is_admin = bool(json.loads(res.stdout))
    except json.JSONDecodeError as exc:
        raise IpGsError(f"failed to parse admin check output: {res.stdout}") from exc
    if not is_admin:
        raise IpGsError("administrator privilege required (run as admin or via scheduled task as SYSTEM).")


def ps_json(script: str) -> Any:
    res = run_powershell(script)
    if res.returncode != 0:
        raise IpGsError(res.stderr or res.stdout or "powershell failed")
    if not res.stdout:
        return None
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise IpGsError(f"failed to parse PowerShell JSON output: {res.stdout}") from exc


def normalize_ps_list(obj: Any) -> list[Any]:
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    return [obj]


def load_settings(path: Path | None = None) -> dict[str, Any]:
    settings_path = path or DEFAULT_SETTINGS_PATH
    if not settings_path.exists():
        raise IpGsError(f"settings json not found: {settings_path}")
    try:
        return json.loads(settings_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IpGsError(f"invalid json: {settings_path}") from exc


def iter_profiles(settings: dict[str, Any], profile_name: str | None) -> Iterable[dict[str, Any]]:
    profiles = settings.get("profiles") or []
    if not isinstance(profiles, list):
        raise IpGsError("settings.profiles must be a list")
    if profile_name is None:
        return profiles
    for profile in profiles:
        if profile.get("name") == profile_name:
            return [profile]
    raise IpGsError(f"profile not found: {profile_name}")


def format_mac(mac: str) -> str:
    mac = mac.strip().upper().replace(":", "-")
    return mac


def log_ps_failure(context: str, res: PowerShellResult) -> None:
    if res.stdout:
        logger.error("%s stdout: %s", context, res.stdout)
    if res.stderr:
        logger.error("%s stderr: %s", context, res.stderr)
