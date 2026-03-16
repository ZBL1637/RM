from __future__ import annotations

from statistics import variance

from app.core.tabular import is_blank, is_numeric, normalize_header, read_tabular_file, to_float, trim_blank_rows
from app.schemas.validation import (
    ValidationIssue,
    ValidationReportPayload,
    ValidationStats,
    ValidationSummary,
)
from app.validators.tabular_rules import build_header_issues


def validate_regression_file(file_path: str, file_type: str) -> ValidationReportPayload:
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
                field="outcome",
                message="回归分析至少需要有效列名，并包含 `outcome` 列。",
                suggestion="请将第一行设置为列名，并提供 `outcome` 与至少 1 个 `predictor_*` 列。",
            )
        )
    else:
        errors.extend(build_header_issues(normalized_headers))

    if not data_rows:
        errors.append(
            ValidationIssue(
                code="METHOD_PRECONDITION_FAILED",
                level="error",
                field="outcome",
                message="未检测到可分析的数据行。",
                suggestion="请至少保留 1 行有效数据后再进行校验。",
            )
        )

    outcome_name = "outcome"
    predictor_names = [header for header in normalized_headers if header.startswith("predictor_")]
    control_names = [header for header in normalized_headers if header.startswith("control_")]

    if outcome_name not in normalized_headers:
        errors.append(
            ValidationIssue(
                code="MISSING_REQUIRED_COLUMN",
                level="error",
                field="outcome",
                message="缺少因变量列 `outcome`。",
                suggestion="请将因变量列命名为 `outcome`，并放在上传文件中。",
            )
        )

    if not predictor_names:
        errors.append(
            ValidationIssue(
                code="MISSING_REQUIRED_COLUMN",
                level="error",
                field="predictors",
                message="至少需要 1 个自变量列，列名应以 `predictor_` 开头。",
                suggestion="请至少提供 1 列自变量，并使用如 `predictor_income` 的列名格式。",
            )
        )

    missing_cells = 0
    analyzed_columns = [header for header in normalized_headers if header]
    numeric_column_count = 0

    role_columns = [header for header in [outcome_name, *predictor_names, *control_names] if header in normalized_headers]
    complete_case_count = 0

    if role_columns and data_rows:
        role_indexes = {header: normalized_headers.index(header) for header in role_columns}

        for header in role_columns:
            index = role_indexes[header]
            column_values = [row[index] if index < len(row) else None for row in data_rows]
            non_empty_values = [value for value in column_values if not is_blank(value)]
            missing_count = len(column_values) - len(non_empty_values)
            missing_cells += missing_count

            if not non_empty_values:
                errors.append(
                    ValidationIssue(
                        code="MISSING_REQUIRED_COLUMN",
                        level="error",
                        field=header,
                        message=f"列 `{header}` 没有有效数据，无法用于回归分析。",
                        suggestion="请补充该列的数值型数据后再重新上传。",
                    )
                )
                continue

            if not all(is_numeric(value) for value in non_empty_values):
                errors.append(
                    ValidationIssue(
                        code="UNEXPECTED_COLUMN_TYPE",
                        level="error",
                        field=header,
                        message=f"列 `{header}` 应为数值型，但检测到文本或无法识别的值。",
                        suggestion="请将该列统一转换为数值型后再重新上传。",
                    )
                )
                continue

            numeric_column_count += 1
            numeric_values = [to_float(value) for value in non_empty_values]
            if len(numeric_values) > 1 and variance(numeric_values) == 0:
                errors.append(
                    ValidationIssue(
                        code="METHOD_PRECONDITION_FAILED",
                        level="error",
                        field=header,
                        message=f"列 `{header}` 没有有效变异，无法用于回归分析。",
                        suggestion="请更换该变量，或确认该列是否录入为同一个固定值。",
                    )
                )

            if missing_count > 0:
                warnings.append(
                    ValidationIssue(
                        code="TOO_MANY_MISSING_VALUES",
                        level="warning",
                        field=header,
                        message=f"列 `{header}` 存在 {missing_count} 个缺失值，分析时会自动跳过不完整样本。",
                        suggestion="建议先补齐关键缺失值，以减少回归分析中被剔除的样本。",
                    )
                )

        for row in data_rows:
            values = []
            valid_row = True
            for header in role_columns:
                index = role_indexes[header]
                value = row[index] if index < len(row) else None
                if is_blank(value) or not is_numeric(value):
                    valid_row = False
                    break
                values.append(value)
            if valid_row and values:
                complete_case_count += 1

        parameter_count = 1 + len(predictor_names) + len(control_names)
        if complete_case_count <= parameter_count:
            errors.append(
                ValidationIssue(
                    code="METHOD_PRECONDITION_FAILED",
                    level="error",
                    field="predictors",
                    message=f"可用于回归分析的完整样本仅有 {complete_case_count} 行，不足以估计当前模型。",
                    suggestion="请减少自变量数量，或补充更多完整样本后再分析。",
                )
            )
        elif complete_case_count < 30:
            warnings.append(
                ValidationIssue(
                    code="INSUFFICIENT_SAMPLE_SIZE",
                    level="warning",
                    field="predictors",
                    message=f"当前可用于回归分析的完整样本为 {complete_case_count} 行，低于建议样本量 30。",
                    suggestion="如条件允许，建议补充更多样本后再进行回归分析。",
                )
            )

    total_cells = len(data_rows) * len(analyzed_columns)
    missing_ratio = round(missing_cells / total_cells, 4) if total_cells > 0 else 0.0

    return ValidationReportPayload(
        passed=len(errors) == 0,
        summary=ValidationSummary(error_count=len(errors), warning_count=len(warnings)),
        errors=errors,
        warnings=warnings,
        stats=ValidationStats(
            row_count=len(data_rows),
            column_count=len(analyzed_columns),
            missing_ratio=missing_ratio,
            numeric_column_count=numeric_column_count,
            categorical_column_count=max(len(analyzed_columns) - numeric_column_count, 0),
        ),
    )
