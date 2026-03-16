# 研究方法自动分析平台 数据规格说明

- 项目名称：研究方法自动分析平台
- 文档类型：数据规格说明
- 版本：v1.0
- 状态：初稿
- 面向阶段：MVP
- 更新时间：2026-03-13

---

# 1. 文档目标

本文档基于分享对话中的 PRD 与架构草案，定义平台在 MVP 阶段的核心数据模型、方法配置规范、文件契约、统一结果结构和接口契约，供前后端、分析模块和测试共同使用。

本文档重点回答以下问题：

1. 系统有哪些核心实体
2. 数据表需要保存哪些字段
3. 方法配置如何描述输入与输出要求
4. 上传、校验、分析、结果、导出的接口契约是什么
5. 前端应按什么统一结构渲染结果

---

# 2. 设计原则

## 2.1 方法优先

所有上传、校验、分析、结果结构都围绕 `method_slug` 驱动，不以页面写死逻辑为中心。

## 2.2 结构化优先

无论是错误提示还是分析结果，系统内部都优先保存结构化 JSON，再在展示层转成人可读文本。

## 2.3 统一结果结构

不同分析方法的输出允许内容不同，但必须适配统一外层结构，避免前端为每种方法编写完全不同的数据处理逻辑。

## 2.4 可扩展

字段和配置必须为新增方法预留空间，优先采用：

- 枚举字段
- 可选字段
- JSON 配置字段
- 版本字段

---

# 3. 通用约定

## 3.1 标识

- 主键 ID：推荐 UUID 或带前缀字符串 ID
- 方法唯一标识：`method_slug`
- 任务唯一标识：`task_id`
- 上传唯一标识：`upload_id`

## 3.2 时间

- 全部时间字段使用 ISO 8601
- 服务端统一使用 UTC 存储
- 前端按本地时区展示

## 3.3 命名

- 数据库字段：`snake_case`
- JSON 字段：`snake_case`
- 前端类型名：`PascalCase`

## 3.4 文件格式

MVP 支持：

- `.xlsx`
- `.csv`

暂不支持：

- `.sav`
- `.dta`
- `.rds`
- `.json`

---

# 4. 核心实体概览

MVP 涉及的核心实体如下：

1. 方法 `Method`
2. 方法模板 `MethodTemplate`
3. 上传记录 `Upload`
4. 分析任务 `AnalysisTask`
5. 校验报告 `ValidationReport`
6. 分析结果 `AnalysisResult`
7. 导出记录 `ExportFile`

实体关系概览：

```text
Method 1 --- n AnalysisTask
Method 1 --- n MethodTemplate
Upload 1 --- n AnalysisTask
AnalysisTask 1 --- 1 ValidationReport
AnalysisTask 1 --- 1 AnalysisResult
AnalysisTask 1 --- n ExportFile
```

---

# 5. 核心枚举

## 5.1 方法枚举

| 值 | 含义 |
| --- | --- |
| `descriptive_stats` | 描述统计 |
| `correlation` | 相关分析 |
| `regression` | 回归分析 |
| `t_test` | t 检验 |
| `anova` | 方差分析 |
| `fsqca` | fsQCA |

## 5.2 任务状态枚举

| 值 | 含义 |
| --- | --- |
| `created` | 任务已创建 |
| `uploaded` | 文件已上传 |
| `validating` | 正在校验 |
| `validated` | 校验已完成 |
| `analyzing` | 正在分析 |
| `success` | 分析成功 |
| `failed` | 任务失败 |
| `canceled` | 任务取消 |

## 5.3 校验问题级别

| 值 | 含义 |
| --- | --- |
| `error` | 阻塞分析 |
| `warning` | 不阻塞分析，但需提醒 |
| `info` | 说明性信息 |

## 5.4 字段类型枚举

| 值 | 含义 |
| --- | --- |
| `string` | 文本 |
| `integer` | 整数 |
| `number` | 数值 |
| `boolean` | 布尔 |
| `category` | 分类变量 |
| `date` | 日期 |
| `set_membership` | 集合隶属度 |

