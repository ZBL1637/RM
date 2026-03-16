import { Suspense } from "react";

import { PageShell } from "@/components/page-shell";
import { TaskResultPageClient } from "@/components/task-result-page-client";
import { getApiBaseUrl } from "@/lib/api-base";

function ResultPageFallback() {
  return (
    <PageShell currentPath="/methods">
      <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
        <p className="section-label text-xs font-semibold text-[var(--accent-700)]">结果页</p>
        <h1 className="mt-4 font-display text-4xl text-[var(--ink-950)]">正在准备结果页面</h1>
        <p className="mt-4 max-w-3xl text-base leading-8 text-[var(--ink-700)]">
          页面会在浏览器中读取任务参数，并把分析结果展示在这个固定网页中。
        </p>
      </section>
    </PageShell>
  );
}

export default function ResultPage() {
  return (
    <Suspense fallback={<ResultPageFallback />}>
      <TaskResultPageClient apiBaseUrl={getApiBaseUrl()} />
    </Suspense>
  );
}
