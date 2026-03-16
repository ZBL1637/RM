from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.responses import build_error_response
from app.core.errors import ServiceError
from app.schemas.common import ApiErrorResponse, ApiSuccessResponse
from app.schemas.exports import CreateExportRequest, CreateExportResponseData
from app.schemas.results import AnalysisResultPayload
from app.schemas.tasks import AnalyzeTaskResponseData, CreateTaskRequest, CreateTaskResponseData
from app.schemas.validation import ValidateTaskResponseData
from app.services.analysis_service import analysis_service
from app.services.export_service import export_service
from app.services.task_service import task_service
from app.services.validation_service import validation_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=ApiSuccessResponse[CreateTaskResponseData],
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
def create_task(payload: CreateTaskRequest) -> ApiSuccessResponse[CreateTaskResponseData] | JSONResponse:
    try:
        task = task_service.create_task(method_slug=payload.method_slug, upload_id=payload.upload_id)
    except ServiceError as error:
        return build_error_response(error)

    return ApiSuccessResponse(message="task created", data=task)


@router.post(
    "/{task_id}/validate",
    response_model=ApiSuccessResponse[ValidateTaskResponseData],
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
def validate_task(task_id: str) -> ApiSuccessResponse[ValidateTaskResponseData] | JSONResponse:
    try:
        validation = validation_service.validate_task(task_id)
    except ServiceError as error:
        return build_error_response(error)

    return ApiSuccessResponse(message="validated", data=validation)


@router.post(
    "/{task_id}/analyze",
    response_model=ApiSuccessResponse[AnalyzeTaskResponseData],
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
def analyze_task(task_id: str) -> ApiSuccessResponse[AnalyzeTaskResponseData] | JSONResponse:
    try:
        result = analysis_service.analyze_task(task_id)
    except ServiceError as error:
        return build_error_response(error)

    return ApiSuccessResponse(message="analysis completed", data=result)


@router.get(
    "/{task_id}/result",
    response_model=ApiSuccessResponse[AnalysisResultPayload],
    responses={404: {"model": ApiErrorResponse}},
)
def get_task_result(task_id: str) -> ApiSuccessResponse[AnalysisResultPayload] | JSONResponse:
    try:
        result = analysis_service.get_result(task_id)
    except ServiceError as error:
        return build_error_response(error)

    return ApiSuccessResponse(message="ok", data=result)


@router.post(
    "/{task_id}/export",
    response_model=ApiSuccessResponse[CreateExportResponseData],
    responses={400: {"model": ApiErrorResponse}, 404: {"model": ApiErrorResponse}},
)
def create_export(task_id: str, payload: CreateExportRequest) -> ApiSuccessResponse[CreateExportResponseData] | JSONResponse:
    try:
        export_result = export_service.create_export(task_id=task_id, export_type=payload.export_type)
    except ServiceError as error:
        return build_error_response(error)

    return ApiSuccessResponse(message="export created", data=export_result)
