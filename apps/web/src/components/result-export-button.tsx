"use client";

import { useState } from "react";

import { AnalysisApiError, createExport } from "@/lib/analysis/api";

type ResultExportButtonProps = {
  apiBaseUrl: string;
  taskId: string;
};

export function ResultExportButton({ apiBaseUrl, taskId }: ResultExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setErrorMessage(null);

    try {
      const result = await createExport(apiBaseUrl, taskId, { export_type: "docx" });
      const downloadUrl = new URL(result.download_url, `${apiBaseUrl}/`).toString();
      window.location.assign(downloadUrl);
    } catch (error) {
      if (error instanceof AnalysisApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("生成导出文件时出现异常，请稍后重试。");
      }
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-3">
      <button
        type="button"
        onClick={handleExport}
        disabled={isExporting}
        className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-5 py-3 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isExporting ? "导出中..." : "导出 DOCX 报告"}
      </button>
      <p className="text-xs leading-6 text-[var(--ink-700)]">当前 MVP 先提供最小可用的 DOCX 报告导出。</p>
      {errorMessage ? (
        <p className="rounded-2xl border border-[rgba(177,78,29,0.12)] bg-[rgba(177,78,29,0.06)] px-3 py-2 text-xs leading-6 text-[var(--ink-900)]">
          {errorMessage}
        </p>
      ) : null}
    </div>
  );
}
