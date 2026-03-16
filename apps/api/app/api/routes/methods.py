from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.common import ApiErrorResponse, ApiSuccessResponse
from app.schemas.methods import MethodDetail, MethodSummary
from app.services.method_service import method_service

router = APIRouter(prefix="/api/methods", tags=["methods"])


@router.get("", response_model=ApiSuccessResponse[list[MethodSummary]])
def list_methods() -> ApiSuccessResponse[list[MethodSummary]]:
    methods = method_service.list_methods()
    return ApiSuccessResponse(message="ok", data=methods)


@router.get(
    "/{slug}",
    response_model=ApiSuccessResponse[MethodDetail],
    responses={404: {"model": ApiErrorResponse}},
)
def get_method_detail(slug: str) -> ApiSuccessResponse[MethodDetail] | JSONResponse:
    method = method_service.get_method_by_slug(slug)
    if method is None:
        error = ApiErrorResponse(
            message="method not found",
            error_code="METHOD_NOT_FOUND",
            details={"slug": slug},
        )
        return JSONResponse(status_code=404, content=error.model_dump())

    return ApiSuccessResponse(message="ok", data=method)
