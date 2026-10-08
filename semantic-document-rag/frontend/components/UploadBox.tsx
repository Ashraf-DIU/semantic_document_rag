"use client";

import { useRef, useState } from "react";
import { api } from "@/lib/api";
import ErrorMessage from "./ErrorMessage";
import Loading from "./Loading";

export default function UploadBox({ onUploaded }: { onUploaded: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notes, setNotes] = useState<string[]>([]);

  async function handleFiles(list: FileList | null) {
    if (!list || list.length === 0) return;
    setBusy(true);
    setError("");
    setNotes([]);
    try {
      const res = await api.uploadFiles(Array.from(list));
      setNotes(res.skipped);
      onUploaded();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files); }}
        className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition ${
          dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-300 bg-white"
        }`}
      >
        <div className="text-4xl">📄</div>
        <p className="mt-2 font-medium">Drop PDFs here</p>
        <p className="text-sm text-slate-500">Text-based PDFs, up to 20 MB each</p>
        <button
          type="button"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
          className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Browse files
        </button>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          multiple
          hidden
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {busy && <Loading label="Extracting, chunking and embedding… this can take a minute on first use." />}
      {error && <ErrorMessage message={error} />}
      {notes.map((n) => (
        <p key={n} className="text-sm text-amber-700">⚠ {n}</p>
      ))}
    </div>
  );
}
