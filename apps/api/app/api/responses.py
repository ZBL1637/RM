from __future__ import annotations

from fastapi.responses import JSONResponse

from app.core.errors import ServiceError
from app.schemas.common import ApiErrorResponse


def build_error_response(error: ServiceError) -> JSONResponse:
    payload = ApiErrorResponse(
        message=error.message,
        error_code=error.error_code,
        details=error.details,
    )
    return JSONResponse(status_code=error.status_code, content=payload.model_dump())
