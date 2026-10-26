from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AppRequest:
    prompt: str
    package_ids: List[str] = field(default_factory=list)
    git_user_name: Optional[str] = None
    git_user_email: Optional[str] = None
    config_actions: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    normalized_manifest: Optional[Dict[str, Any]] = None


@dataclass
class RunResult:
    run_id: str
    status: str
    summary: str
    output_dir: str
    installed: List[str] = field(default_factory=list)
    configured: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
