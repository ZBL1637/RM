from __future__ import annotations

from threading import Lock

from app.schemas.results import AnalysisResultRecord


class AnalysisResultRepository:
    def __init__(self) -> None:
        self._records: dict[str, AnalysisResultRecord] = {}
        self._lock = Lock()

    def save(self, record: AnalysisResultRecord) -> AnalysisResultRecord:
        with self._lock:
            self._records[record.task_id] = record
        return record

    def get_by_task_id(self, task_id: str) -> AnalysisResultRecord | None:
        record = self._records.get(task_id)
        return record.model_copy(deep=True) if record else None


analysis_result_repository = AnalysisResultRepository()
