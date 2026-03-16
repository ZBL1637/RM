from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.errors import ServiceError
from app.repositories.task_repository import task_repository
from app.repositories.upload_repository import upload_repository
from app.schemas.tasks import AnalysisTaskRecord, CreateTaskResponseData
from app.services.method_service import method_service


class TaskService:
    def create_task(self, method_slug: str, upload_id: str) -> CreateTaskResponseData:
        method = method_service.get_method_by_slug(method_slug)
        if method is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应的研究方法。",
                error_code="METHOD_NOT_FOUND",
                details={"method_slug": method_slug},
            )

        upload = upload_repository.get(upload_id)
        if upload is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应的上传文件，请重新上传后再创建任务。",
                error_code="UPLOAD_NOT_FOUND",
                details={"upload_id": upload_id},
            )

        task = AnalysisTaskRecord(
            id=f"task_{uuid4().hex[:12]}",
            method_id=method.id,
            method_slug=method.slug,
            upload_id=upload.id,
            status="created",
            created_at=_utc_now(),
        )
        task_repository.save(task)

        return CreateTaskResponseData(task_id=task.id, status=task.status)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


task_service = TaskService()
