import Link from "next/link";

type PageShellProps = {
  children: React.ReactNode;
  currentPath: "/" | "/methods";
};

const navItems = [
  { href: "/" as const, label: "首页" },
  { href: "/methods" as const, label: "方法库" },
];

export function PageShell({ children, currentPath }: PageShellProps) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-[rgba(32,25,20,0.08)] bg-white/78 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5 sm:px-8 lg:px-12">
          <div>
            <Link href="/" className="text-sm font-semibold tracking-[0.2em] text-[var(--ink-950)] uppercase">
              研究方法自动分析平台
            </Link>
            <p className="mt-2 text-sm text-[var(--ink-700)]">
              研究方法导航 + 数据格式校验 + 自动分析 + 结果解释
            </p>
          </div>

          <nav className="flex items-center gap-3 text-sm">
            {navItems.map((item) => {
              const active = item.href === currentPath;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-full px-4 py-2 transition ${
                    active
                      ? "bg-[var(--ink-950)] text-white"
                      : "border border-[rgba(32,25,20,0.08)] bg-white/88 text-[var(--ink-700)] hover:border-[rgba(32,25,20,0.18)]"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col px-6 py-10 sm:px-8 lg:px-12">{children}</main>
    </div>
  );
}