## 5.5 导出类型枚举

| 值 | 含义 |
| --- | --- |
| `pdf` | PDF 报告 |
| `docx` | Word 报告 |
| `md` | Markdown 报告 |

---

# 6. 数据表设计

# 6.1 `methods`

用途：存储研究方法元信息。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | uuid/string | 是 | 主键 |
| `slug` | string | 是 | 方法唯一标识 |
| `name` | string | 是 | 方法名称 |
| `category` | string | 是 | 方法分类，如 `quantitative` |
| `description` | text | 是 | 简短说明 |
| `applicable_scenarios` | jsonb | 否 | 适用研究问题列表 |
| `input_spec_json` | jsonb | 是 | 输入规范配置 |
| `output_spec_json` | jsonb | 是 | 输出规范配置 |
| `template_file_path` | string | 否 | 模板文件路径 |
| `sample_file_path` | string | 否 | 示例文件路径 |
| `is_active` | boolean | 是 | 是否启用 |
| `display_order` | integer | 否 | 排序值 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

# 6.2 `uploads`

用途：存储上传文件记录。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | uuid/string | 是 | 主键 |
| `user_id` | string | 否 | MVP 可为空 |
| `file_name` | string | 是 | 原始文件名 |
| `storage_path` | string | 是 | 存储路径 |
| `file_type` | string | 是 | `csv`/`xlsx` |
| `mime_type` | string | 否 | MIME 类型 |
| `file_size` | integer | 是 | 字节数 |
| `checksum` | string | 否 | 文件摘要 |
| `uploaded_at` | timestamptz | 是 | 上传时间 |

# 6.3 `analysis_tasks`

用途：存储任务主记录。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | uuid/string | 是 | 主键 |
| `user_id` | string | 否 | MVP 可为空 |
| `method_id` | string | 是 | 关联方法 |
| `method_slug` | string | 是 | 冗余存储，便于查询 |
| `upload_id` | string | 是 | 关联上传文件 |
| `status` | string | 是 | 任务状态 |
| `validation_passed` | boolean | 否 | 是否通过校验 |
| `started_at` | timestamptz | 否 | 开始分析时间 |
| `finished_at` | timestamptz | 否 | 完成时间 |
| `error_code` | string | 否 | 失败错误码 |
| `error_message` | text | 否 | 失败信息 |
| `created_at` | timestamptz | 是 | 创建时间 |

# 6.4 `validation_reports`

用途：存储校验结果摘要和详情。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | uuid/string | 是 | 主键 |
| `task_id` | string | 是 | 关联任务 |
| `passed` | boolean | 是 | 是否通过 |
| `error_count` | integer | 是 | 错误数 |
| `warning_count` | integer | 是 | 警告数 |
| `report_json` | jsonb | 是 | 详细校验结果 |
| `created_at` | timestamptz | 是 | 创建时间 |

# 6.5 `analysis_results`

用途：存储统一结构分析结果。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | uuid/string | 是 | 主键 |
| `task_id` | string | 是 | 关联任务 |
| `method_slug` | string | 是 | 方法标识 |
| `result_json` | jsonb | 是 | 完整结果 |
| `summary_text` | text | 否 | 摘要说明 |
| `created_at` | timestamptz | 是 | 创建时间 |

# 6.6 `export_files`

用途：存储导出记录。

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | uuid/string | 是 | 主键 |
| `task_id` | string | 是 | 关联任务 |
| `export_type` | string | 是 | `pdf`/`docx`/`md` |
| `storage_path` | string | 是 | 导出文件路径 |
| `created_at` | timestamptz | 是 | 创建时间 |

---

# 7. 方法配置规格

## 7.1 方法配置对象 `MethodSpec`

建议以 JSON 方式管理方法规范。

```json
{
  "slug": "regression",
  "name": "回归分析",
  "category": "quantitative",
  "min_sample_size": 30,
  "accepted_file_types": ["csv", "xlsx"],
  "fields": [],
  "analysis_options": {},
  "result_blocks": []
}
```

