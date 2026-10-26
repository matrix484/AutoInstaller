from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List


class Configurator:
    def configure(self, manifest: Dict[str, Any]) -> List[str]:
        completed: List[str] = []
        config = manifest.get("configuration", {})
        if not isinstance(config, dict):
            return completed

        git_user_name = config.get("git_user_name")
        git_user_email = config.get("git_user_email")
        if git_user_name:
            subprocess.run(["git", "config", "--global", "user.name", git_user_name], check=False, capture_output=True, text=True)
            completed.append("git user.name")
        if git_user_email:
            subprocess.run(["git", "config", "--global", "user.email", git_user_email], check=False, capture_output=True, text=True)
            completed.append("git user.email")

        directories = config.get("directories", [])
        if isinstance(directories, list):
            for directory in directories:
                safe = self._safe_directory(directory)
                if safe:
                    Path(safe).mkdir(parents=True, exist_ok=True)
                    completed.append(f"directory:{safe}")

        files = config.get("files", [])
        if isinstance(files, list):
            for entry in files:
                if not isinstance(entry, dict):
                    continue
                path = entry.get("path")
                content = entry.get("content", "")
                if not path or not isinstance(content, str):
                    continue
                safe = self._safe_path(path)
                if safe:
                    file_path = Path(safe)
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding="utf-8")
                    completed.append(f"file:{safe}")

        return completed

    def _safe_directory(self, path: str) -> str | None:
        if not isinstance(path, str):
            return None
        if not path or path.startswith("\\\\") or path.startswith("\\"):
            return None
        if ":" not in path:
            return None
        if any(token in path.lower() for token in ["program files", "windows", "system32"]):
            return None
        return path

    def _safe_path(self, path: str) -> str | None:
        return self._safe_directory(path)
