"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import ErrorMessage from "@/components/ErrorMessage";
import FileList from "@/components/FileList";
import Loading from "@/components/Loading";
import UploadBox from "@/components/UploadBox";
import { api } from "@/lib/api";
import type { DocumentInfo } from "@/lib/types";

export default function UploadPage() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      setDocuments(await api.listDocuments());
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Your documents</h1>
        <p className="text-slate-600">{documents.length} document(s) indexed</p>
      </div>
      <UploadBox onUploaded={refresh} />
      {loading && <Loading label="Connecting to the server…" />}
      {error && <ErrorMessage message={error} />}
      {!loading && <FileList documents={documents} onChanged={refresh} />}
      {documents.length > 0 && (
        <Link href="/chat" className="inline-block rounded-md bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700">
          Open AI assistant →
        </Link>
      )}
    </div>
  );
}
