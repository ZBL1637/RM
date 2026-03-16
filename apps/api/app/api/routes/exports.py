from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from app.api.responses import build_error_response
from app.core.errors import ServiceError
from app.services.export_service import export_service

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/{export_id}/download", response_model=None)
def download_export(export_id: str) -> FileResponse | JSONResponse:
    try:
        export_file = export_service.get_export_file(export_id)
    except ServiceError as error:
        return build_error_response(error)

    file_path = Path(export_file.storage_path)
    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    filename = f"{export_file.task_id}_{export_file.export_type}_report.docx"
    return FileResponse(path=file_path, media_type=media_type, filename=filename)
