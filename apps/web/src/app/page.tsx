import Link from "next/link";

import { MethodCard } from "@/components/method-card";
import { PageShell } from "@/components/page-shell";
import { SectionPanel } from "@/components/section-panel";
import { getFeaturedMethods } from "@/lib/methods";

const workflowSteps = [
  "方法浏览",
  "方法选择",
  "模板下载",
  "数据上传",
  "数据校验",
  "自动分析",
  "结果展示",
  "报告导出",
];

const valuePoints = [
  "帮助用户浏览和了解研究方法。",
  "帮助用户判断某个方法是否适合自己的研究问题。",
  "帮助用户完成上传、校验、分析与导出的最小闭环。",
];

export default async function Home() {
  const featuredMethods = await getFeaturedMethods();

  return (
    <PageShell currentPath="/">
      <section className="rounded-[32px] border border-[rgba(32,25,20,0.08)] bg-white/84 p-8 shadow-[0_22px_56px_rgba(77,50,23,0.08)] sm:p-10">
        <p className="section-label text-xs font-semibold text-[var(--accent-700)]">平台定位</p>
        <h1 className="mt-4 max-w-4xl font-display text-4xl leading-tight text-[var(--ink-950)] sm:text-5xl">
          面向科研用户的研究方法导航与自动分析平台
        </h1>
        <p className="mt-5 max-w-4xl text-base leading-8 text-[var(--ink-700)]">
          本平台是一个研究方法导航、数据格式校验、自动分析、结果解释的一体化平台。平台不替代研究者的理论判断、
          变量设计和研究结论归纳，而是将标准化、规则清晰、可程序化的方法分析流程进行产品化。
        </p>

        <div className="mt-8 flex flex-wrap items-center gap-3">
          <Link
            href="/methods"
            className="inline-flex items-center justify-center rounded-full bg-[var(--ink-950)] px-5 py-3 text-sm font-medium text-white transition hover:bg-[var(--ink-900)]"
          >
            浏览研究方法
          </Link>
          <span className="rounded-full border border-[rgba(32,25,20,0.1)] px-4 py-3 text-sm text-[var(--ink-700)]">
            当前页面基于静态方法目录构建，可直接发布到 GitHub Pages
          </span>
        </div>
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
        <SectionPanel
          title="MVP 核心闭环"
          eyebrow="产品目标"
          description="MVP 优先保障稳定可用的核心链路，先跑通方法浏览到报告导出的完整流程。"
        >
          <div className="flex flex-wrap gap-2">
            {workflowSteps.map((step) => (
              <span
                key={step}
                className="rounded-full border border-[rgba(32,25,20,0.08)] bg-[var(--surface-0)] px-4 py-2 text-sm text-[var(--ink-700)]"
              >
                {step}
              </span>
            ))}
          </div>
        </SectionPanel>

        <SectionPanel
          title="当前页面承担的角色"
          eyebrow="范围说明"
          description="当前 MVP 已接通方法浏览、上传校验、真实分析、结果页和导出入口，首页承担统一入口与能力概览的角色。"
        >
          <ul className="space-y-3 text-sm leading-7 text-[var(--ink-700)]">
            {valuePoints.map((point) => (
              <li key={point} className="rounded-2xl bg-[var(--surface-0)] px-4 py-3">
                {point}
              </li>
            ))}
          </ul>
        </SectionPanel>
      </section>

      <section className="mt-10">
        <SectionPanel
          title="首批方法"
          eyebrow="方法库"
          description="当前首页直接读取首批方法静态数据，方法详情页会继续展示适用场景、输入要求、样本要求和输出说明。"
        >
          <div className="grid gap-5 lg:grid-cols-3">
            {featuredMethods.map((method) => (
              <MethodCard key={method.slug} method={method} />
            ))}
          </div>
        </SectionPanel>
      </section>
    </PageShell>
  );
}
