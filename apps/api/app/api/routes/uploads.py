from __future__ import annotations

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.api.responses import build_error_response
from app.core.errors import ServiceError
from app.schemas.common import ApiErrorResponse, ApiSuccessResponse
from app.schemas.uploads import UploadResponseData
from app.services.upload_service import upload_service

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post(
    "",
    response_model=ApiSuccessResponse[UploadResponseData],
    responses={400: {"model": ApiErrorResponse}},
)
async def create_upload(file: UploadFile = File(...)) -> ApiSuccessResponse[UploadResponseData] | JSONResponse:
    try:
        upload = await upload_service.create_upload(file)
    except ServiceError as error:
        return build_error_response(error)

    return ApiSuccessResponse(message="uploaded", data=upload)
