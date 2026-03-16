import Link from "next/link";

import { PageShell } from "@/components/page-shell";

export default function NotFound() {
  return (
    <PageShell currentPath="/">
      <section className="flex min-h-[60vh] flex-col items-start justify-center rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)]">
        <p className="section-label text-xs font-semibold text-[var(--accent-700)]">页面不存在</p>
        <h1 className="mt-4 font-display text-4xl text-[var(--ink-950)] sm:text-5xl">没有找到对应的方法页面</h1>
        <p className="mt-4 max-w-2xl text-base leading-8 text-[var(--ink-700)]">
          你访问的页面不在当前方法浏览范围内。可以返回首页，或前往方法列表页继续查看已纳入 MVP 的方法。
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/"
            className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-5 py-3 text-sm font-medium text-white"
          >
            返回首页
          </Link>
          <Link
            href="/methods"
            className="inline-flex items-center justify-center rounded-full border border-[rgba(32,25,20,0.12)] px-5 py-3 text-sm font-medium text-[var(--ink-700)]"
          >
            查看方法列表
          </Link>
        </div>
      </section>
    </PageShell>
  );
}
