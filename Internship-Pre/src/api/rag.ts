import request from "@/utils/request";

// ── 知识库 ─────────────────────────────────────────────
export interface KnowledgeBase {
  id: number;
  name: string;
  description: string;
  status: number;
  doc_count: number;
  chunk_count: number;
  creator: number | null;
  creator_name: string;
  create_time: string;
  update_time: string;
}

export function getKnowledgeBaseList(params?: Record<string, any>): Promise<{ records: KnowledgeBase[]; total: number }> {
  return request.get("/rag/kb/", { params });
}

export function getKnowledgeBase(id: number): Promise<KnowledgeBase> {
  return request.get(`/rag/kb/${id}`);
}

export function createKnowledgeBase(data: Partial<KnowledgeBase>): Promise<KnowledgeBase> {
  return request.post("/rag/kb/", data);
}

export function updateKnowledgeBase(id: number, data: Partial<KnowledgeBase>): Promise<KnowledgeBase> {
  return request.put(`/rag/kb/${id}`, data);
}

export function deleteKnowledgeBase(id: number) {
  return request.delete(`/rag/kb/${id}`);
}

// ── 文档 ─────────────────────────────────────────────
export interface Document {
  id: number;
  knowledge_base: number;
  file_name: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: number;
  status_display: string;
  error_message: string;
  create_time: string;
  update_time: string;
}

export function getDocumentList(params?: Record<string, any>): Promise<{ records: Document[]; total: number }> {
  return request.get("/rag/documents/", { params });
}

export function getDocument(id: number): Promise<Document> {
  return request.get(`/rag/documents/${id}`);
}

export function deleteDocument(id: number) {
  return request.delete(`/rag/documents/${id}`);
}

export function reprocessDocument(id: number): Promise<Document> {
  return request.post(`/rag/documents/${id}/reprocess`);
}

export function uploadDocument(knowledgeBaseId: number, file: File): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("knowledge_base_id", String(knowledgeBaseId));
  return request.post("/rag/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

// ── 问答 ─────────────────────────────────────────────
export interface ChatSource {
  document_id: number;
  document_name: string;
  chunk_index: number;
  content: string;
  relevance_score: number;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  tokens_used: number;
}

export function chatWithKB(kbId: number, question: string): Promise<ChatResponse> {
  return request.post(`/rag/kb/${kbId}/chat`, { question });
}
