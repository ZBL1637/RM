from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiSuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T


class ApiErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: dict[str, Any] = Field(default_factory=dict)
