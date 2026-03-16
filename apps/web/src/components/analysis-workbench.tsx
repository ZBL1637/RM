"use client";

import type { ChangeEvent } from "react";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { AnalysisApiError, analyzeTask, createTask, uploadFile, validateTask } from "@/lib/analysis/api";
import type {
  AnalyzeTaskResponseData,
  CreateTaskResponseData,
  UploadResponseData,
  ValidateTaskResponseData,
  ValidationIssue,
} from "@/types/analysis";

type AnalysisWorkbenchProps = {
  apiBaseUrl: string;
  methodSlug: string;
  methodName: string;
  acceptedFileTypes: Array<"csv" | "xlsx">;
  validationEnabled: boolean;
};

function formatFileSize(size: number) {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function formatFieldLabel(field: string) {
  if (field.startsWith("column_")) {
    return field.replace("column_", "第 ") + " 列";
  }
  if (field === "variables") {
    return "字段集合";
  }
  if (field === "outcome") {
    return "因变量";
  }
  if (field === "predictors") {
    return "自变量集合";
  }
  if (field.startsWith("predictor_")) {
    return `自变量 ${field.replace("predictor_", "")}`;
  }
  if (field.startsWith("control_")) {
    return `控制变量 ${field.replace("control_", "")}`;
  }
  return field;
}

function ValidationIssueList({
  title,
  issues,
  tone,
}: {
  title: string;
  issues: ValidationIssue[];
  tone: "error" | "warning";
}) {
  if (issues.length === 0) {
    return null;
  }

  const toneClass =
    tone === "error"
      ? "border-[rgba(177,78,29,0.14)] bg-[rgba(177,78,29,0.06)]"
      : "border-[rgba(35,98,87,0.12)] bg-[rgba(35,98,87,0.06)]";

  return (
    <section className="mt-6">
      <h3 className="text-sm font-semibold text-[var(--ink-950)]">{title}</h3>
      <div className="mt-3 space-y-3">
        {issues.map((issue, index) => (
          <article key={`${issue.code}-${issue.field}-${index}`} className={`rounded-[20px] border px-4 py-4 ${toneClass}`}>
            <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--ink-700)]">
              <span className="rounded-full bg-white px-3 py-1">{issue.code}</span>
              <span className="rounded-full bg-white px-3 py-1">{formatFieldLabel(issue.field)}</span>
            </div>
            <p className="mt-3 text-sm font-medium text-[var(--ink-950)]">{issue.message}</p>
            <p className="mt-2 text-sm leading-7 text-[var(--ink-700)]">建议：{issue.suggestion}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export function AnalysisWorkbench({
  apiBaseUrl,
  methodSlug,
  methodName,
  acceptedFileTypes,
  validationEnabled,
}: AnalysisWorkbenchProps) {
  const router = useRouter();
  const apiConfigured = apiBaseUrl.length > 0;
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponseData | null>(null);
  const [taskResult, setTaskResult] = useState<CreateTaskResponseData | null>(null);
  const [validationResult, setValidationResult] = useState<ValidateTaskResponseData | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeTaskResponseData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const acceptValue = useMemo(() => acceptedFileTypes.map((item) => `.${item}`).join(","), [acceptedFileTypes]);

  const resetDownstreamState = () => {
    setUploadResult(null);
    setTaskResult(null);
    setValidationResult(null);
    setAnalysisResult(null);
    setErrorMessage(null);
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    resetDownstreamState();
  };

  const handleUploadAndCreateTask = async () => {
    if (!selectedFile) {
      setErrorMessage("请先选择一个 .csv 或 .xlsx 文件。");
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);
    setValidationResult(null);

    try {
      const upload = await uploadFile(apiBaseUrl, selectedFile);
      const task = await createTask(apiBaseUrl, {
        method_slug: methodSlug,
        upload_id: upload.upload_id,
      });

      setUploadResult(upload);
      setTaskResult(task);
    } catch (error) {
      if (error instanceof AnalysisApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("上传或创建任务时出现异常，请稍后重试。");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleValidate = async () => {
    if (!taskResult) {
      setErrorMessage("请先完成文件上传并创建任务。");
      return;
    }

    setIsValidating(true);
    setErrorMessage(null);

    try {
      const validation = await validateTask(apiBaseUrl, taskResult.task_id);
      setValidationResult(validation);
    } catch (error) {
      if (error instanceof AnalysisApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("触发校验时出现异常，请稍后重试。");
      }
    } finally {
      setIsValidating(false);
    }
  };

  const handleAnalyze = async () => {
    if (!taskResult) {
      setErrorMessage("请先完成文件上传、创建任务并通过校验。");
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const analysis = await analyzeTask(apiBaseUrl, taskResult.task_id);
      setAnalysisResult(analysis);
      router.push(`/result?taskId=${analysis.task_id}`);
    } catch (error) {
      if (error instanceof AnalysisApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("开始分析时出现异常，请稍后重试。");
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {!apiConfigured ? (
        <section className="rounded-[24px] border border-[rgba(177,78,29,0.12)] bg-[rgba(177,78,29,0.06)] p-6">
          <h2 className="font-display text-2xl text-[var(--ink-950)]">当前站点尚未配置分析 API</h2>
          <p className="mt-3 text-sm leading-7 text-[var(--ink-700)]">
            如果要把前端部署到 GitHub Pages，请先在构建环境中设置 `NEXT_PUBLIC_API_BASE_URL`，让网页能够访问外部分析后端。
          </p>
        </section>
      ) : null}

      {!validationEnabled ? (
        <section className="rounded-[24px] border border-[rgba(177,78,29,0.12)] bg-[rgba(177,78,29,0.06)] p-6">
          <h2 className="font-display text-2xl text-[var(--ink-950)]">当前方法暂未开放校验闭环</h2>
          <p className="mt-3 text-sm leading-7 text-[var(--ink-700)]">
            当前 MVP 已优先打通描述统计与回归分析。其他方法页面先保留结构和入口，后续再逐步补齐真实校验逻辑。
          </p>
        </section>
      ) : null}

      <section className="rounded-[28px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-7 shadow-[0_18px_48px_rgba(77,50,23,0.08)]">
        <h2 className="font-display text-2xl text-[var(--ink-950)]">上传文件并创建任务</h2>
        <p className="mt-3 text-sm leading-7 text-[var(--ink-700)]">
          当前仅支持 {acceptedFileTypes.map((item) => `.${item}`).join(" / ")}。上传成功后，系统会为当前方法创建一个待校验任务。
        </p>

        <div className="mt-6 rounded-[24px] border border-dashed border-[rgba(32,25,20,0.16)] bg-[var(--surface-0)] p-6">
          <label className="block text-sm font-medium text-[var(--ink-950)]" htmlFor="analysis-file">
            选择数据文件
          </label>
          <input
            id="analysis-file"
            type="file"
            accept={acceptValue}
            onChange={handleFileChange}
            disabled={!validationEnabled || !apiConfigured || isUploading}
            className="mt-3 block w-full rounded-2xl border border-[rgba(32,25,20,0.12)] bg-white px-4 py-3 text-sm text-[var(--ink-700)] file:mr-4 file:rounded-full file:border-0 file:bg-[var(--ink-950)] file:px-4 file:py-2 file:text-sm file:font-medium file:text-white"
          />
          <p className="mt-3 text-sm text-[var(--ink-700)]">
            {selectedFile ? `已选择：${selectedFile.name}` : "请选择本地 CSV 或 XLSX 文件。"}
          </p>
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleUploadAndCreateTask}
            disabled={!validationEnabled || !apiConfigured || !selectedFile || isUploading}
            className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isUploading ? "上传中..." : "上传并创建任务"}
          </button>
          <button
            type="button"
            onClick={handleValidate}
            disabled={!validationEnabled || !apiConfigured || !taskResult || isValidating}
            className="inline-flex items-center justify-center rounded-full border border-[rgba(32,25,20,0.12)] px-5 py-3 text-sm font-medium text-[var(--ink-700)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isValidating ? "校验中..." : "开始校验"}
          </button>
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!validationEnabled || !apiConfigured || !validationResult?.validation_passed || isAnalyzing}
            className="inline-flex items-center justify-center rounded-full border border-[rgba(35,98,87,0.18)] bg-[rgba(35,98,87,0.08)] px-5 py-3 text-sm font-medium text-[var(--teal-700)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isAnalyzing ? "分析中..." : "开始分析"}
          </button>
        </div>

        {errorMessage ? (
          <div className="mt-6 rounded-[20px] border border-[rgba(177,78,29,0.12)] bg-[rgba(177,78,29,0.06)] px-4 py-4 text-sm leading-7 text-[var(--ink-900)]">
            {errorMessage}
          </div>
        ) : null}
      </section>

      {uploadResult ? (
        <section className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-6">
          <h3 className="font-display text-xl text-[var(--ink-950)]">上传结果</h3>
          <dl className="mt-4 grid gap-4 text-sm text-[var(--ink-700)] sm:grid-cols-2">
            <div>
              <dt className="font-medium text-[var(--ink-950)]">文件名</dt>
              <dd className="mt-1">{uploadResult.file_name}</dd>
            </div>
            <div>
              <dt className="font-medium text-[var(--ink-950)]">文件类型</dt>
              <dd className="mt-1">.{uploadResult.file_type}</dd>
            </div>
            <div>
              <dt className="font-medium text-[var(--ink-950)]">文件大小</dt>
              <dd className="mt-1">{formatFileSize(uploadResult.file_size)}</dd>
            </div>
            <div>
              <dt className="font-medium text-[var(--ink-950)]">上传时间</dt>
              <dd className="mt-1">{new Date(uploadResult.uploaded_at).toLocaleString()}</dd>
            </div>
          </dl>
        </section>
      ) : null}

      {taskResult ? (
        <section className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-6">
          <h3 className="font-display text-xl text-[var(--ink-950)]">任务状态</h3>
          <dl className="mt-4 grid gap-4 text-sm text-[var(--ink-700)] sm:grid-cols-2">
            <div>
              <dt className="font-medium text-[var(--ink-950)]">任务 ID</dt>
              <dd className="mt-1">{taskResult.task_id}</dd>
            </div>
            <div>
              <dt className="font-medium text-[var(--ink-950)]">当前状态</dt>
              <dd className="mt-1">{analysisResult?.status ?? validationResult?.status ?? taskResult.status}</dd>
            </div>
          </dl>
        </section>
      ) : null}

      {validationResult ? (
        <section className="rounded-[28px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-7 shadow-[0_18px_48px_rgba(77,50,23,0.08)]">
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="font-display text-2xl text-[var(--ink-950)]">校验结果</h2>
            <span
              className={`rounded-full px-4 py-2 text-sm ${
                validationResult.validation_passed
                  ? "bg-[rgba(35,98,87,0.09)] text-[var(--teal-700)]"
                  : "bg-[rgba(177,78,29,0.08)] text-[var(--accent-700)]"
              }`}
            >
              {validationResult.validation_passed ? "可开始分析" : "校验未通过"}
            </span>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-xs text-[var(--ink-700)]">错误数</p>
              <p className="mt-2 text-2xl font-semibold text-[var(--ink-950)]">
                {validationResult.validation.summary.error_count}
              </p>
            </article>
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-xs text-[var(--ink-700)]">警告数</p>
              <p className="mt-2 text-2xl font-semibold text-[var(--ink-950)]">
                {validationResult.validation.summary.warning_count}
              </p>
            </article>
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-xs text-[var(--ink-700)]">样本量</p>
              <p className="mt-2 text-2xl font-semibold text-[var(--ink-950)]">
                {validationResult.validation.stats.row_count}
              </p>
            </article>
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-xs text-[var(--ink-700)]">字段数</p>
              <p className="mt-2 text-2xl font-semibold text-[var(--ink-950)]">
                {validationResult.validation.stats.column_count}
              </p>
            </article>
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-xs text-[var(--ink-700)]">缺失比例</p>
              <p className="mt-2 text-2xl font-semibold text-[var(--ink-950)]">
                {(validationResult.validation.stats.missing_ratio * 100).toFixed(1)}%
              </p>
            </article>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4 text-sm text-[var(--ink-700)]">
              <p className="font-medium text-[var(--ink-950)]">数值型字段</p>
              <p className="mt-2">{validationResult.validation.stats.numeric_column_count}</p>
            </article>
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4 text-sm text-[var(--ink-700)]">
              <p className="font-medium text-[var(--ink-950)]">分类型字段</p>
              <p className="mt-2">{validationResult.validation.stats.categorical_column_count}</p>
            </article>
          </div>

          <ValidationIssueList title="错误项" issues={validationResult.validation.errors} tone="error" />
          <ValidationIssueList title="提醒项" issues={validationResult.validation.warnings} tone="warning" />

          {validationResult.validation_passed ? (
            <div className="mt-6 rounded-[20px] border border-[rgba(35,98,87,0.12)] bg-[rgba(35,98,87,0.06)] px-4 py-4">
              <p className="text-sm font-medium text-[var(--ink-950)]">当前数据已进入“可开始分析”状态。</p>
              <p className="mt-2 text-sm leading-7 text-[var(--ink-700)]">
                现在可以直接点击“开始分析”，系统会执行真实的 {methodName} 计算并跳转到结果页。
              </p>
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
