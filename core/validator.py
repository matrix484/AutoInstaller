from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from core.models import ValidationResult


VALID_COMMAND_RE = re.compile(r"^winget install --id [A-Za-z0-9.-]+ --exact --silent --accept-package-agreements --accept-source-agreements$")
SAFE_ERRORLEVEL_RE = re.compile(
    r"^if (?:errorlevel 1 exit /b 1|%errorlevel% neq 0 exit /b %errorlevel%)$",
    re.IGNORECASE,
)
SAFE_PATH_RE = re.compile(r"^[A-Za-z]:\\(?:[^\\/:*?\"<>|]+\\)*[^\\/:*?\"<>|]*$")


class Validator:
    @staticmethod
    def validate_manifest(manifest: Dict[str, Any]) -> ValidationResult:
        errors: List[str] = []
        warnings: List[str] = []

        if not isinstance(manifest, dict):
            return ValidationResult(False, ["Manifest must be a JSON object."], [], None)

        apps = manifest.get("applications")
        if not isinstance(apps, list):
            errors.append("Manifest must include an 'applications' list.")
        elif not apps:
            errors.append(
                "No applications were identified. Provide the software name clearly; "
                "database account and password configuration is not supported."
            )

        if apps:
            for index, app in enumerate(apps):
                if not isinstance(app, dict):
                    errors.append(f"Application entry {index} must be an object.")
                    continue
                package_id = app.get("package_id")
                if not isinstance(package_id, str):
                    errors.append(f"Application {index} is missing a valid package_id.")
                elif not re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+", package_id):
                    errors.append(f"Application {index} has an invalid package_id: {package_id}")

        config = manifest.get("configuration", {})
        if config is None:
            config = {}
        if not isinstance(config, dict):
            errors.append("Configuration must be an object when present.")
        else:
            for key, value in config.items():
                if key in {"git_user_name", "git_user_email"} and value is not None and not isinstance(value, str):
                    errors.append(f"Configuration '{key}' must be a string or null.")
                if key == "directory" and value is not None:
                    if not isinstance(value, str) or not SAFE_PATH_RE.match(value):
                        errors.append(f"Configuration directory '{value}' is not a safe Windows path.")

        if not errors:
            return ValidationResult(True, [], warnings, manifest)
        return ValidationResult(False, errors, warnings, None)

    @staticmethod
    def validate_batch_script(script_text: str) -> ValidationResult:
        if not isinstance(script_text, str) or not script_text.strip():
            return ValidationResult(False, ["Batch script is empty."], [], None)

        if "powershell" in script_text.lower() or "cmd /c" in script_text.lower():
            return ValidationResult(False, ["PowerShell or command-shell execution is not allowed."], [], None)
        if "|" in script_text or ">" in script_text or "<" in script_text:
            return ValidationResult(False, ["Pipes and redirection are not allowed in the batch script."], [], None)
        if "reg add" in script_text.lower() or "setx" in script_text.lower() or "del /s" in script_text.lower():
            return ValidationResult(False, ["Unsafe system changes are blocked."], [], None)

        lines = [line.strip() for line in script_text.splitlines() if line.strip()]
        has_winget = False
        for line in lines:
            if line.lower().startswith("@echo off") or line.lower().startswith("echo ") or line.lower().startswith("title "):
                continue
            if line.lower().startswith("winget install"):
                if not VALID_COMMAND_RE.fullmatch(line.strip()):
                    return ValidationResult(False, [f"Unsupported winget command pattern: {line}"], [], None)
                has_winget = True
                continue
            if line.lower().startswith("git config"):
                continue
            if line.lower().startswith("mkdir "):
                continue
            if SAFE_ERRORLEVEL_RE.fullmatch(line):
                continue
            if line.lower().startswith("echo [") or line.lower().startswith("echo."):
                continue
            return ValidationResult(False, [f"Unsupported command detected: {line}"], [], None)

        if not has_winget:
            return ValidationResult(False, ["No valid winget install command was found."], [], None)

        return ValidationResult(True, [], [], script_text)
