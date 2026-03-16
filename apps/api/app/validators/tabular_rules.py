from __future__ import annotations

from collections import Counter

from app.schemas.validation import ValidationIssue


def build_header_issues(normalized_headers: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    duplicate_headers = [
        header for header, count in Counter(header for header in normalized_headers if header).items() if count > 1
    ]
    for duplicate in duplicate_headers:
        issues.append(
            ValidationIssue(
                code="DUPLICATE_COLUMN_NAME",
                level="error",
                field=duplicate,
                message=f"列名 `{duplicate}` 重复，系统无法区分字段。",
                suggestion="请确保每一列都有唯一列名后再重新上传。",
            )
        )

    for index, header in enumerate(normalized_headers, start=1):
        if header:
            continue
        issues.append(
            ValidationIssue(
                code="MISSING_REQUIRED_COLUMN",
                level="error",
                field=f"column_{index}",
                message=f"第 {index} 列缺少列名。",
                suggestion="请在模板第一行补充明确的列名。",
            )
        )

    return issues
