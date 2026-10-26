from __future__ import annotations

import os
import subprocess
from pathlib import Path


def is_winget_available() -> bool:
    try:
        result = subprocess.run(
            ["winget", "--version"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def build_winget_install_command(package_id: str) -> str:
    return (
        f'winget install --id {package_id} --exact --silent '
        '--accept-package-agreements --accept-source-agreements'
    )


def install_package(package_id: str, log_path: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    command = build_winget_install_command(package_id)
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
