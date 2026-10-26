from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ai.llm_client import LLMClient
from core.validator import Validator


class Planner:
    def __init__(self):
        self.llm = LLMClient()

    def generate(self, prompt: str) -> Dict[str, Any]:
        payload = self.llm.generate_plan(prompt)
        script = payload.get("batch_script") or ""
        manifest = payload.get("manifest") or {}

        batch_result = Validator.validate_batch_script(script)
        manifest_result = Validator.validate_manifest(manifest)
        if not batch_result.is_valid or not manifest_result.is_valid:
            errors = batch_result.errors + manifest_result.errors
            if (
                "No valid winget install command was found." in batch_result.errors
                or any("No applications were identified." in error for error in errors)
            ):
                errors.append(
                    "Try a prompt focused on installation, such as "
                    "'Install MySQL Server using its exact Winget package ID.' "
                    "Do not include account passwords; database credential setup is unsupported."
                )
            raise ValueError(
                "Generated script or manifest failed validation: "
                + "; ".join(errors)
            )

        return {"batch_script": script, "manifest": manifest_result.normalized_manifest}

    def save_run(self, run_dir: Path, batch_script: str, manifest: Dict[str, Any]) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "install.bat").write_text(batch_script, encoding="utf-8")
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
