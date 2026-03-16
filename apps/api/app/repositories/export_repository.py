from __future__ import annotations

from threading import Lock

from app.schemas.exports import ExportFileRecord


class ExportRepository:
    def __init__(self) -> None:
        self._records: dict[str, ExportFileRecord] = {}
        self._lock = Lock()

    def save(self, export_file: ExportFileRecord) -> ExportFileRecord:
        with self._lock:
            self._records[export_file.id] = export_file
        return export_file

    def get(self, export_id: str) -> ExportFileRecord | None:
        record = self._records.get(export_id)
        return record.model_copy(deep=True) if record else None


export_repository = ExportRepository()
