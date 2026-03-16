from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ServiceError(Exception):
    status_code: int
    message: str
    error_code: str
    details: dict[str, Any] = field(default_factory=dict)
