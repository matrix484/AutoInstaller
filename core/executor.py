from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, List, Optional

from package_managers.winget import install_package


class Executor:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.activity: List[str] = []

    def run_batch_script(
        self,
        script_path: Path,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> int:
        process = subprocess.Popen(
            ["cmd.exe", "/c", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=False,
        )

        output_lines: List[str] = []
        if process.stdout is not None:
            for line in iter(process.stdout.readline, ""):
                text = line.rstrip("\r\n")
                if not text:
                    continue
                output_lines.append(text)
                if stream_callback is not None:
                    stream_callback(text)

        process.stdout.close() if process.stdout is not None else None
        return_code = process.wait(timeout=600)
        self.activity.extend(output_lines)
        return return_code

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
