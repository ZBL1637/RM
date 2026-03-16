import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { DetailSection } from "@/components/detail-section";
import { PageShell } from "@/components/page-shell";
import { getMethodBySlug, getMethodSlugs, methodCategoryLabels } from "@/lib/methods";
import type { MethodFieldSpec } from "@/types/methods";

type MethodDetailPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export function generateStaticParams() {
  return getMethodSlugs().map((slug) => ({ slug }));
}

export const dynamicParams = false;

const fieldTypeLabels: Record<string, string> = {
  number: "数值型",
  category: "分类型",
  set_membership: "集合隶属度",
};

function getFieldTypeLabel(type: string) {
  return fieldTypeLabels[type] ?? type;
}

function renderFieldRequirements(fields: MethodFieldSpec[]) {
  return (
    <div className="space-y-3">
      {fields.map((field) => (
        <article key={field.name} className="rounded-2xl bg-[var(--surface-0)] px-4 py-4">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="font-medium text-[var(--ink-950)]">{field.label}</h4>
            <span className="rounded-full bg-white px-3 py-1 text-xs text-[var(--ink-700)]">
              {getFieldTypeLabel(field.type)}
            </span>
            <span className="rounded-full bg-white px-3 py-1 text-xs text-[var(--ink-700)]">
              {field.required ? "必填" : "可选"}
            </span>
          </div>
          <p className="mt-2 text-sm leading-7 text-[var(--ink-700)]">{field.description}</p>
        </article>
      ))}
    </div>
  );
}

export async function generateMetadata({ params }: MethodDetailPageProps): Promise<Metadata> {
  const { slug } = await params;
  const method = await getMethodBySlug(slug);

  if (!method) {
    return {
      title: "方法不存在",
    };
  }

  return {
    title: method.name,
    description: method.description,
  };
}

export default async function MethodDetailPage({ params }: MethodDetailPageProps) {
  const { slug } = await params;
  const method = await getMethodBySlug(slug);

  if (!method) {
    notFound();
  }

  return (
    <PageShell currentPath="/methods">
      <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
        <Link href="/methods" className="text-sm text-[var(--ink-700)] hover:text-[var(--ink-950)]">
          方法列表 / {method.name}
        </Link>

        <div className="mt-5 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-[var(--surface-0)] px-3 py-1 text-xs font-medium text-[var(--ink-700)]">
            {methodCategoryLabels[method.category]}
          </span>
          <span className="rounded-full bg-[rgba(35,98,87,0.09)] px-3 py-1 text-xs font-medium text-[var(--teal-700)]">
            难度 {method.analysisDifficulty}
          </span>
        </div>

        <h1 className="mt-5 font-display text-4xl text-[var(--ink-950)]">{method.name}</h1>
        <p className="mt-4 max-w-4xl text-base leading-8 text-[var(--ink-700)]">{method.description}</p>

        <div className="mt-8 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-[var(--surface-0)] p-6">
            <p className="text-sm font-medium text-[var(--ink-950)]">适用场景</p>
            <ul className="mt-4 space-y-3 text-sm leading-7 text-[var(--ink-700)]">
              {method.applicableScenarios.map((scenario) => (
                <li key={scenario}>{scenario}</li>
              ))}
            </ul>
          </div>

          <aside className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white p-6">
            <p className="text-sm font-medium text-[var(--ink-950)]">操作入口</p>
            <div className="mt-4 flex flex-col gap-3">
              <button
                type="button"
                disabled
                className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-4 py-3 text-sm font-medium text-white opacity-85"
              >
                {method.templateResource.label}
              </button>
              <button
                type="button"
                disabled
                className="inline-flex items-center justify-center rounded-full border border-[rgba(32,25,20,0.12)] px-4 py-3 text-sm font-medium text-[var(--ink-700)]"
              >
                {method.sampleResource.label}
              </button>
              <Link
                href={`/analysis/${method.slug}`}
                className="inline-flex items-center justify-center rounded-full border border-dashed border-[rgba(32,25,20,0.16)] px-4 py-3 text-sm font-medium text-[var(--ink-700)] transition hover:border-[rgba(32,25,20,0.24)] hover:bg-[var(--surface-0)]"
              >
                立即使用
              </Link>
            </div>
            <p className="mt-4 text-sm leading-7 text-[var(--ink-700)]">
              上传与分析页已按架构文档中的 `/analysis/[methodSlug]` 路径接入，当前优先支持描述统计与回归分析的真实闭环。
            </p>
          </aside>
        </div>
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-2">
        <DetailSection title="输入要求" description="不同方法对应不同模板和校验规则，当前页面字段要求来自静态方法目录。">
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-[var(--ink-950)]">支持文件格式</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {method.inputSpec.acceptedFileTypes.map((fileType) => (
                  <span
                    key={fileType}
                    className="rounded-full bg-[var(--surface-0)] px-3 py-1 text-sm text-[var(--ink-700)]"
                  >
                    .{fileType}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-[var(--ink-950)]">字段要求</p>
              <div className="mt-3">{renderFieldRequirements(method.inputSpec.fields)}</div>
            </div>
          </div>
        </DetailSection>

        <DetailSection
          title="样本要求"
          description={method.sampleRequirement}
          items={method.inputSpec.minSampleSize ? [`建议样本量不少于 ${method.inputSpec.minSampleSize}`] : undefined}
        />

        <DetailSection title="适用数据类型" description={method.dataTypeLabel} />

        <DetailSection title="前提条件" items={method.prerequisites} />

        <DetailSection title="输出说明" description={method.outputSpec.summary} items={method.outputSpec.resultBlocks} />

        <DetailSection title="常见错误说明" items={method.commonErrors} />
      </section>
    </PageShell>
  );
}
