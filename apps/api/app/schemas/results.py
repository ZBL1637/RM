from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class AnalysisSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    highlights: list[str]


class AnalysisTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    columns: list[str]
    rows: list[list[str | int | float | None]]


class AnalysisChartData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    labels: list[str]
    values: list[float]


class AnalysisChart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    title: str
    type: Literal["bar"]
    data: AnalysisChartData


class AnalysisInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plain_language: str
    academic_style: str


class AnalysisResultPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str
    method_slug: str
    status: Literal["success"]
    result_version: str = "1.0"
    generated_at: str
    summary: AnalysisSummary
    tables: list[AnalysisTable]
    charts: list[AnalysisChart]
    interpretation: AnalysisInterpretation
    report_payload: dict[str, Any]


class AnalysisResultRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    task_id: str
    method_slug: str
    result_json: AnalysisResultPayload
    summary_text: str | None = None
    created_at: str
