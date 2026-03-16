type DetailSectionProps = {
  title: string;
  description?: string;
  items?: string[];
  children?: React.ReactNode;
};

export function DetailSection({ title, description, items, children }: DetailSectionProps) {
  return (
    <section className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white/80 p-6">
      <h3 className="font-display text-xl text-[var(--ink-950)]">{title}</h3>
      {description ? <p className="mt-3 text-sm leading-7 text-[var(--ink-700)]">{description}</p> : null}
      {items && items.length > 0 ? (
        <ul className="mt-4 space-y-3 text-sm leading-7 text-[var(--ink-700)]">
          {items.map((item) => (
            <li key={item} className="rounded-2xl bg-[var(--surface-0)] px-4 py-3">
              {item}
            </li>
          ))}
        </ul>
      ) : null}
      {children ? <div className="mt-4">{children}</div> : null}
    </section>
  );
}
