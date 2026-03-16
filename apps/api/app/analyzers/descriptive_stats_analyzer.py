from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import mean, median, stdev

from app.core.tabular import is_blank, is_numeric, normalize_header, read_tabular_file, to_float, trim_blank_rows
from app.schemas.results import (
    AnalysisChart,
    AnalysisChartData,
    AnalysisInterpretation,
    AnalysisResultPayload,
    AnalysisSummary,
    AnalysisTable,
)


def analyze_descriptive_stats(task_id: str, file_path: str, file_type: str) -> AnalysisResultPayload:
    headers, rows = read_tabular_file(file_path, file_type)
    normalized_headers = [normalize_header(value) for value in headers]
    data_rows = trim_blank_rows(rows)

    numeric_rows: list[list[str | int | float | None]] = []
    categorical_rows: list[list[str | int | float | None]] = []
    mean_chart_labels: list[str] = []
    mean_chart_values: list[float] = []
    categorical_chart_labels: list[str] = []
    categorical_chart_values: list[float] = []

    top_numeric_variable: tuple[str, float] | None = None
    top_category_item: tuple[str, str, float] | None = None

    for index, header in enumerate(normalized_headers):
        if not header:
            continue

        column_values = [row[index] if index < len(row) else None for row in data_rows]
        non_empty_values = [value for value in column_values if not is_blank(value)]
        missing_count = len(column_values) - len(non_empty_values)

        if not non_empty_values:
            continue

        all_numeric = all(is_numeric(value) for value in non_empty_values)

        if all_numeric:
            numeric_values = [to_float(value) for value in non_empty_values]
            variable_mean = round(mean(numeric_values), 4)
            variable_median = round(median(numeric_values), 4)
            variable_std = round(stdev(numeric_values), 4) if len(numeric_values) > 1 else 0.0
            variable_min = round(min(numeric_values), 4)
            variable_max = round(max(numeric_values), 4)

            numeric_rows.append(
                [
                    header,
                    len(numeric_values),
                    variable_mean,
                    variable_median,
                    variable_std,
                    variable_min,
                    variable_max,
                    missing_count,
                ]
            )
            mean_chart_labels.append(header)
            mean_chart_values.append(variable_mean)

            if top_numeric_variable is None or variable_mean > top_numeric_variable[1]:
                top_numeric_variable = (header, variable_mean)
            continue

        counts = Counter(str(value).strip() for value in non_empty_values)
        total_count = sum(counts.values())
        sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

        for category_value, category_count in sorted_items:
            proportion = round(category_count / total_count, 4)
            categorical_rows.append([header, category_value, category_count, proportion])

        if sorted_items:
            first_category, first_count = sorted_items[0]
            first_proportion = round(first_count / total_count, 4)
            if top_category_item is None or first_proportion > top_category_item[2]:
                top_category_item = (header, first_category, first_proportion)

            if not categorical_chart_labels:
                categorical_chart_labels = [category for category, _ in sorted_items]
                categorical_chart_values = [float(count) for _, count in sorted_items]

    tables: list[AnalysisTable] = []
    if numeric_rows:
        tables.append(
            AnalysisTable(
                key="numeric_summary",
                title="数值变量描述统计表",
                columns=["variable", "count", "mean", "median", "std_dev", "min", "max", "missing_count"],
                rows=numeric_rows,
            )
        )
    if categorical_rows:
        tables.append(
            AnalysisTable(
                key="categorical_frequency",
                title="分类变量频数与比例表",
                columns=["variable", "category", "count", "proportion"],
                rows=categorical_rows,
            )
        )

    charts: list[AnalysisChart] = []
    if mean_chart_labels:
        charts.append(
            AnalysisChart(
                key="numeric_means",
                title="数值变量均值图",
                type="bar",
                data=AnalysisChartData(labels=mean_chart_labels, values=mean_chart_values),
            )
        )
    elif categorical_chart_labels:
        charts.append(
            AnalysisChart(
                key="categorical_distribution",
                title="分类变量频数图",
                type="bar",
                data=AnalysisChartData(labels=categorical_chart_labels, values=categorical_chart_values),
            )
        )

    highlights = [
        f"共完成 {len(data_rows)} 行样本、{len([header for header in normalized_headers if header])} 个字段的描述统计。",
    ]
    if numeric_rows and top_numeric_variable is not None:
        highlights.append(f"数值变量中，{top_numeric_variable[0]} 的均值最高，为 {top_numeric_variable[1]:.2f}。")
    if categorical_rows and top_category_item is not None:
        highlights.append(
            f"分类变量中，{top_category_item[0]} 的 `{top_category_item[1]}` 最常见，占比 {top_category_item[2]:.1%}。"
        )

    plain_language_parts = [f"本次描述统计共处理 {len(data_rows)} 行样本。"]
    academic_parts = [f"描述统计结果显示，样本共包含 {len(data_rows)} 个观测值。"]

    if numeric_rows:
        first_numeric = numeric_rows[0]
        plain_language_parts.append(
            f"数值变量 {first_numeric[0]} 的平均值为 {float(first_numeric[2]):.2f}，标准差为 {float(first_numeric[4]):.2f}。"
        )
        academic_parts.append(
            f"数值变量 {first_numeric[0]} 的均值为 {float(first_numeric[2]):.2f}，标准差为 {float(first_numeric[4]):.2f}。"
        )
    if categorical_rows:
        first_categorical = categorical_rows[0]
        plain_language_parts.append(
            f"分类变量 {first_categorical[0]} 中，{first_categorical[1]} 最常见，占比 {float(first_categorical[3]):.1%}。"
        )
        academic_parts.append(
            f"分类变量 {first_categorical[0]} 中，{first_categorical[1]} 的频数最高，占比 {float(first_categorical[3]):.1%}。"
        )

    generated_at = _utc_now()
    return AnalysisResultPayload(
        task_id=task_id,
        method_slug="descriptive_stats",
        status="success",
        generated_at=generated_at,
        summary=AnalysisSummary(title="描述统计完成", highlights=highlights),
        tables=tables,
        charts=charts,
        interpretation=AnalysisInterpretation(
            plain_language="".join(plain_language_parts),
            academic_style="".join(academic_parts),
        ),
        report_payload={
            "row_count": len(data_rows),
            "column_count": len([header for header in normalized_headers if header]),
            "table_keys": [table.key for table in tables],
            "chart_keys": [chart.key for chart in charts],
        },
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
