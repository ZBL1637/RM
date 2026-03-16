import type {
  AnalysisResultPayload,
  ApiAnalysisErrorResponse,
  ApiAnalysisSuccessResponse,
  AnalyzeTaskResponseData,
  CreateExportRequest,
  CreateExportResponseData,
  CreateTaskRequest,
  CreateTaskResponseData,
  UploadResponseData,
  ValidateTaskResponseData,
} from "@/types/analysis";

export class AnalysisApiError extends Error {
  status: number;
  errorCode?: string;
  details?: Record<string, unknown>;

  constructor(message: string, status: number, errorCode?: string, details?: Record<string, unknown>) {
    super(message);
    this.name = "AnalysisApiError";
    this.status = status;
    this.errorCode = errorCode;
    this.details = details;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = (await response.json()) as ApiAnalysisSuccessResponse<T> | ApiAnalysisErrorResponse;

  if (!response.ok || !payload.success) {
    const errorPayload = payload as ApiAnalysisErrorResponse;
    throw new AnalysisApiError(
      errorPayload.message ?? "请求失败，请稍后重试。",
      response.status,
      errorPayload.error_code,
      errorPayload.details,
    );
  }

  return payload.data;
}

export async function uploadFile(apiBaseUrl: string, file: File): Promise<UploadResponseData> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${apiBaseUrl}/api/uploads`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<UploadResponseData>(response);
}

export async function createTask(apiBaseUrl: string, payload: CreateTaskRequest): Promise<CreateTaskResponseData> {
  const response = await fetch(`${apiBaseUrl}/api/tasks`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseResponse<CreateTaskResponseData>(response);
}

export async function validateTask(apiBaseUrl: string, taskId: string): Promise<ValidateTaskResponseData> {
  const response = await fetch(`${apiBaseUrl}/api/tasks/${taskId}/validate`, {
    method: "POST",
  });

  return parseResponse<ValidateTaskResponseData>(response);
}

export async function analyzeTask(apiBaseUrl: string, taskId: string): Promise<AnalyzeTaskResponseData> {
  const response = await fetch(`${apiBaseUrl}/api/tasks/${taskId}/analyze`, {
    method: "POST",
  });

  return parseResponse<AnalyzeTaskResponseData>(response);
}

export async function getTaskResult(apiBaseUrl: string, taskId: string): Promise<AnalysisResultPayload> {
  const response = await fetch(`${apiBaseUrl}/api/tasks/${taskId}/result`, {
    cache: "no-store",
  });

  return parseResponse<AnalysisResultPayload>(response);
}

export async function createExport(
  apiBaseUrl: string,
  taskId: string,
  payload: CreateExportRequest,
): Promise<CreateExportResponseData> {
  const response = await fetch(`${apiBaseUrl}/api/tasks/${taskId}/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseResponse<CreateExportResponseData>(response);
}
