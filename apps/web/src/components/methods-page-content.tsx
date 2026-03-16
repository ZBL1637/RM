import Link from "next/link";

import { MethodCard } from "@/components/method-card";
import { PageShell } from "@/components/page-shell";
import { SectionPanel } from "@/components/section-panel";
import { methodCategoryLabels } from "@/lib/methods";
import type { Method, MethodCategory } from "@/types/methods";

type MethodsPageContentProps = {
  methods: Method[];
  selectedCategory: "all" | MethodCategory;
};

const filterOptions: Array<{ value: "all" | MethodCategory; label: string }> = [
  { value: "all", label: "全部方法" },
  { value: "quantitative", label: methodCategoryLabels.quantitative },
  { value: "configurational", label: methodCategoryLabels.configurational },
];

function getFilterHref(value: "all" | MethodCategory) {
  if (value === "all") {
    return "/methods";
  }

  return `/methods/category/${value}`;
}

export function MethodsPageContent({ methods, selectedCategory }: MethodsPageContentProps) {
  const filteredMethods =
    selectedCategory === "all" ? methods : methods.filter((method) => method.category === selectedCategory);

  return (
    <PageShell currentPath="/methods">
      <SectionPanel
        title="方法列表"
        eyebrow="方法库"
        description="平台提供可浏览的研究方法列表，帮助用户了解每种方法的用途和输入要求。当前页面直接读取内置方法目录，可静态导出到 GitHub Pages。"
      >
        <div className="flex flex-wrap items-center gap-3">
          {filterOptions.map((option) => {
            const active = option.value === selectedCategory;

            return (
              <Link
                key={option.value}
                href={getFilterHref(option.value)}
                className={`rounded-full px-4 py-2 text-sm transition ${
                  active
                    ? "bg-[var(--ink-950)] text-white"
                    : "border border-[rgba(32,25,20,0.1)] bg-[var(--surface-0)] text-[var(--ink-700)] hover:border-[rgba(32,25,20,0.18)]"
                }`}
              >
                {option.label}
              </Link>
            );
          })}
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-3">
          {filteredMethods.map((method) => (
            <MethodCard key={method.slug} method={method} />
          ))}
        </div>
      </SectionPanel>
    </PageShell>
  );
}
