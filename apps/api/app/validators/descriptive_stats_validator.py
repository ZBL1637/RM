from __future__ import annotations

from collections import Counter

from app.core.tabular import is_blank, is_numeric, normalize_header, read_tabular_file, trim_blank_rows
from app.schemas.validation import (
    ValidationIssue,
    ValidationReportPayload,
    ValidationStats,
    ValidationSummary,
)
from app.validators.tabular_rules import build_header_issues


def validate_descriptive_stats_file(file_path: str, file_type: str) -> ValidationReportPayload:
    headers, rows = read_tabular_file(file_path, file_type)
    normalized_headers = [normalize_header(value) for value in headers]
    data_rows = trim_blank_rows(rows)

    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []

    if not normalized_headers or all(not header for header in normalized_headers):
        errors.append(
            ValidationIssue(
                code="MISSING_REQUIRED_COLUMN",
                level="error",
                field="variables",
                message="至少需要 1 个字段，当前未检测到有效列名。",
                suggestion="请将第一行设置为列名，并至少保留 1 个字段。",
            )
        )

    errors.extend(build_header_issues(normalized_headers))

    if not data_rows:
        errors.append(
            ValidationIssue(
                code="METHOD_PRECONDITION_FAILED",
                level="error",
                field="variables",
                message="未检测到可分析的数据行。",
                suggestion="请至少保留 1 行有效数据后再进行校验。",
            )
        )

    numeric_column_count = 0
    categorical_column_count = 0
    missing_cells = 0
    analyzed_column_count = len([header for header in normalized_headers if header])

    for index, header in enumerate(normalized_headers):
        if not header:
            continue

        column_values = [row[index] if index < len(row) else None for row in data_rows]
        non_empty_values = [value for value in column_values if not is_blank(value)]
        missing_cells += len(column_values) - len(non_empty_values)

        if not non_empty_values:
            warnings.append(
                ValidationIssue(
                    code="TOO_MANY_MISSING_VALUES",
                    level="warning",
                    field=header,
                    message=f"列 `{header}` 当前没有有效值。",
                    suggestion="请检查该列是否应保留，或补充有效数据。",
                )
            )
            categorical_column_count += 1
            continue

        numeric_like = sum(1 for value in non_empty_values if is_numeric(value))
        text_like = len(non_empty_values) - numeric_like

        if numeric_like and text_like:
            warnings.append(
                ValidationIssue(
                    code="UNEXPECTED_COLUMN_TYPE",
                    level="warning",
                    field=header,
                    message=f"列 `{header}` 同时包含数值和文本，统计结果可能不稳定。",
                    suggestion="建议将该列统一为数值型或分类型后重新上传。",
                )
            )

        if text_like == 0:
            numeric_column_count += 1
        else:
            categorical_column_count += 1

    total_cells = len(data_rows) * analyzed_column_count
    missing_ratio = round(missing_cells / total_cells, 4) if total_cells > 0 else 0.0

    if missing_ratio > 0.2:
        warnings.append(
            ValidationIssue(
                code="TOO_MANY_MISSING_VALUES",
                level="warning",
                field="variables",
                message=f"当前缺失值比例为 {missing_ratio:.2%}，可能影响统计解释。",
                suggestion="建议先补齐关键缺失值，再开始分析。",
            )
        )

    if len(data_rows) < 3:
        warnings.append(
            ValidationIssue(
                code="INSUFFICIENT_SAMPLE_SIZE",
                level="warning",
                field="variables",
                message=f"当前样本量为 {len(data_rows)}，描述统计结果的稳定性可能有限。",
                suggestion="如条件允许，建议补充更多样本后再分析。",
            )
        )

    summary = ValidationSummary(
        error_count=len(errors),
        warning_count=len(warnings),
    )
    stats = ValidationStats(
        row_count=len(data_rows),
        column_count=analyzed_column_count,
        missing_ratio=missing_ratio,
        numeric_column_count=numeric_column_count,
        categorical_column_count=categorical_column_count,
    )

    return ValidationReportPayload(
        passed=len(errors) == 0,
        summary=summary,
        errors=errors,
        warnings=warnings,
        stats=stats,
    )
