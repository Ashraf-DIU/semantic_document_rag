export interface DocumentInfo {
  document_id: string;
  filename: string;
  pages: number;
  chunks: number;
  uploaded_at: string;
}

export interface UploadResponse {
  documents: DocumentInfo[];
  skipped: string[];
}

export interface Source {
  document_id: string;
  document: string;
  page_start: number;
  page_end: number;
  score: number;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  error?: boolean;
}
