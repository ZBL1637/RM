from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.core.errors import ServiceError
from app.repositories.task_repository import task_repository
from app.repositories.upload_repository import upload_repository
from app.repositories.validation_repository import validation_repository
from app.schemas.validation import (
    ValidateTaskResponseData,
    ValidationReportRecord,
)
from app.validators.descriptive_stats_validator import validate_descriptive_stats_file
from app.validators.regression_validator import validate_regression_file


class ValidationService:
    def validate_task(self, task_id: str) -> ValidateTaskResponseData:
        task = task_repository.get(task_id)
        if task is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应任务，请重新创建任务后再校验。",
                error_code="TASK_NOT_FOUND",
                details={"task_id": task_id},
            )

        upload = upload_repository.get(task.upload_id)
        if upload is None:
            raise ServiceError(
                status_code=404,
                message="任务关联的上传文件不存在，请重新上传文件。",
                error_code="UPLOAD_NOT_FOUND",
                details={"upload_id": task.upload_id, "task_id": task.id},
            )

        if task.method_slug not in {"descriptive_stats", "regression"}:
            raise ServiceError(
                status_code=400,
                message="当前仅描述统计和回归分析已打通数据校验闭环。",
                error_code="VALIDATION_NOT_IMPLEMENTED",
                details={"method_slug": task.method_slug},
            )

        validating_task = task.model_copy(update={"status": "validating", "error_code": None, "error_message": None})
        task_repository.update(validating_task)

        try:
            if task.method_slug == "descriptive_stats":
                report = validate_descriptive_stats_file(upload.storage_path, upload.file_type)
            else:
                report = validate_regression_file(upload.storage_path, upload.file_type)
        except ValueError as error:
            failed_task = validating_task.model_copy(
                update={
                    "status": "failed",
                    "error_code": "FILE_PARSE_FAILED",
                    "error_message": "文件无法解析，请检查文件格式和内容后重试。",
                }
            )
            task_repository.update(failed_task)
            raise ServiceError(
                status_code=400,
                message="文件无法解析，请检查文件格式和内容后重试。",
                error_code="FILE_PARSE_FAILED",
                details={"task_id": task.id, "upload_id": upload.id, "reason": str(error)},
            ) from error

        completed_task = validating_task.model_copy(
            update={
                "status": "validated",
                "validation_passed": report.passed,
                "error_code": None,
                "error_message": None,
            }
        )
        task_repository.update(completed_task)

        validation_repository.save(
            ValidationReportRecord(
                id=f"val_{uuid4().hex[:12]}",
                task_id=task.id,
                passed=report.passed,
                error_count=report.summary.error_count,
                warning_count=report.summary.warning_count,
                report_json=report,
                created_at=_utc_now(),
            )
        )

        return ValidateTaskResponseData(
            task_id=task.id,
            status=completed_task.status,
            validation_passed=report.passed,
            validation=report,
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


validation_service = ValidationService()
