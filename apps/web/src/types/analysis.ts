import type { ApiErrorResponse, ApiSuccessResponse } from "@/types/methods";

export type UploadResponseData = {
  upload_id: string;
  file_name: string;
  file_size: number;
  file_type: "csv" | "xlsx";
  mime_type: string | null;
  uploaded_at: string;
};

export type TaskStatus = "created" | "uploaded" | "validating" | "validated" | "analyzing" | "success" | "failed" | "canceled";

export type CreateTaskRequest = {
  method_slug: string;
  upload_id: string;
};

export type CreateTaskResponseData = {
  task_id: string;
  status: TaskStatus;
};

export type AnalyzeTaskResponseData = {
  task_id: string;
  status: TaskStatus;
};

export type ExportType = "pdf" | "docx" | "md";

export type CreateExportRequest = {
  export_type: ExportType;
};

export type CreateExportResponseData = {
  export_id: string;
  download_url: string;
};

export type ValidationIssue = {
  code: string;
  level: "error" | "warning" | "info";
  field: string;
  message: string;
  suggestion: string;
};

export type ValidationReport = {
  passed: boolean;
  summary: {
    error_count: number;
    warning_count: number;
  };
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  stats: {
    row_count: number;
    column_count: number;
    missing_ratio: number;
    numeric_column_count: number;
    categorical_column_count: number;
  };
};

export type ValidateTaskResponseData = {
  task_id: string;
  status: TaskStatus;
  validation_passed: boolean;
  validation: ValidationReport;
};

export type AnalysisSummary = {
  title: string;
  highlights: string[];
};

export type AnalysisTable = {
  key: string;
  title: string;
  columns: string[];
  rows: Array<Array<string | number | null>>;
};

export type AnalysisChart = {
  key: string;
  title: string;
  type: "bar";
  data: {
    labels: string[];
    values: number[];
  };
};

export type AnalysisInterpretation = {
  plain_language: string;
  academic_style: string;
};

export type AnalysisResultPayload = {
  task_id: string;
  method_slug: string;
  status: "success";
  result_version: string;
  generated_at: string;
  summary: AnalysisSummary;
  tables: AnalysisTable[];
  charts: AnalysisChart[];
  interpretation: AnalysisInterpretation;
  report_payload: Record<string, unknown>;
};

export type ApiAnalysisSuccessResponse<T> = ApiSuccessResponse<T>;
export type ApiAnalysisErrorResponse = ApiErrorResponse;
