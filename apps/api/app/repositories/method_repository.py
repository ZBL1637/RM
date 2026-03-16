from __future__ import annotations

from app.schemas.methods import (
    MethodDetail,
    MethodFieldConstraints,
    MethodFieldSpec,
    MethodInputSpec,
    MethodOutputSpec,
    MethodResultBlockSpec,
)


class MethodRepository:
    def __init__(self) -> None:
        self._methods = {method.slug: method for method in STATIC_METHODS}

    def list_active(self) -> list[MethodDetail]:
        methods = sorted(self._methods.values(), key=lambda method: method.display_order)
        return [method.model_copy(deep=True) for method in methods if method.is_active]

    def get_active_by_slug(self, slug: str) -> MethodDetail | None:
        method = self._methods.get(slug)
        if method is None or not method.is_active:
            return None

        return method.model_copy(deep=True)


STATIC_METHODS: tuple[MethodDetail, ...] = (
    MethodDetail(
        id="method_descriptive_stats",
        slug="descriptive_stats",
        name="描述统计",
        category="quantitative",
        description="用于概览样本与变量的整体分布，输出均值、中位数、标准差、最大值、最小值以及频数和比例。",
        applicable_scenarios=[
            "已完成数据收集，想先了解样本和变量的基本分布情况。",
            "需要在论文或报告中呈现基础统计结果。",
            "准备进入相关分析或回归分析前，先做数据概览。",
        ],
        data_type_label="接受常规表格数据，可同时包含数值型字段和分类型字段。",
        analysis_difficulty="低",
        sample_requirement="接受常规表格数据，至少 1 个字段。",
        is_recommended=True,
        input_spec_json=MethodInputSpec(
            accepted_file_types=["csv", "xlsx"],
            fields=[
                MethodFieldSpec(
                    name="variables",
                    label="待统计字段",
                    type="number",
                    required=True,
                    role="variables",
                    allow_missing=False,
                    constraints=MethodFieldConstraints(),
                    description="至少 1 列；数值型字段可计算均值、标准差，分类型字段可在同一文件中计算频数和比例。",
                )
            ],
        ),
        output_spec_json=MethodOutputSpec(
            summary="输出结构化基础统计结果，便于用户快速理解样本概况。",
            result_blocks=[
                MethodResultBlockSpec(key="mean", type="table", title="均值", required=True),
                MethodResultBlockSpec(key="median", type="table", title="中位数", required=True),
                MethodResultBlockSpec(key="std", type="table", title="标准差", required=True),
                MethodResultBlockSpec(key="extremes", type="table", title="最大值与最小值", required=True),
                MethodResultBlockSpec(key="frequency", type="table", title="频数与比例", required=True),
            ],
        ),
        template_file_url=None,
        sample_file_url=None,
        prerequisites=[
            "文件格式仅支持 .xlsx 和 .csv。",
            "字段命名应清晰且文件可正常读取。",
        ],
        common_errors=[
            "文件类型不支持",
            "文件无法解析",
        ],
        is_active=True,
        display_order=1,
        created_at="2026-03-14T00:00:00Z",
        updated_at="2026-03-14T00:00:00Z",
    ),
    MethodDetail(
        id="method_regression",
        slug="regression",
        name="回归分析",
        category="quantitative",
        description="分析自变量对因变量的影响。",
        applicable_scenarios=[
            "已经有明确因变量和自变量，想判断影响方向与显著性。",
            "需要输出模型摘要、系数表和拟合优度。",
            "希望将结果整理为论文中的“结果分析”部分。",
        ],
        data_type_label="以数值型字段为主，可包含控制变量。",
        analysis_difficulty="中",
        sample_requirement="样本量建议不少于 30。",
        is_recommended=True,
        input_spec_json=MethodInputSpec(
            accepted_file_types=["csv", "xlsx"],
            min_sample_size=30,
            fields=[
                MethodFieldSpec(
                    name="outcome",
                    label="因变量",
                    type="number",
                    required=True,
                    role="dependent_variable",
                    allow_missing=False,
                    constraints=MethodFieldConstraints(),
                    description="回归分析的因变量。",
                ),
                MethodFieldSpec(
                    name="predictors",
                    label="自变量",
                    type="number",
                    required=True,
                    role="independent_variable",
                    allow_missing=False,
                    constraints=MethodFieldConstraints(),
                    description="至少 1 列，用于解释因变量变化。",
                ),
                MethodFieldSpec(
                    name="controls",
                    label="控制变量",
                    type="number",
                    required=False,
                    role="control_variable",
                    allow_missing=True,
                    constraints=MethodFieldConstraints(),
                    description="可选，用于控制其他影响因素。",
                ),
            ],
        ),
        output_spec_json=MethodOutputSpec(
            summary="输出模型整体表现、变量影响方向与显著性结果。",
            result_blocks=[
                MethodResultBlockSpec(key="model_summary", type="table", title="模型摘要", required=True),
                MethodResultBlockSpec(key="coefficients", type="table", title="系数表", required=True),
                MethodResultBlockSpec(key="significance", type="text", title="显著性结果", required=True),
                MethodResultBlockSpec(key="fit", type="table", title="拟合优度", required=True),
                MethodResultBlockSpec(key="interpretation", type="text", title="结果解释", required=True),
            ],
        ),
        template_file_url=None,
        sample_file_url=None,
        prerequisites=[
            "需包含 1 个因变量和 1 个或多个自变量。",
            "MVP 当前约定因变量列名为 `outcome`，自变量列名以 `predictor_` 开头，可选控制变量列名以 `control_` 开头。",
            "数值型字段优先。",
        ],
        common_errors=[
            "缺少必填字段 outcome",
            "字段类型不匹配",
            "当前样本量低于回归分析建议样本量 30",
            "自变量之间完全共线或字段没有变异",
        ],
        is_active=True,
        display_order=2,
        created_at="2026-03-14T00:00:00Z",
        updated_at="2026-03-14T00:00:00Z",
    ),
    MethodDetail(
        id="method_fsqca",
        slug="fsqca",
        name="fsQCA",
        category="configurational",
        description="用于识别通向结果出现的条件组态，输出必要条件分析、真值表、组态解、一致性与覆盖度。",
        applicable_scenarios=[
            "研究问题关注多重条件如何共同导致某一结果。",
            "已有条件变量与结果变量，想比较不同组态路径。",
            "需要从组态视角解释复杂因果关系。",
        ],
        data_type_label="优先使用已校准数据，字段类型应为集合隶属度。",
        analysis_difficulty="高",
        sample_requirement="至少 1 个结果变量和 1 个或多个条件变量；MVP 优先使用已校准数据。",
        is_recommended=True,
        input_spec_json=MethodInputSpec(
            accepted_file_types=["csv", "xlsx"],
            fields=[
                MethodFieldSpec(
                    name="outcome",
                    label="结果变量",
                    type="set_membership",
                    required=True,
                    role="outcome",
                    allow_missing=False,
                    constraints=MethodFieldConstraints(),
                    description="用于表示目标结果的集合隶属度。",
                ),
                MethodFieldSpec(
                    name="conditions",
                    label="条件变量",
                    type="set_membership",
                    required=True,
                    role="conditions",
                    allow_missing=False,
                    constraints=MethodFieldConstraints(),
                    description="至少 1 列，用于构成组态分析条件。",
                ),
            ],
        ),
        output_spec_json=MethodOutputSpec(
            summary="输出必要条件分析、真值表与组态路径，帮助用户理解多重条件组合。",
            result_blocks=[
                MethodResultBlockSpec(key="necessity", type="table", title="必要条件分析", required=True),
                MethodResultBlockSpec(key="truth_table", type="table", title="真值表", required=True),
                MethodResultBlockSpec(key="solution", type="table", title="组态解", required=True),
                MethodResultBlockSpec(key="consistency", type="table", title="一致性与覆盖度", required=True),
                MethodResultBlockSpec(key="path_interpretation", type="text", title="路径解释", required=True),
            ],
        ),
        template_file_url=None,
        sample_file_url=None,
        prerequisites=[
            "若未实现自动校准，则只接受已校准数据。",
            "字段类型应为 set_membership。",
        ],
        common_errors=[
            "字段类型不匹配",
            "方法前提不满足",
            "未按要求提供已校准数据",
        ],
        is_active=True,
        display_order=3,
        created_at="2026-03-14T00:00:00Z",
        updated_at="2026-03-14T00:00:00Z",
    ),
)


method_repository = MethodRepository()
