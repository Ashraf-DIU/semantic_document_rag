import type { Source } from "@/lib/types";

export default function SourceCard({ source }: { source: Source }) {
  const pages =
    source.page_start === source.page_end
      ? `Page ${source.page_start}`
      : `Pages ${source.page_start}–${source.page_end}`;
  return (
    <details className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm">
      <summary className="cursor-pointer select-none">
        <span className="font-medium">📄 {source.document}</span>
        <span className="text-slate-500"> — {pages} · similarity {Math.round(source.score * 100)}%</span>
      </summary>
      <p className="mt-2 whitespace-pre-wrap text-slate-600">{source.snippet}</p>
    </details>
  );
}
