type SectionPanelProps = {
  title: string;
  eyebrow?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
};

export function SectionPanel({ title, eyebrow, description, children, className }: SectionPanelProps) {
  return (
    <section
      className={`rounded-[28px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-7 shadow-[0_18px_48px_rgba(77,50,23,0.08)] ${className ?? ""}`}
    >
      {eyebrow ? (
        <p className="section-label text-xs font-semibold text-[var(--accent-700)]">{eyebrow}</p>
      ) : null}
      <h2 className="mt-3 font-display text-2xl text-[var(--ink-950)]">{title}</h2>
      {description ? <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--ink-700)]">{description}</p> : null}
      <div className="mt-6">{children}</div>
    </section>
  );
}