## 7.2 字段定义对象 `FieldSpec`

```json
{
  "name": "outcome",
  "label": "因变量",
  "type": "number",
  "required": true,
  "role": "dependent_variable",
  "allow_missing": false,
  "constraints": {
    "min": null,
    "max": null,
    "allowed_values": null
  },
  "description": "回归分析的因变量"
}
```

字段含义建议：

| 字段 | 说明 |
| --- | --- |
| `name` | 文件列名 |
| `label` | 前端展示名 |
| `type` | 字段类型 |
| `required` | 是否必填 |
| `role` | 字段在方法中的角色 |
| `allow_missing` | 是否允许缺失 |
| `constraints` | 最值、枚举、长度等 |
| `description` | 业务说明 |

## 7.3 结果块配置 `ResultBlockSpec`

```json
{
  "key": "model_summary",
  "type": "table",
  "title": "模型摘要",
  "required": true
}
```

支持类型建议：

- `summary`
- `table`
- `chart`
- `text`
- `download`

---

# 8. MVP 方法输入规范

# 8.1 描述统计 `descriptive_stats`

输入要求：

- 接受常规表格数据
- 至少 1 个字段
- 数值字段可计算均值、标准差
- 分类型字段可计算频数和比例

建议最小输入：

| 字段角色 | 要求 |
| --- | --- |
| `variables` | 至少 1 列 |

# 8.2 相关分析 `correlation`

输入要求：

- 至少 2 个数值型字段
- 缺失值比例不能超过配置阈值
- 样本量建议不少于 30

建议最小输入：

| 字段角色 | 要求 |
| --- | --- |
| `variables` | 至少 2 列数值型字段 |

# 8.3 回归分析 `regression`

输入要求：

- 1 个因变量
- 1 个或多个自变量
- 数值型字段优先
- 样本量建议不少于 30

MVP 当前最小约定：

- 因变量列名固定为 `outcome`
- 自变量列名需以 `predictor_` 开头
- 控制变量列名可选，需以 `control_` 开头

建议最小输入：

| 字段角色 | 要求 |
| --- | --- |
| `outcome` | 1 列，数值型 |
| `predictors` | 至少 1 列 |
| `controls` | 可选 |

# 8.4 t 检验 `t_test`

输入要求：

- 1 个分组变量
- 1 个结果变量
- 分组变量应包含 2 个水平

建议最小输入：

| 字段角色 | 要求 |
| --- | --- |
| `group` | 1 列，分类变量 |
| `outcome` | 1 列，数值型 |

# 8.5 方差分析 `anova`

输入要求：

- 1 个分组变量
- 1 个结果变量
- 分组变量应包含 3 个及以上水平

建议最小输入：

| 字段角色 | 要求 |
| --- | --- |
| `group` | 1 列，分类变量 |
| `outcome` | 1 列，数值型 |

# 8.6 fsQCA `fsqca`

输入要求：

- 1 个结果变量
- 至少 1 个条件变量
- 优先使用已校准数据
- 字段类型应为 `set_membership`

MVP 约束建议：

- 若未实现自动校准，则只接受已校准数据
- 若未完成完整求解，可先保留占位能力

---

# 9. 校验报告结构

## 9.1 统一结构

```json
{
  "passed": false,
  "summary": {
    "error_count": 2,
    "warning_count": 1
  },
  "errors": [
    {
      "code": "MISSING_REQUIRED_COLUMN",
      "level": "error",
      "field": "outcome",
      "message": "缺少必填字段 outcome",
      "suggestion": "请按模板补充该列"
    }
  ],
  "warnings": [],
  "stats": {
    "row_count": 24,
    "column_count": 5,
    "missing_ratio": 0.08
  }
}
```

## 9.2 常见错误码

