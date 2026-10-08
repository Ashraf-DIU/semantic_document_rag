"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import ChatBox from "@/components/ChatBox";
import ErrorMessage from "@/components/ErrorMessage";
import Loading from "@/components/Loading";
import { api } from "@/lib/api";
import type { DocumentInfo } from "@/lib/types";

export default function ChatPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selected, setSelected] = useState<string[]>([]); // empty = all documents
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .listDocuments()
      .then(setDocuments)
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load documents"))
      .finally(() => setLoading(false));
  }, []);

  function toggle(id: string) {
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  }

  if (loading) return <Loading label="Connecting to the server…" />;
  if (error) return <ErrorMessage message={error} />;

  if (documents.length === 0) {
    return (
      <p className="text-slate-600">
        No documents yet.{" "}
        <Link href="/upload" className="text-indigo-600 underline">Upload some PDFs</Link> first.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Document assistant</h1>
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="text-slate-500">Search in:</span>
        <button
          onClick={() => setSelected([])}
          className={`rounded-full border px-3 py-1 ${
            selected.length === 0 ? "border-indigo-600 bg-indigo-600 text-white" : "border-slate-300 bg-white"
          }`}
        >
          All documents
        </button>
        {documents.map((d) => (
          <button
            key={d.document_id}
            onClick={() => toggle(d.document_id)}
            className={`max-w-[14rem] truncate rounded-full border px-3 py-1 ${
              selected.includes(d.document_id)
                ? "border-indigo-600 bg-indigo-600 text-white"
                : "border-slate-300 bg-white"
            }`}
          >
            {d.filename}
          </button>
        ))}
      </div>
      <ChatBox documentIds={selected} />
    </div>
  );
}
