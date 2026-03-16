"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { AnalysisBarChart } from "@/components/analysis-bar-chart";
import { AnalysisResultTable } from "@/components/analysis-result-table";
import { PageShell } from "@/components/page-shell";
import { ResultExportButton } from "@/components/result-export-button";
import { SectionPanel } from "@/components/section-panel";
import { AnalysisApiError, getTaskResult } from "@/lib/analysis/api";
import { findMethodBySlug } from "@/lib/methods";
import type { AnalysisResultPayload } from "@/types/analysis";

type TaskResultPageClientProps = {
  apiBaseUrl: string;
};

export function TaskResultPageClient({ apiBaseUrl }: TaskResultPageClientProps) {
  const searchParams = useSearchParams();
  const taskId = searchParams.get("taskId")?.trim() ?? "";
  const [result, setResult] = useState<AnalysisResultPayload | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!taskId) {
      setResult(null);
      setErrorMessage("请先在分析页完成一次任务，系统会把结果展示在这个网页中。");
      return;
    }

    if (!apiBaseUrl) {
      setResult(null);
      setErrorMessage("当前站点尚未配置分析 API 地址，请先设置 NEXT_PUBLIC_API_BASE_URL。");
      return;
    }

    let disposed = false;

    async function loadResult() {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const nextResult = await getTaskResult(apiBaseUrl, taskId);

        if (!disposed) {
          setResult(nextResult);
        }
      } catch (error) {
        if (disposed) {
          return;
        }

        setResult(null);

        if (error instanceof AnalysisApiError && error.status === 404) {
          setErrorMessage("没有找到对应的任务结果，请确认任务是否已分析完成。");
          return;
        }

        if (error instanceof AnalysisApiError) {
          setErrorMessage(error.message);
          return;
        }

        setErrorMessage("加载结果时出现异常，请稍后重试。");
      } finally {
        if (!disposed) {
          setIsLoading(false);
        }
      }
    }

    void loadResult();

    return () => {
      disposed = true;
    };
  }, [apiBaseUrl, taskId]);

  const method = useMemo(() => (result ? findMethodBySlug(result.method_slug) : null), [result]);

  if (!taskId || errorMessage) {
    return (
      <PageShell currentPath="/methods">
        <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
          <p className="section-label text-xs font-semibold text-[var(--accent-700)]">结果页</p>
          <h1 className="mt-4 font-display text-4xl text-[var(--ink-950)]">网页结果展示</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-[var(--ink-700)]">
            {errorMessage ?? "分析结果会显示在这个固定页面中，并支持后续导出。"}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/methods"
              className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-5 py-3 text-sm font-medium text-white"
            >
              返回方法列表
            </Link>
          </div>
        </section>
      </PageShell>
    );
  }

  if (isLoading || !result) {
    return (
      <PageShell currentPath="/methods">
        <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
          <p className="section-label text-xs font-semibold text-[var(--accent-700)]">结果页</p>
          <h1 className="mt-4 font-display text-4xl text-[var(--ink-950)]">正在加载分析结果</h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-[var(--ink-700)]">
            任务 ID：{taskId}。页面会在拿到后端结果后自动展示摘要、表格、图表和导出入口。
          </p>
        </section>
      </PageShell>
    );
  }

  return (
    <PageShell currentPath="/methods">
      <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
        <p className="section-label text-xs font-semibold text-[var(--accent-700)]">结果页</p>
        <h1 className="mt-4 font-display text-4xl text-[var(--ink-950)]">
          {method ? `${method.name}结果` : "分析结果"}
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-8 text-[var(--ink-700)]">
          当前结果来自真实计算，不使用假数据占位。页面按统一结果结构展示摘要、表格、图表和可读解释，并提供最小可用的报告导出入口。
        </p>

        <div className="mt-6">
          <ResultExportButton apiBaseUrl={apiBaseUrl} taskId={result.task_id} />
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
            <p className="text-xs text-[var(--ink-700)]">任务 ID</p>
            <p className="mt-2 text-sm font-medium text-[var(--ink-950)]">{result.task_id}</p>
          </article>
          <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
            <p className="text-xs text-[var(--ink-700)]">方法标识</p>
            <p className="mt-2 text-sm font-medium text-[var(--ink-950)]">{result.method_slug}</p>
          </article>
          <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
            <p className="text-xs text-[var(--ink-700)]">结果版本</p>
            <p className="mt-2 text-sm font-medium text-[var(--ink-950)]">{result.result_version}</p>
          </article>
          <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
            <p className="text-xs text-[var(--ink-700)]">生成时间</p>
            <p className="mt-2 text-sm font-medium text-[var(--ink-950)]">
              {new Date(result.generated_at).toLocaleString()}
            </p>
          </article>
        </div>
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <SectionPanel
          title={result.summary.title}
          eyebrow="结果摘要"
          description="下列摘要直接基于结构化计算结果生成，用于帮助用户快速把握核心发现。"
        >
          <ul className="space-y-3 text-sm leading-7 text-[var(--ink-700)]">
            {result.summary.highlights.map((highlight) => (
              <li key={highlight} className="rounded-2xl bg-[var(--surface-0)] px-4 py-3">
                {highlight}
              </li>
            ))}
          </ul>
        </SectionPanel>

        <SectionPanel
          title="可读解释"
          eyebrow="解释"
          description="解释文本严格根据本次结果中的表格与图表信息生成，不脱离结果自由发挥。"
        >
          <div className="space-y-4">
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-sm font-medium text-[var(--ink-950)]">通俗解释</p>
              <p className="mt-2 text-sm leading-7 text-[var(--ink-700)]">{result.interpretation.plain_language}</p>
            </article>
            <article className="rounded-[20px] bg-[var(--surface-0)] px-4 py-4">
              <p className="text-sm font-medium text-[var(--ink-950)]">学术表达</p>
              <p className="mt-2 text-sm leading-7 text-[var(--ink-700)]">{result.interpretation.academic_style}</p>
            </article>
          </div>
        </SectionPanel>
      </section>

      {result.tables.length > 0 ? (
        <section className="mt-10 grid gap-5">
          {result.tables.map((table) => (
            <AnalysisResultTable key={table.key} table={table} />
          ))}
        </section>
      ) : null}

      {result.charts.length > 0 ? (
        <section className="mt-10 grid gap-5 lg:grid-cols-2">
          {result.charts.map((chart) => (
            <AnalysisBarChart key={chart.key} chart={chart} />
          ))}
        </section>
      ) : null}
    </PageShell>
  );
}