| 错误码 | 含义 |
| --- | --- |
| `INVALID_FILE_TYPE` | 文件类型不支持 |
| `FILE_TOO_LARGE` | 文件过大 |
| `FILE_PARSE_FAILED` | 文件无法解析 |
| `MISSING_REQUIRED_COLUMN` | 缺少必填列 |
| `UNEXPECTED_COLUMN_TYPE` | 字段类型不匹配 |
| `TOO_MANY_MISSING_VALUES` | 缺失值过多 |
| `INSUFFICIENT_SAMPLE_SIZE` | 样本量不足 |
| `METHOD_PRECONDITION_FAILED` | 方法前提不满足 |

---

# 10. 分析结果统一结构

## 10.1 顶层结构

```json
{
  "task_id": "task_001",
  "method_slug": "regression",
  "status": "success",
  "summary": {
    "title": "回归分析完成",
    "highlights": [
      "模型整体显著",
      "X1 对 Y 为显著正向影响"
    ]
  },
  "tables": [],
  "charts": [],
  "interpretation": {
    "plain_language": "",
    "academic_style": ""
  },
  "report_payload": {}
}
```

## 10.2 表格对象

```json
{
  "key": "coefficients",
  "title": "回归系数表",
  "columns": ["variable", "coef", "p_value"],
  "rows": [
    ["X1", 0.42, 0.01]
  ]
}
```

## 10.3 图表对象

```json
{
  "key": "coef_chart",
  "title": "回归系数图",
  "type": "bar",
  "data": {
    "labels": ["X1", "X2"],
    "values": [0.42, -0.11]
  }
}
```

## 10.4 解释对象

```json
{
  "plain_language": "模型表明 X1 增加时，Y 有上升趋势。",
  "academic_style": "回归结果显示，X1 对 Y 的影响显著且为正向。"
}
```

---

# 11. API 契约

## 11.1 获取方法列表

`GET /api/methods`

响应：

```json
{
  "success": true,
  "message": "ok",
  "data": [
    {
      "slug": "regression",
      "name": "回归分析",
      "category": "quantitative",
      "description": "分析自变量对因变量的影响"
    }
  ]
}
```

MVP 为支持方法卡片展示，`data` 中的方法项可继续返回以下字段：

- `applicable_scenarios`
- `data_type_label`
- `analysis_difficulty`
- `sample_requirement`
- `is_recommended`

## 11.2 获取方法详情

`GET /api/methods/{slug}`

响应字段建议：

- 基础方法信息
- 输入字段规范
- 样本量要求
- 模板下载地址
- 示例文件地址
- 输出结构说明

