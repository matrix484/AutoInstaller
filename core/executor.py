from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from package_managers.winget import install_package


class Executor:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.activity: List[str] = []

    def run_batch_script(self, script_path: Path) -> int:
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=600,
            shell=True,
            check=False,
        )
        self.activity.append(result.stdout)
        self.activity.append(result.stderr)
        return result.returncode

    def install_applications(self, manifest: dict) -> List[str]:
        installed: List[str] = []
        for app in manifest.get("applications", []):
            package_id = app.get("package_id")
            if not package_id:
                continue
            proc = install_package(package_id)
            if proc.returncode == 0:
                installed.append(package_id)
        return installed
