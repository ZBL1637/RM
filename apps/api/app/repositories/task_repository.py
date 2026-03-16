from __future__ import annotations

from threading import Lock

from app.schemas.tasks import AnalysisTaskRecord


class TaskRepository:
    def __init__(self) -> None:
        self._records: dict[str, AnalysisTaskRecord] = {}
        self._lock = Lock()

    def save(self, task: AnalysisTaskRecord) -> AnalysisTaskRecord:
        with self._lock:
            self._records[task.id] = task
        return task

    def get(self, task_id: str) -> AnalysisTaskRecord | None:
        task = self._records.get(task_id)
        return task.model_copy(deep=True) if task else None

    def update(self, task: AnalysisTaskRecord) -> AnalysisTaskRecord:
        return self.save(task)


task_repository = TaskRepository()
