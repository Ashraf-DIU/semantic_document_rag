import type { ChatMessage } from "@/lib/types";
import SourceCard from "./SourceCard";

export default function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] space-y-3 rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-indigo-600 text-white"
            : message.error
            ? "border border-red-200 bg-red-50 text-red-700"
            : "border border-slate-200 bg-white"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.sources && message.sources.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Sources</p>
            {message.sources.map((s, i) => (
              <SourceCard key={`${s.document_id}-${i}`} source={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