最小响应示例：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "id": "method_regression",
    "slug": "regression",
    "name": "回归分析",
    "category": "quantitative",
    "description": "分析自变量对因变量的影响",
    "applicable_scenarios": [
      "已经有明确因变量和自变量，想判断影响方向与显著性。"
    ],
    "data_type_label": "以数值型字段为主，可包含控制变量。",
    "analysis_difficulty": "中",
    "sample_requirement": "样本量建议不少于 30。",
    "input_spec_json": {
      "spec_version": "1.0",
      "accepted_file_types": ["csv", "xlsx"],
      "min_sample_size": 30,
      "fields": []
    },
    "output_spec_json": {
      "summary": "输出模型整体表现、变量影响方向与显著性结果。",
      "result_blocks": []
    },
    "template_file_url": null,
    "sample_file_url": null,
    "prerequisites": [],
    "common_errors": [],
    "is_recommended": true,
    "is_active": true,
    "display_order": 2,
    "created_at": "2026-03-14T00:00:00Z",
    "updated_at": "2026-03-14T00:00:00Z"
  }
}
```

## 11.3 上传文件

`POST /api/uploads`

请求：

- `multipart/form-data`
- 字段：`file`

响应：

```json
{
  "success": true,
  "message": "uploaded",
  "data": {
    "upload_id": "upl_001",
    "file_name": "sample.xlsx",
    "file_size": 10240,
    "file_type": "xlsx"
  }
}
```

## 11.4 创建任务

`POST /api/tasks`

请求：

```json
{
  "method_slug": "regression",
  "upload_id": "upl_001"
}
```

响应：

```json
{
  "success": true,
  "message": "task created",
  "data": {
    "task_id": "task_001",
    "status": "created"
  }
}
```

## 11.5 校验任务

`POST /api/tasks/{taskId}/validate`

响应：

```json
{
  "success": true,
  "message": "validated",
  "data": {
    "task_id": "task_001",
    "status": "validated",
    "validation_passed": true,
    "validation": {
      "passed": true,
      "summary": {
        "error_count": 0,
        "warning_count": 1
      },
      "errors": [],
      "warnings": [
        {
          "code": "INSUFFICIENT_SAMPLE_SIZE",
          "level": "warning",
          "field": "variables",
          "message": "当前样本量较少，描述统计结果的稳定性可能有限。",
          "suggestion": "如条件允许，建议补充更多样本后再分析。"
        }
      ],
      "stats": {
        "row_count": 24,
        "column_count": 5,
        "missing_ratio": 0.08
      }
    }
  }
}
```

MVP 当前优先完整支持 `descriptive_stats` 与 `regression` 的上传与校验闭环，其他方法可先返回“尚未实现校验”的统一错误响应。

## 11.6 执行分析

`POST /api/tasks/{taskId}/analyze`

请求可选：

```json
{
  "options": {}
}
```

响应：

```json
{
  "success": true,
  "message": "analysis completed",
  "data": {
    "task_id": "task_001",
    "status": "success"
  }
}
```

MVP 当前对 `descriptive_stats` 与 `regression` 采用同步完成的最小实现，分析完成后直接返回成功状态。

## 11.7 获取任务结果

`GET /api/tasks/{taskId}/result`

响应 `data` 即统一结果结构。

最小响应示例：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "task_id": "task_001",
    "method_slug": "descriptive_stats",
    "status": "success",
    "result_version": "1.0",
    "generated_at": "2026-03-14T00:00:00Z",
    "summary": {
      "title": "描述统计完成",
      "highlights": [
        "共完成 24 行样本、5 个字段的描述统计。"
      ]
    },
    "tables": [],
    "charts": [],
    "interpretation": {
      "plain_language": "",
      "academic_style": ""
    },
    "report_payload": {}
  }
}
```

## 11.8 导出报告

`POST /api/tasks/{taskId}/export`

请求：

```json
{
  "export_type": "docx"
}
```

响应：

```json
{
  "success": true,
  "message": "export created",
  "data": {
    "export_id": "exp_001",
    "download_url": "/api/exports/exp_001/download"
  }
}
```

MVP 当前最小实现：

- 已支持 `docx`
- `pdf` / `md` 先保留枚举与扩展空间，后续再补真实生成能力

## 11.9 下载导出文件

`GET /api/exports/{exportId}/download`

说明：

- 当前用于下载 `POST /api/tasks/{taskId}/export` 生成的导出文件
- MVP 当前优先下载 `docx` 报告

---

# 12. 文件与存储规则

## 12.1 上传目录建议

```text
storage/
├─ uploads/
│  └─ {yyyy}/{mm}/{upload_id}_{safe_file_name}
└─ exports/
   └─ {yyyy}/{mm}/{export_id}.{ext}
```

## 12.2 文件命名规则

- 保留原始文件名用于展示
- 实际存储文件名采用安全文件名
- 文件下载时再回填可读名称

## 12.3 文件大小建议

- CSV：不超过 10 MB
- XLSX：不超过 20 MB

---

# 13. 版本与兼容性

## 13.1 配置版本

方法配置建议增加 `spec_version` 字段，用于未来升级模板和校验规则。

## 13.2 结果版本

统一结果结构建议包含：

- `result_version`
- `method_slug`
- `generated_at`

以便未来前端兼容不同输出版本。

---

# 14. 结论

MVP 阶段的数据规格核心是：

1. 以 `method_slug` 驱动整个流程
2. 使用统一任务模型串联上传、校验、分析和导出
3. 使用统一结果结构降低前端复杂度
4. 通过 JSON 配置为未来新增方法预留扩展空间

一句话总结：

**这份数据规格的目标，是让“方法配置、文件上传、校验报告、分析结果、接口响应”形成一套稳定、可扩展的公共契约。**
