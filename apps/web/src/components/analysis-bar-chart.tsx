import type { AnalysisChart } from "@/types/analysis";

type AnalysisBarChartProps = {
  chart: AnalysisChart;
};

export function AnalysisBarChart({ chart }: AnalysisBarChartProps) {
  const maxAbsValue = Math.max(...chart.data.values.map((value) => Math.abs(value)), 1);

  return (
    <section className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-6">
      <h3 className="font-display text-xl text-[var(--ink-950)]">{chart.title}</h3>
      <div className="mt-5 space-y-4">
        {chart.data.labels.map((label, index) => {
          const value = chart.data.values[index] ?? 0;
          const width = `${(Math.abs(value) / maxAbsValue) * 100}%`;
          const toneClass = value < 0 ? "bg-[var(--accent-700)]" : "bg-[var(--teal-700)]";

          return (
            <div key={`${chart.key}-${label}`} className="space-y-2">
              <div className="flex items-center justify-between gap-4 text-sm">
                <span className="font-medium text-[var(--ink-950)]">{label}</span>
                <span className="text-[var(--ink-700)]">{value.toFixed(2)}</span>
              </div>
              <div className="h-3 rounded-full bg-[var(--surface-0)]">
                <div className={`h-3 rounded-full ${toneClass}`} style={{ width }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
