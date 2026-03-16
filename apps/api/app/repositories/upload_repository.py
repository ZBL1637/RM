from __future__ import annotations

from threading import Lock

from app.schemas.uploads import UploadRecord


class UploadRepository:
    def __init__(self) -> None:
        self._records: dict[str, UploadRecord] = {}
        self._lock = Lock()

    def save(self, upload: UploadRecord) -> UploadRecord:
        with self._lock:
            self._records[upload.id] = upload
        return upload

    def get(self, upload_id: str) -> UploadRecord | None:
        upload = self._records.get(upload_id)
        return upload.model_copy(deep=True) if upload else None


upload_repository = UploadRepository()
