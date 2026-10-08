"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { DocumentInfo } from "@/lib/types";
import ErrorMessage from "./ErrorMessage";

export default function FileList({
  documents,
  onChanged,
}: {
  documents: DocumentInfo[];
  onChanged: () => void;
}) {
  const [error, setError] = useState("");

  async function remove(id: string) {
    setError("");
    try {
      await api.deleteDocument(id);
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  }

  if (documents.length === 0) {
    return <p className="text-sm text-slate-500">No documents yet. Upload a PDF to get started.</p>;
  }

  return (
    <div className="space-y-2">
      {error && <ErrorMessage message={error} />}
      <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        {documents.map((d) => (
          <li key={d.document_id} className="flex items-center justify-between gap-3 px-4 py-3">
            <div className="min-w-0">
              <p className="truncate font-medium">📄 {d.filename}</p>
              <p className="text-xs text-slate-500">{d.pages} pages · {d.chunks} chunks</p>
            </div>
            <button
              onClick={() => remove(d.document_id)}
              className="shrink-0 text-sm text-red-600 hover:underline"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
