import type { AnalysisTable } from "@/types/analysis";

type AnalysisResultTableProps = {
  table: AnalysisTable;
};

function formatCellValue(value: string | number | null) {
  if (value === null) {
    return "-";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4).replace(/\.?0+$/, "");
  }
  return value;
}

export function AnalysisResultTable({ table }: AnalysisResultTableProps) {
  return (
    <section className="rounded-[24px] border border-[rgba(32,25,20,0.08)] bg-white/82 p-6">
      <h3 className="font-display text-xl text-[var(--ink-950)]">{table.title}</h3>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-0 text-left text-sm text-[var(--ink-700)]">
          <thead>
            <tr>
              {table.columns.map((column) => (
                <th
                  key={column}
                  className="border-b border-[rgba(32,25,20,0.08)] px-3 py-3 font-medium text-[var(--ink-950)]"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr key={`${table.key}-${rowIndex}`}>
                {row.map((cell, cellIndex) => (
                  <td key={`${table.key}-${rowIndex}-${cellIndex}`} className="border-b border-[rgba(32,25,20,0.06)] px-3 py-3">
                    {formatCellValue(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
