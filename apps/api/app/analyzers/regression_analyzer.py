from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
from scipy.stats import f as f_distribution
from scipy.stats import t as t_distribution

from app.core.errors import ServiceError
from app.core.tabular import is_blank, is_numeric, normalize_header, read_tabular_file, to_float, trim_blank_rows
from app.schemas.results import (
    AnalysisChart,
    AnalysisChartData,
    AnalysisInterpretation,
    AnalysisResultPayload,
    AnalysisSummary,
    AnalysisTable,
)


def analyze_regression(task_id: str, file_path: str, file_type: str) -> AnalysisResultPayload:
    headers, rows = read_tabular_file(file_path, file_type)
    normalized_headers = [normalize_header(value) for value in headers]
    data_rows = trim_blank_rows(rows)

    if "outcome" not in normalized_headers:
        raise ServiceError(
            status_code=400,
            message="回归分析缺少因变量列 `outcome`，请按模板整理数据后重试。",
            error_code="MISSING_REQUIRED_COLUMN",
            details={"field": "outcome"},
        )

    predictor_names = [header for header in normalized_headers if header.startswith("predictor_")]
    control_names = [header for header in normalized_headers if header.startswith("control_")]
    variable_names = [*predictor_names, *control_names]
    if not variable_names:
        raise ServiceError(
            status_code=400,
            message="回归分析至少需要 1 个自变量列，列名应以 `predictor_` 开头。",
            error_code="MISSING_REQUIRED_COLUMN",
            details={"field": "predictors"},
        )

    relevant_columns = ["outcome", *variable_names]
    column_indexes = {header: normalized_headers.index(header) for header in relevant_columns}

    outcome_values: list[float] = []
    design_rows: list[list[float]] = []

    for row in data_rows:
        candidate_values: list[float] = []
        valid_row = True

        for header in relevant_columns:
            index = column_indexes[header]
            value = row[index] if index < len(row) else None
            if is_blank(value) or not is_numeric(value):
                valid_row = False
                break
            candidate_values.append(to_float(value))

        if not valid_row:
            continue

        outcome_values.append(candidate_values[0])
        design_rows.append(candidate_values[1:])

    sample_size = len(outcome_values)
    parameter_count = len(variable_names) + 1
    if sample_size <= parameter_count:
        raise ServiceError(
            status_code=400,
            message="完整样本不足以估计当前回归模型，请减少变量或补充样本后重试。",
            error_code="METHOD_PRECONDITION_FAILED",
            details={"sample_size": sample_size, "parameter_count": parameter_count},
        )

    y = np.asarray(outcome_values, dtype=float)
    x = np.asarray(design_rows, dtype=float)
    design_matrix = np.column_stack([np.ones(sample_size), x])

    if np.linalg.matrix_rank(design_matrix) < design_matrix.shape[1]:
        raise ServiceError(
            status_code=400,
            message="自变量之间可能存在完全共线或固定不变的字段，当前模型无法稳定估计。",
            error_code="METHOD_PRECONDITION_FAILED",
            details={"variables": variable_names},
        )

    coefficients, _, _, _ = np.linalg.lstsq(design_matrix, y, rcond=None)
    fitted = design_matrix @ coefficients
    residuals = y - fitted

    sse = float(np.sum(residuals**2))
    sst = float(np.sum((y - float(np.mean(y))) ** 2))
    ssr = float(max(sst - sse, 0.0))
    df_model = len(variable_names)
    df_resid = sample_size - parameter_count

    mse = sse / df_resid
    xtx_inv = np.linalg.inv(design_matrix.T @ design_matrix)
    standard_errors = np.sqrt(np.diag(mse * xtx_inv))
    t_values = coefficients / standard_errors
    p_values = 2 * (1 - t_distribution.cdf(np.abs(t_values), df=df_resid))

    r_squared = 1 - (sse / sst) if sst > 0 else 0.0
    adjusted_r_squared = 1 - ((1 - r_squared) * (sample_size - 1) / df_resid) if df_resid > 0 else r_squared
    f_statistic = (ssr / df_model) / (sse / df_resid) if df_model > 0 and sse > 0 else 0.0
    model_p_value = 1 - f_distribution.cdf(f_statistic, df_model, df_resid) if df_model > 0 else 1.0

    variable_labels = ["intercept", *variable_names]
    coefficient_rows: list[list[str | int | float | None]] = []
    strongest_variable: tuple[str, float, float] | None = None

    for variable, coefficient, std_error, t_value, p_value in zip(
        variable_labels,
        coefficients.tolist(),
        standard_errors.tolist(),
        t_values.tolist(),
        p_values.tolist(),
        strict=True,
    ):
        significant = "yes" if p_value < 0.05 else "no"
        rounded_coefficient = round(float(coefficient), 4)
        rounded_p = round(float(p_value), 4)
        coefficient_rows.append(
            [
                variable,
                rounded_coefficient,
                round(float(std_error), 4),
                round(float(t_value), 4),
                rounded_p,
                significant,
            ]
        )

        if variable == "intercept":
            continue

        if strongest_variable is None or abs(rounded_coefficient) > abs(strongest_variable[1]):
            strongest_variable = (variable, rounded_coefficient, rounded_p)

    model_summary_rows = [
        ["sample_size", sample_size],
        ["predictor_count", len(predictor_names)],
        ["control_count", len(control_names)],
        ["r_squared", round(float(r_squared), 4)],
        ["adjusted_r_squared", round(float(adjusted_r_squared), 4)],
    ]
    fit_rows = [
        ["f_statistic", round(float(f_statistic), 4)],
        ["model_p_value", round(float(model_p_value), 4)],
        ["residual_df", df_resid],
    ]

    coefficient_chart_labels = [row[0] for row in coefficient_rows if row[0] != "intercept"]
    coefficient_chart_values = [float(row[1]) for row in coefficient_rows if row[0] != "intercept"]

    highlights = [
        f"回归模型基于 {sample_size} 个完整样本完成估计。",
        f"模型的 R² 为 {r_squared:.3f}，调整后 R² 为 {adjusted_r_squared:.3f}。",
    ]
    if model_p_value < 0.05:
        highlights.append(f"模型整体显著（F = {f_statistic:.2f}, p = {_format_p_value(model_p_value)}）。")
    else:
        highlights.append(f"模型整体未达到常用显著性水平（p = {_format_p_value(model_p_value)}）。")

    if strongest_variable is not None:
        variable_name, coefficient_value, p_value = strongest_variable
        direction = "正向" if coefficient_value >= 0 else "负向"
        significance = "达到显著" if p_value < 0.05 else "未达到显著"
        highlights.append(f"{variable_name} 的回归系数绝对值最大，呈 {direction} 影响，且{significance}。")

    significant_variables = [
        row for row in coefficient_rows if row[0] != "intercept" and isinstance(row[4], float) and row[4] < 0.05
    ]

    if significant_variables:
        effect_parts = []
        for row in significant_variables[:3]:
            direction = "正向" if float(row[1]) >= 0 else "负向"
            effect_parts.append(f"{row[0]} 对 outcome 呈{direction}影响（p = {_format_p_value(float(row[4]))}）")
        effect_text = "；".join(effect_parts)
    else:
        effect_text = "当前模型中未检测到达到常用显著性水平的自变量。"

    plain_language = (
        f"本次回归分析使用了 {sample_size} 个完整样本。模型可以解释 outcome 约 {r_squared:.1%} 的变异。"
        f"{effect_text}"
    )
    academic_style = (
        f"回归结果显示，模型整体 {'显著' if model_p_value < 0.05 else '未显著'}，"
        f"F({df_model}, {df_resid}) = {f_statistic:.2f}, p {('= ' + _format_p_value(model_p_value)) if model_p_value >= 0.001 else '< 0.001'}，"
        f"R² = {r_squared:.3f}，调整后 R² = {adjusted_r_squared:.3f}。{effect_text}"
    )

    return AnalysisResultPayload(
        task_id=task_id,
        method_slug="regression",
        status="success",
        generated_at=_utc_now(),
        summary=AnalysisSummary(title="回归分析完成", highlights=highlights),
        tables=[
            AnalysisTable(
                key="model_summary",
                title="模型摘要",
                columns=["metric", "value"],
                rows=model_summary_rows,
            ),
            AnalysisTable(
                key="coefficients",
                title="系数表",
                columns=["variable", "coef", "std_err", "t_value", "p_value", "significant"],
                rows=coefficient_rows,
            ),
            AnalysisTable(
                key="fit_statistics",
                title="拟合统计",
                columns=["metric", "value"],
                rows=fit_rows,
            ),
        ],
        charts=[
            AnalysisChart(
                key="coefficient_chart",
                title="回归系数图",
                type="bar",
                data=AnalysisChartData(labels=coefficient_chart_labels, values=coefficient_chart_values),
            )
        ],
        interpretation=AnalysisInterpretation(
            plain_language=plain_language,
            academic_style=academic_style,
        ),
        report_payload={
            "sample_size": sample_size,
            "outcome": "outcome",
            "predictors": predictor_names,
            "controls": control_names,
            "r_squared": round(float(r_squared), 4),
            "adjusted_r_squared": round(float(adjusted_r_squared), 4),
            "model_p_value": round(float(model_p_value), 4),
        },
    )


def _format_p_value(value: float) -> str:
    if value < 0.001:
        return "< 0.001"
    return f"{value:.3f}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
