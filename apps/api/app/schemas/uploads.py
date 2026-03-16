from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UploadRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str | None = None
    file_name: str
    storage_path: str
    file_type: str
    mime_type: str | None = None
    file_size: int
    checksum: str | None = None
    uploaded_at: str


class UploadResponseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    upload_id: str
    file_name: str
    file_size: int
    file_type: str
    mime_type: str | None = None
    uploaded_at: str
