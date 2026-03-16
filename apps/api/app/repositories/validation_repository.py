from __future__ import annotations

from threading import Lock

from app.schemas.validation import ValidationReportRecord


class ValidationRepository:
    def __init__(self) -> None:
        self._records: dict[str, ValidationReportRecord] = {}
        self._lock = Lock()

    def save(self, report: ValidationReportRecord) -> ValidationReportRecord:
        with self._lock:
            self._records[report.task_id] = report
        return report

    def get_by_task_id(self, task_id: str) -> ValidationReportRecord | None:
        report = self._records.get(task_id)
        return report.model_copy(deep=True) if report else None


validation_repository = ValidationRepository()
