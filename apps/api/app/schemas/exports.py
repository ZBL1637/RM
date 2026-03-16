from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

ExportType = Literal["pdf", "docx", "md"]


class ExportFileRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    task_id: str
    export_type: ExportType
    storage_path: str
    created_at: str


class CreateExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_type: ExportType


class CreateExportResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_id: str
    download_url: str
