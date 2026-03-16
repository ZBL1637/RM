from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

TaskStatus = Literal["created", "uploaded", "validating", "validated", "analyzing", "success", "failed", "canceled"]


class AnalysisTaskRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str | None = None
    method_id: str
    method_slug: str
    upload_id: str
    status: TaskStatus
    validation_passed: bool | None = None
    started_at: str | None = None
    finished_at: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: str


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method_slug: str
    upload_id: str


class CreateTaskResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    status: TaskStatus


class AnalyzeTaskResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    status: TaskStatus
