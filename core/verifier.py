from __future__ import annotations

import shutil
import subprocess
from typing import Any, Dict, List


class Verifier:
    def verify(self, manifest: Dict[str, Any]) -> Dict[str, List[str]]:
        installed: List[str] = []
        failed: List[str] = []

        for app in manifest.get("applications", []):
            package_id = app.get("package_id")
            if not package_id:
                continue
            check = shutil.which(package_id.split(".")[-1])
            if check:
                installed.append(package_id)
            else:
                failed.append(package_id)

        config = manifest.get("configuration", {})
        configured: List[str] = []
        if isinstance(config, dict):
            git_user_name = config.get("git_user_name")
            git_user_email = config.get("git_user_email")
            if git_user_name:
                result = subprocess.run(["git", "config", "--global", "user.name"], capture_output=True, text=True, check=False)
                if result.stdout.strip() == git_user_name:
                    configured.append("git user.name")
            if git_user_email:
                result = subprocess.run(["git", "config", "--global", "user.email"], capture_output=True, text=True, check=False)
                if result.stdout.strip() == git_user_email:
                    configured.append("git user.email")

        return {"installed": installed, "failed": failed, "configured": configured}
