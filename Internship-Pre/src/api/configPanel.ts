import request from "@/utils/request";

export interface PanelConfig {
  "system.name": string;
  "system.logo": string;
  "log.enabled": string;
  "log.retention_days": string;
  "log.alert_enabled": string;
  "security.level": string;
  "security.two_factor": string;
  "security.password_policy": string;
}

/** 获取面板配置 */
export function getPanelConfig(): Promise<PanelConfig> {
  return request.get("/config/panel");
}

/** 批量保存面板配置 */
export function savePanelConfig(data: Partial<PanelConfig>) {
  return request.post("/config/panel-save", data);
}

/** 上传图片 */
export function uploadImage(file: File): Promise<{ url: string }> {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/config/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
