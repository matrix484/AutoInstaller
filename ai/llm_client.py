from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

from app_paths import get_app_dir
from ai.prompts import SYSTEM_PROMPT

load_dotenv(get_app_dir() / ".env")


class LLMClient:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        configured_gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
        if configured_gemini_model == "gemini-2.5-flash":
            configured_gemini_model = "gemini-3.8-flash"
        self.gemini_model = configured_gemini_model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        default_provider = "openai" if self.api_key and not self.gemini_api_key else "gemini"
        self.provider = os.getenv("LLM_PROVIDER", default_provider).strip().lower()

    def is_configured(self) -> bool:
        if self.provider == "gemini":
            return bool(self.gemini_api_key)
        if self.provider == "openai":
            return bool(self.api_key)
        return False

    def generate_plan(self, prompt: str) -> dict[str, Any]:
        if self.provider not in {"gemini", "openai"}:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider}")
        if not self.is_configured():
            return self._fallback_plan(prompt)

        try:
            from openai import OpenAI

            if self.provider == "gemini":
                client = OpenAI(
                    api_key=self.gemini_api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    timeout=60.0,
                    max_retries=5,
                )
                model = self.gemini_model
            else:
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url or None,
                    timeout=60.0,
                    max_retries=2,
                )
                model = self.model

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("The model returned an empty response.")
            payload = json.loads(content)
            if not isinstance(payload, dict):
                raise ValueError("Response is not a JSON object.")
            return payload
        except Exception as exc:
            raise RuntimeError(self._format_provider_error(exc)) from exc

    def _format_provider_error(self, exc: Exception) -> str:
        status_code = getattr(exc, "status_code", None)
        detail = str(exc).strip()
        for api_key in (self.gemini_api_key, self.api_key):
            if api_key:
                detail = detail.replace(api_key, "[REDACTED]")
        detail = detail[:500]

        if status_code == 401:
            reason = "HTTP 401: the API key was rejected. Check or replace the key."
        elif status_code == 403:
            reason = "HTTP 403: the API key does not have access to this API or model."
        elif status_code == 404:
            reason = "HTTP 404: the requested model or API endpoint was not found."
        elif status_code == 429:
            reason = "HTTP 429: the provider quota or rate limit was reached."
        elif status_code == 503:
            reason = (
                "HTTP 503: Gemini is temporarily overloaded. The request was retried; "
                "wait briefly and try again."
            )
        elif status_code is not None:
            reason = f"The provider returned HTTP {status_code}."
        else:
            reason = f"The request failed ({type(exc).__name__})."

        message = f"{self.provider.capitalize()} error: {reason}"
        if detail and status_code != 503:
            message += f" Details: {detail}"
        return message

    def _fallback_plan(self, prompt: str) -> dict[str, Any]:
        package_id_map = (
            ("git", "Git.Git"),
            ("visual studio code", "Microsoft.VisualStudioCode"),
            ("vscode", "Microsoft.VisualStudioCode"),
            ("code", "Microsoft.VisualStudioCode"),
            ("python", "Python.Python.3.12"),
            ("firefox", "Mozilla.Firefox"),
            ("mozilla firefox", "Mozilla.Firefox"),
            ("krita", "Krita.Krita"),
            ("inkscape", "Inkscape.Inkscape"),
            ("7zip", "7zip.7zip"),
            ("7-zip", "7zip.7zip"),
            ("vlc", "VideoLAN.VLC"),
            ("notepad++", "Notepad++.Notepad++"),
            ("notepad plus plus", "Notepad++.Notepad++"),
            ("google chrome", "Google.Chrome"),
            ("chrome", "Google.Chrome"),
            ("discord", "Discord.Discord"),
            ("gimp", "GIMP.GIMP"),
            ("blender", "BlenderFoundation.Blender"),
            ("docker desktop", "Docker.DockerDesktop"),
            ("nodejs", "OpenJS.NodeJS.LTS"),
            ("node.js", "OpenJS.NodeJS.LTS"),
            ("node", "OpenJS.NodeJS.LTS"),
            ("obs studio", "OBSProject.OBSStudio"),
            ("obs", "OBSProject.OBSStudio"),
            ("postman", "Postman.Postman"),
            ("slack", "SlackTechnologies.Slack"),
            ("steam", "Valve.Steam"),
            ("telegram", "Telegram.TelegramDesktop"),
            ("zoom", "Zoom.Zoom"),
            ("winrar", "RARLab.WinRAR"),
        )

        lowered = prompt.lower()
        package_ids = []
        seen = set()
        for keyword, package_id in package_id_map:
            if keyword in lowered and package_id not in seen:
                package_ids.append(package_id)
                seen.add(package_id)

        lines = ["@echo off", "title Auto Installer", "echo Starting installation..."]
        for index, package_id in enumerate(package_ids, start=1):
            lines.append(f"echo Installing package {index}: {package_id}")
            lines.append(f"winget install --id {package_id} --exact --silent --accept-package-agreements --accept-source-agreements")
        lines.append("if %errorlevel% neq 0 exit /b %errorlevel%")
        lines.append("echo Installation completed.")

        manifest = {
            "applications": [{"name": package_id.split(".")[-1], "package_id": package_id} for package_id in package_ids],
            "configuration": {},
            "verification": [{"name": package_id, "check": "winget package is installed"} for package_id in package_ids],
        }
        return {"batch_script": "\n".join(lines), "manifest": manifest}
