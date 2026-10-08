import type { ChatResponse, DocumentInfo, UploadResponse } from "./types";

// Empty = same origin: on Vercel, /api/* is routed to the backend service by vercel.json.
// For plain `npm run dev` (frontend only), set NEXT_PUBLIC_API_URL=http://localhost:8000.
const API_URL = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api${path}`, init);
  } catch {
    throw new Error(
      "Cannot reach the server. If it is hosted on a free plan it may be waking up — wait ~30 seconds and retry."
    );
  }
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listDocuments: () => request<DocumentInfo[]>("/documents"),

  uploadFiles: (files: File[]) => {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return request<UploadResponse>("/upload", { method: "POST", body: form });
  },

  deleteDocument: (id: string) =>
    request<{ deleted: string }>(`/documents/${id}`, { method: "DELETE" }),

  chat: (question: string, documentIds: string[], topK = 5) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        top_k: topK,
        document_ids: documentIds.length ? documentIds : null,
      }),
    }),
};
