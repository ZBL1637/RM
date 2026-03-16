from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MethodCategory = Literal["quantitative", "configurational"]
FieldType = Literal["string", "integer", "number", "boolean", "category", "date", "set_membership"]
ResultBlockType = Literal["summary", "table", "chart", "text", "download"]
AnalysisDifficulty = Literal["低", "中", "高"]


class MethodFieldConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: float | None = None
    max: float | None = None
    allowed_values: list[str] | None = None


class MethodFieldSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    label: str
    type: FieldType
    required: bool
    role: str
    allow_missing: bool = False
    constraints: MethodFieldConstraints | None = None
    description: str


class MethodInputSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    spec_version: str = "1.0"
    accepted_file_types: list[Literal["csv", "xlsx"]]
    min_sample_size: int | None = None
    fields: list[MethodFieldSpec]


class MethodResultBlockSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    type: ResultBlockType
    title: str
    required: bool


class MethodOutputSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    result_blocks: list[MethodResultBlockSpec]


class MethodSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    name: str
    category: MethodCategory
    description: str
    applicable_scenarios: list[str]
    data_type_label: str
    analysis_difficulty: AnalysisDifficulty
    sample_requirement: str
    is_recommended: bool = False


class MethodDetail(MethodSummary):
    input_spec_json: MethodInputSpec
    output_spec_json: MethodOutputSpec
    template_file_url: str | None = None
    sample_file_url: str | None = None
    prerequisites: list[str] = Field(default_factory=list)
    common_errors: list[str] = Field(default_factory=list)
    is_active: bool = True
    display_order: int = 0
    created_at: str
    updated_at: str
