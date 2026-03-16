from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import ServiceError
from app.repositories.upload_repository import upload_repository
from app.schemas.uploads import UploadRecord, UploadResponseData

SAFE_FILE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


class UploadService:
    async def create_upload(self, file: UploadFile) -> UploadResponseData:
        file_name = file.filename or ""
        file_type = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

        if file_type not in {"csv", "xlsx"}:
            raise ServiceError(
                status_code=400,
                message="仅支持上传 .csv 或 .xlsx 文件。",
                error_code="INVALID_FILE_TYPE",
                details={"file_name": file_name},
            )

        content = await file.read()
        if not content:
            raise ServiceError(
                status_code=400,
                message="上传文件为空，请选择包含数据的文件。",
                error_code="FILE_PARSE_FAILED",
                details={"file_name": file_name},
            )

        max_size = settings.max_csv_size_bytes if file_type == "csv" else settings.max_xlsx_size_bytes
        if len(content) > max_size:
            raise ServiceError(
                status_code=400,
                message="上传文件超过当前大小限制，请压缩后重试。",
                error_code="FILE_TOO_LARGE",
                details={"file_name": file_name, "file_size": len(content), "max_size": max_size},
            )

        upload_id = f"upl_{uuid4().hex[:12]}"
        uploaded_at = _utc_now()
        storage_path = self._build_storage_path(upload_id, file_name, file_type, uploaded_at)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(content)

        record = UploadRecord(
            id=upload_id,
            file_name=file_name,
            storage_path=str(storage_path),
            file_type=file_type,
            mime_type=file.content_type,
            file_size=len(content),
            checksum=hashlib.sha256(content).hexdigest(),
            uploaded_at=uploaded_at,
        )
        upload_repository.save(record)

        return UploadResponseData(
            upload_id=record.id,
            file_name=record.file_name,
            file_size=record.file_size,
            file_type=record.file_type,
            mime_type=record.mime_type,
            uploaded_at=record.uploaded_at,
        )

    @staticmethod
    def _build_storage_path(upload_id: str, file_name: str, file_type: str, uploaded_at: str) -> Path:
        safe_name = SAFE_FILE_NAME_PATTERN.sub("_", Path(file_name).stem).strip("._") or "upload"
        timestamp = datetime.fromisoformat(uploaded_at.replace("Z", "+00:00"))
        return (
            settings.storage_root
            / "uploads"
            / f"{timestamp.year:04d}"
            / f"{timestamp.month:02d}"
            / f"{upload_id}_{safe_name}.{file_type}"
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


upload_service = UploadService()
