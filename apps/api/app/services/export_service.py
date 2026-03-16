from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.errors import ServiceError
from app.exporters.docx_exporter import export_result_to_docx
from app.repositories.export_repository import export_repository
from app.repositories.method_repository import method_repository
from app.repositories.task_repository import task_repository
from app.repositories.analysis_result_repository import analysis_result_repository
from app.schemas.exports import CreateExportResponseData, ExportFileRecord


class ExportService:
    def create_export(self, task_id: str, export_type: str) -> CreateExportResponseData:
        task = task_repository.get(task_id)
        if task is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应任务，请确认任务 ID 是否正确。",
                error_code="TASK_NOT_FOUND",
                details={"task_id": task_id},
            )

        if task.status != "success":
            raise ServiceError(
                status_code=400,
                message="当前任务尚未完成分析，暂时不能导出报告。",
                error_code="EXPORT_NOT_READY",
                details={"task_id": task_id, "status": task.status},
            )

        result_record = analysis_result_repository.get_by_task_id(task_id)
        if result_record is None:
            raise ServiceError(
                status_code=404,
                message="当前任务还没有分析结果，请先完成分析。",
                error_code="RESULT_NOT_FOUND",
                details={"task_id": task_id},
            )

        method = method_repository.get_active_by_slug(result_record.method_slug)
        if method is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应方法配置，暂时无法生成导出文件。",
                error_code="METHOD_NOT_FOUND",
                details={"method_slug": result_record.method_slug},
            )

        if export_type != "docx":
            raise ServiceError(
                status_code=400,
                message="当前 MVP 仅支持导出 DOCX 报告。",
                error_code="EXPORT_TYPE_NOT_SUPPORTED",
                details={"export_type": export_type},
            )

        export_id = f"exp_{uuid4().hex[:12]}"
        destination = _build_export_path(export_id, "docx")
        export_result_to_docx(method, result_record.result_json, destination)

        export_repository.save(
            ExportFileRecord(
                id=export_id,
                task_id=task_id,
                export_type="docx",
                storage_path=str(destination),
                created_at=_utc_now(),
            )
        )

        return CreateExportResponseData(
            export_id=export_id,
            download_url=f"/api/exports/{export_id}/download",
        )

    def get_export_file(self, export_id: str) -> ExportFileRecord:
        export_file = export_repository.get(export_id)
        if export_file is None:
            raise ServiceError(
                status_code=404,
                message="未找到对应导出文件，请重新生成报告后再下载。",
                error_code="EXPORT_NOT_FOUND",
                details={"export_id": export_id},
            )

        if not Path(export_file.storage_path).exists():
            raise ServiceError(
                status_code=404,
                message="导出文件不存在，请重新生成报告后再下载。",
                error_code="EXPORT_FILE_MISSING",
                details={"export_id": export_id},
            )

        return export_file


def _build_export_path(export_id: str, suffix: str) -> Path:
    now = datetime.now(timezone.utc)
    return settings.storage_root / "exports" / f"{now:%Y}" / f"{now:%m}" / f"{export_id}.{suffix}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


export_service = ExportService()
