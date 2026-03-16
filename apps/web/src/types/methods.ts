export type MethodCategory = "quantitative" | "configurational";
export type ResultBlockType = "summary" | "table" | "chart" | "text" | "download";

export type MethodFieldSpec = {
  name: string;
  label: string;
  type: string;
  required: boolean;
  role: string;
  description: string;
};

export type MethodFieldSpecDto = MethodFieldSpec & {
  allow_missing: boolean;
  constraints: {
    min: number | null;
    max: number | null;
    allowed_values: string[] | null;
  } | null;
};

export type MethodInputSpec = {
  acceptedFileTypes: Array<"csv" | "xlsx">;
  minSampleSize?: number;
  fields: MethodFieldSpec[];
};

export type MethodInputSpecDto = {
  spec_version: string;
  accepted_file_types: Array<"csv" | "xlsx">;
  min_sample_size: number | null;
  fields: MethodFieldSpecDto[];
};

export type MethodResultBlockDto = {
  key: string;
  type: ResultBlockType;
  title: string;
  required: boolean;
};

export type MethodOutputSpec = {
  summary: string;
  resultBlocks: string[];
};

export type MethodOutputSpecDto = {
  summary: string;
  result_blocks: MethodResultBlockDto[];
};

export type MethodResource = {
  label: string;
  url: string | null;
  status: "placeholder";
};

export type MethodListItemDto = {
  id: string;
  slug: string;
  name: string;
  category: MethodCategory;
  description: string;
  applicable_scenarios: string[];
  data_type_label: string;
  analysis_difficulty: "低" | "中" | "高";
  sample_requirement: string;
  is_recommended: boolean;
};

export type MethodDetailDto = MethodListItemDto & {
  input_spec_json: MethodInputSpecDto;
  output_spec_json: MethodOutputSpecDto;
  template_file_url: string | null;
  sample_file_url: string | null;
  prerequisites: string[];
  common_errors: string[];
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
};

export type ApiSuccessResponse<T> = {
  success: true;
  message: string;
  data: T;
};

export type ApiErrorResponse = {
  success: false;
  message: string;
  error_code: string;
  details: Record<string, unknown>;
};

export type Method = {
  id: string;
  slug: string;
  name: string;
  category: MethodCategory;
  description: string;
  applicableScenarios: string[];
  dataTypeLabel: string;
  analysisDifficulty: "低" | "中" | "高";
  sampleRequirement: string;
  prerequisites: string[];
  inputSpec: MethodInputSpec;
  outputSpec: MethodOutputSpec;
  templateResource: MethodResource;
  sampleResource: MethodResource;
  commonErrors: string[];
  isRecommended: boolean;
};
