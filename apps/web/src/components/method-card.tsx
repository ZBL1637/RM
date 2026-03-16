import Link from "next/link";

import { methodCategoryLabels } from "@/lib/methods";
import type { Method } from "@/types/methods";

type MethodCardProps = {
  method: Method;
};

export function MethodCard({ method }: MethodCardProps) {
  return (
    <article className="flex h-full flex-col rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-6 shadow-[0_16px_40px_rgba(77,50,23,0.08)]">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-[var(--surface-0)] px-3 py-1 text-xs font-medium text-[var(--ink-700)]">
          {methodCategoryLabels[method.category]}
        </span>
        <span className="rounded-full bg-[rgba(35,98,87,0.09)] px-3 py-1 text-xs font-medium text-[var(--teal-700)]">
          难度 {method.analysisDifficulty}
        </span>
      </div>

      <h3 className="mt-5 font-display text-2xl text-[var(--ink-950)]">{method.name}</h3>
      <p className="mt-3 text-sm leading-7 text-[var(--ink-700)]">{method.description}</p>

      <dl className="mt-5 space-y-4 text-sm">
        <div>
          <dt className="font-medium text-[var(--ink-950)]">适用场景</dt>
          <dd className="mt-1 leading-7 text-[var(--ink-700)]">{method.applicableScenarios[0]}</dd>
        </div>
        <div>
          <dt className="font-medium text-[var(--ink-950)]">数据类型</dt>
          <dd className="mt-1 leading-7 text-[var(--ink-700)]">{method.dataTypeLabel}</dd>
        </div>
        <div>
          <dt className="font-medium text-[var(--ink-950)]">样本要求</dt>
          <dd className="mt-1 leading-7 text-[var(--ink-700)]">{method.sampleRequirement}</dd>
        </div>
      </dl>

      <div className="mt-6 flex items-center gap-3">
        <Link
          href={`/methods/${method.slug}`}
          className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-4 py-2 text-sm font-medium text-white transition hover:bg-[var(--ink-900)]"
        >
          查看详情
        </Link>
        <Link
          href={`/analysis/${method.slug}`}
          className="inline-flex items-center justify-center rounded-full border border-[rgba(32,25,20,0.12)] px-4 py-2 text-sm font-medium text-[var(--ink-700)] transition hover:border-[rgba(32,25,20,0.2)] hover:bg-white"
        >
          立即使用
        </Link>
      </div>
    </article>
  );
}
