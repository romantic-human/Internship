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
  return request.get("/rag/kb", { params });
}

export function getKnowledgeBase(id: number): Promise<KnowledgeBase> {
  return request.get(`/rag/kb/${id}`);
}

export function createKnowledgeBase(data: Partial<KnowledgeBase>): Promise<KnowledgeBase> {
  return request.post("/rag/kb", data);
}

export function updateKnowledgeBase(id: number, data: Partial<KnowledgeBase>): Promise<KnowledgeBase> {
  return request.put(`/rag/kb/${id}`, data);
}

export function deleteKnowledgeBase(id: number): Promise<void> {
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
  return request.get("/rag/documents", { params });
}

export function getDocument(id: number): Promise<Document> {
  return request.get(`/rag/documents/${id}`);
}

export function deleteDocument(id: number): Promise<void> {
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

export function chatWithKB(kbId: number, question: string, image?: string): Promise<ChatResponse> {
  const data: Record<string, any> = { question };
  if (image) data.image = image;
  return request.post(`/rag/kb/${kbId}/chat`, data);
}

export function chatWithKBStream(
  kbId: number,
  question: string,
  onToken: (token: string) => void,
  onSources: (sources: ChatSource[]) => void,
  onDone: () => void,
  onError: (err: string) => void,
  image?: string,
): AbortController {
  const controller = new AbortController();
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "/api";
  const token = localStorage.getItem("access_token") || "";

  const body: Record<string, any> = { question };
  if (image) body.image = image;

  fetch(`${baseUrl}/rag/kb/${kbId}/chat-stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
    signal: controller.signal,
  })
    .then(async (response) => {
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "token" || data.type === "answer") {
                onToken(data.content);
              } else if (data.type === "sources") {
                onSources(data.content);
              } else if (data.type === "error") {
                onError(data.content);
              }
            } catch {
              // skip malformed SSE
            }
          }
        }
      }
      onDone();
    })
    .catch((err) => {
      if (err.name !== "AbortError") {
        onError(err.message);
      }
    });

  return controller;
}

