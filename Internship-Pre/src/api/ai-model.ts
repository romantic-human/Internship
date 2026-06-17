import request from "@/utils/request";

// ── AI 模型配置 ─────────────────────────────────────────────
export interface AIModelConfig {
  id: number;
  name: string;
  provider: string;
  provider_display: string;
  model_type: string;
  model_type_display: string;
  model_name: string;
  api_key: string;
  api_base_url: string;
  is_default: boolean;
  status: number;
  remark: string;
  create_time: string;
  update_time: string;
}

export interface AIModelListResponse {
  records: AIModelConfig[];
  total: number;
}

// 获取模型配置列表
export function getAIModelList(params?: Record<string, any>): Promise<AIModelListResponse> {
  return request.get("/config/ai-model", { params });
}

// 获取单个模型配置
export function getAIModel(id: number): Promise<AIModelConfig> {
  return request.get(`/config/ai-model/${id}`);
}

// 创建模型配置
export function createAIModel(data: Partial<AIModelConfig>): Promise<AIModelConfig> {
  return request.post("/config/ai-model", data);
}

// 更新模型配置
export function updateAIModel(id: number, data: Partial<AIModelConfig>): Promise<AIModelConfig> {
  return request.put(`/config/ai-model/${id}`, data);
}

// 删除模型配置
export function deleteAIModel(id: number): Promise<void> {
  return request.delete(`/config/ai-model/${id}`);
}

// 设置默认模型
export function setDefaultAIModel(id: number): Promise<void> {
  return request.post(`/config/ai-model/${id}/set-default`);
}

// 测试模型连接
export function testAIModelConnection(id: number): Promise<{ model: string; response: string }> {
  return request.post(`/config/ai-model/${id}/test`);
}

// 获取可用模型列表（按类型）
export function getAvailableModels(modelType?: string): Promise<AIModelConfig[]> {
  const params: Record<string, any> = {};
  if (modelType) params.model_type = modelType;
  return request.get("/config/ai-model/list-models", { params });
}
