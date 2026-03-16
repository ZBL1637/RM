from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    level: Literal["error", "warning", "info"]
    field: str
    message: str
    suggestion: str


class ValidationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_count: int
    warning_count: int


class ValidationStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row_count: int
    column_count: int
    missing_ratio: float
    numeric_column_count: int = 0
    categorical_column_count: int = 0


class ValidationReportPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passed: bool
    summary: ValidationSummary
    errors: list[ValidationIssue]
    warnings: list[ValidationIssue]
    stats: ValidationStats


class ValidationReportRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    task_id: str
    passed: bool
    error_count: int
    warning_count: int
    report_json: ValidationReportPayload
    created_at: str


class ValidateTaskResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    status: str
    validation_passed: bool
    validation: ValidationReportPayload
