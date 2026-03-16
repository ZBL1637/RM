import Link from "next/link";
import { notFound } from "next/navigation";

import { AnalysisWorkbench } from "@/components/analysis-workbench";
import { PageShell } from "@/components/page-shell";
import { SectionPanel } from "@/components/section-panel";
import { getApiBaseUrl } from "@/lib/api-base";
import { getMethodBySlug, getMethodSlugs, methodCategoryLabels } from "@/lib/methods";

type AnalysisPageProps = {
  params: Promise<{
    methodSlug: string;
  }>;
};

export function generateStaticParams() {
  return getMethodSlugs().map((methodSlug) => ({ methodSlug }));
}

export const dynamicParams = false;

export default async function AnalysisPage({ params }: AnalysisPageProps) {
  const { methodSlug } = await params;
  const method = await getMethodBySlug(methodSlug);

  if (!method) {
    notFound();
  }

  const validationEnabled = ["descriptive_stats", "regression"].includes(method.slug);

  return (
    <PageShell currentPath="/methods">
      <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
        <Link href={`/methods/${method.slug}`} className="text-sm text-[var(--ink-700)] hover:text-[var(--ink-950)]">
          方法详情 / {method.name} / 上传与校验
        </Link>

        <div className="mt-5 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-[var(--surface-0)] px-3 py-1 text-xs font-medium text-[var(--ink-700)]">
            {methodCategoryLabels[method.category]}
          </span>
          <span className="rounded-full bg-[rgba(35,98,87,0.09)] px-3 py-1 text-xs font-medium text-[var(--teal-700)]">
            当前状态：{validationEnabled ? "已接入真实闭环" : "占位流程"}
          </span>
        </div>

        <h1 className="mt-5 font-display text-4xl text-[var(--ink-950)]">上传与校验：{method.name}</h1>
        <p className="mt-4 max-w-4xl text-base leading-8 text-[var(--ink-700)]">
          当前页面对应架构文档中的 `/analysis/[methodSlug]`。本轮已为描述统计与回归分析接入真实上传、校验和分析闭环，
          其他方法仍保留占位结构。
        </p>
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-[0.88fr_1.12fr]">
        <SectionPanel
          title="方法输入要求"
          eyebrow="上传前检查"
          description="上传前先确认文件格式、字段范围和样本要求，以减少后续校验报错。"
        >
          <div className="space-y-4 text-sm leading-7 text-[var(--ink-700)]">
            <div>
              <p className="font-medium text-[var(--ink-950)]">支持文件格式</p>
              <p className="mt-2">{method.inputSpec.acceptedFileTypes.map((item) => `.${item}`).join(" / ")}</p>
            </div>
            <div>
              <p className="font-medium text-[var(--ink-950)]">样本要求</p>
              <p className="mt-2">{method.sampleRequirement}</p>
            </div>
            <div>
              <p className="font-medium text-[var(--ink-950)]">字段说明</p>
              <ul className="mt-3 space-y-3">
                {method.inputSpec.fields.map((field) => (
                  <li key={field.name} className="rounded-2xl bg-[var(--surface-0)] px-4 py-3">
                    <span className="font-medium text-[var(--ink-950)]">{field.label}</span>
                    <span className="ml-2 text-[var(--ink-700)]">{field.description}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </SectionPanel>

        <AnalysisWorkbench
          apiBaseUrl={getApiBaseUrl()}
          methodSlug={method.slug}
          methodName={method.name}
          acceptedFileTypes={method.inputSpec.acceptedFileTypes}
          validationEnabled={validationEnabled}
        />
      </section>
    </PageShell>
  );
}
