from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.analyzers.descriptive_stats_analyzer import analyze_descriptive_stats
from app.analyzers.regression_analyzer import analyze_regression
from app.core.errors import ServiceError
from app.repositories.analysis_result_repository import analysis_result_repository
from app.repositories.task_repository import task_repository
from app.repositories.upload_repository import upload_repository
from app.schemas.results import AnalysisResultPayload, AnalysisResultRecord
from app.schemas.tasks import AnalyzeTaskResponseData


class AnalysisService:
    def analyze_task(self, task_id: str) -> AnalyzeTaskResponseData:
        task = task_repository.get(task_id)
        if task is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应任务，请重新创建任务后再分析。",
                error_code="TASK_NOT_FOUND",
                details={"task_id": task_id},
            )

        if task.method_slug not in {"descriptive_stats", "regression"}:
            raise ServiceError(
                status_code=400,
                message="当前仅描述统计和回归分析已接入真实分析能力。",
                error_code="ANALYSIS_NOT_IMPLEMENTED",
                details={"method_slug": task.method_slug},
            )

        if task.validation_passed is not True:
            raise ServiceError(
                status_code=400,
                message="当前任务尚未通过校验，请先修复数据问题再开始分析。",
                error_code="VALIDATION_REQUIRED",
                details={"task_id": task.id, "status": task.status},
            )

        upload = upload_repository.get(task.upload_id)
        if upload is None:
            raise ServiceError(
                status_code=404,
                message="任务关联的上传文件不存在，请重新上传文件。",
                error_code="UPLOAD_NOT_FOUND",
                details={"upload_id": task.upload_id, "task_id": task.id},
            )

        existing_result = analysis_result_repository.get_by_task_id(task.id)
        if existing_result is not None:
            completed_task = task.model_copy(
                update={"status": "success", "started_at": task.started_at or existing_result.created_at, "finished_at": existing_result.created_at}
            )
            task_repository.update(completed_task)
            return AnalyzeTaskResponseData(task_id=task.id, status=completed_task.status)

        analyzing_task = task.model_copy(
            update={
                "status": "analyzing",
                "started_at": _utc_now(),
                "error_code": None,
                "error_message": None,
            }
        )
        task_repository.update(analyzing_task)

        try:
            if task.method_slug == "descriptive_stats":
                result = analyze_descriptive_stats(task_id=task.id, file_path=upload.storage_path, file_type=upload.file_type)
            else:
                result = analyze_regression(task_id=task.id, file_path=upload.storage_path, file_type=upload.file_type)
        except ServiceError as error:
            failed_task = analyzing_task.model_copy(
                update={
                    "status": "failed",
                    "finished_at": _utc_now(),
                    "error_code": error.error_code,
                    "error_message": error.message,
                }
            )
            task_repository.update(failed_task)
            raise
        except ValueError as error:
            failed_task = analyzing_task.model_copy(
                update={
                    "status": "failed",
                    "finished_at": _utc_now(),
                    "error_code": "FILE_PARSE_FAILED",
                    "error_message": "分析时无法读取上传文件，请重新上传后再试。",
                }
            )
            task_repository.update(failed_task)
            raise ServiceError(
                status_code=400,
                message="分析时无法读取上传文件，请重新上传后再试。",
                error_code="FILE_PARSE_FAILED",
                details={"task_id": task.id, "upload_id": upload.id, "reason": str(error)},
            ) from error

        created_at = _utc_now()
        analysis_result_repository.save(
            AnalysisResultRecord(
                id=f"res_{uuid4().hex[:12]}",
                task_id=task.id,
                method_slug=task.method_slug,
                result_json=result,
                summary_text=result.interpretation.plain_language,
                created_at=created_at,
            )
        )

        completed_task = analyzing_task.model_copy(update={"status": "success", "finished_at": created_at})
        task_repository.update(completed_task)

        return AnalyzeTaskResponseData(task_id=task.id, status=completed_task.status)

    def get_result(self, task_id: str) -> AnalysisResultPayload:
        task = task_repository.get(task_id)
        if task is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应任务，请确认任务 ID 是否正确。",
                error_code="TASK_NOT_FOUND",
                details={"task_id": task_id},
            )

        result = analysis_result_repository.get_by_task_id(task_id)
        if result is None:
            raise ServiceError(
                status_code=404,
                message="当前任务还没有分析结果，请先完成分析。",
                error_code="RESULT_NOT_FOUND",
                details={"task_id": task_id, "status": task.status},
            )

        return result.result_json


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


analysis_service = AnalysisService()
