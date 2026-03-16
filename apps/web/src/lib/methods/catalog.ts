import type { Method } from "@/types/methods";

function placeholderResource(label: string) {
  return {
    label,
    url: null,
    status: "placeholder" as const,
  };
}

export const methodCatalog: readonly Method[] = [
  {
    id: "method_descriptive_stats",
    slug: "descriptive_stats",
    name: "描述统计",
    category: "quantitative",
    description: "用于概览样本与变量的整体分布，输出均值、中位数、标准差、最大值、最小值以及频数和比例。",
    applicableScenarios: [
      "已完成数据收集，想先了解样本和变量的基本分布情况。",
      "需要在论文或报告中呈现基础统计结果。",
      "准备进入相关分析或回归分析前，先做数据概览。",
    ],
    dataTypeLabel: "接受常规表格数据，可同时包含数值型字段和分类型字段。",
    analysisDifficulty: "低",
    sampleRequirement: "接受常规表格数据，至少 1 个字段。",
    prerequisites: ["文件格式仅支持 .xlsx 和 .csv。", "字段命名应清晰且文件可正常读取。"],
    inputSpec: {
      acceptedFileTypes: ["csv", "xlsx"],
      fields: [
        {
          name: "variables",
          label: "待统计字段",
          type: "number",
          required: true,
          role: "variables",
          description: "至少 1 列；数值型字段可计算均值、标准差，分类型字段可在同一文件中计算频数和比例。",
        },
      ],
    },
    outputSpec: {
      summary: "输出结构化基础统计结果，便于用户快速理解样本概况。",
      resultBlocks: ["均值", "中位数", "标准差", "最大值与最小值", "频数与比例"],
    },
    templateResource: placeholderResource("描述统计模板下载"),
    sampleResource: placeholderResource("描述统计示例文件下载"),
    commonErrors: ["文件类型不支持", "文件无法解析"],
    isRecommended: true,
  },
  {
    id: "method_regression",
    slug: "regression",
    name: "回归分析",
    category: "quantitative",
    description: "分析自变量对因变量的影响。",
    applicableScenarios: [
      "已经有明确因变量和自变量，想判断影响方向与显著性。",
      "需要输出模型摘要、系数表和拟合优度。",
      "希望将结果整理为论文中的“结果分析”部分。",
    ],
    dataTypeLabel: "以数值型字段为主，可包含控制变量。",
    analysisDifficulty: "中",
    sampleRequirement: "样本量建议不少于 30。",
    prerequisites: [
      "需包含 1 个因变量和 1 个或多个自变量。",
      "MVP 当前约定因变量列名为 `outcome`，自变量列名以 `predictor_` 开头，可选控制变量列名以 `control_` 开头。",
      "数值型字段优先。",
    ],
    inputSpec: {
      acceptedFileTypes: ["csv", "xlsx"],
      minSampleSize: 30,
      fields: [
        {
          name: "outcome",
          label: "因变量",
          type: "number",
          required: true,
          role: "dependent_variable",
          description: "回归分析的因变量。",
        },
        {
          name: "predictors",
          label: "自变量",
          type: "number",
          required: true,
          role: "independent_variable",
          description: "至少 1 列，用于解释因变量变化。",
        },
        {
          name: "controls",
          label: "控制变量",
          type: "number",
          required: false,
          role: "control_variable",
          description: "可选，用于控制其他影响因素。",
        },
      ],
    },
    outputSpec: {
      summary: "输出模型整体表现、变量影响方向与显著性结果。",
      resultBlocks: ["模型摘要", "系数表", "显著性结果", "拟合优度", "结果解释"],
    },
    templateResource: placeholderResource("回归分析模板下载"),
    sampleResource: placeholderResource("回归分析示例文件下载"),
    commonErrors: [
      "缺少必填字段 outcome",
      "字段类型不匹配",
      "当前样本量低于回归分析建议样本量 30",
      "自变量之间完全共线或字段没有变异",
    ],
    isRecommended: true,
  },
  {
    id: "method_fsqca",
    slug: "fsqca",
    name: "fsQCA",
    category: "configurational",
    description: "用于识别通向结果出现的条件组态，输出必要条件分析、真值表、组态解、一致性与覆盖度。",
    applicableScenarios: [
      "研究问题关注多重条件如何共同导致某一结果。",
      "已有条件变量与结果变量，想比较不同组态路径。",
      "需要从组态视角解释复杂因果关系。",
    ],
    dataTypeLabel: "优先使用已校准数据，字段类型应为集合隶属度。",
    analysisDifficulty: "高",
    sampleRequirement: "至少 1 个结果变量和 1 个或多个条件变量；MVP 优先使用已校准数据。",
    prerequisites: ["若未实现自动校准，则只接受已校准数据。", "字段类型应为 set_membership。"],
    inputSpec: {
      acceptedFileTypes: ["csv", "xlsx"],
      fields: [
        {
          name: "outcome",
          label: "结果变量",
          type: "set_membership",
          required: true,
          role: "outcome",
          description: "用于表示目标结果的集合隶属度。",
        },
        {
          name: "conditions",
          label: "条件变量",
          type: "set_membership",
          required: true,
          role: "conditions",
          description: "至少 1 列，用于构成组态分析条件。",
        },
      ],
    },
    outputSpec: {
      summary: "输出必要条件分析、真值表与组态路径，帮助用户理解多重条件组合。",
      resultBlocks: ["必要条件分析", "真值表", "组态解", "一致性与覆盖度", "路径解释"],
    },
    templateResource: placeholderResource("fsQCA 模板下载"),
    sampleResource: placeholderResource("fsQCA 示例文件下载"),
    commonErrors: ["字段类型不匹配", "方法前提不满足", "未按要求提供已校准数据"],
    isRecommended: true,
  },
];
