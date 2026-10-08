import Link from "next/link";

export default function Home() {
  return (
    <section className="py-16 text-center">
      <h1 className="text-4xl font-bold tracking-tight">Semantic Document Search</h1>
      <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600">
        Upload your PDFs and ask questions in plain English. Every answer comes with the document
        and page it was taken from.
      </p>
      <div className="mt-8 flex justify-center gap-3">
        <Link href="/upload" className="rounded-md bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700">
          Upload documents
        </Link>
        <Link href="/chat" className="rounded-md border border-slate-300 bg-white px-5 py-2.5 font-medium hover:bg-slate-100">
          Open AI assistant
        </Link>
      </div>
      <ul className="mx-auto mt-14 grid max-w-3xl gap-4 text-left sm:grid-cols-3">
        {[
          ["Multi-PDF search", "Search across several papers at once, or filter to one."],
          ["Hybrid retrieval", "Semantic embeddings fused with BM25 keyword matching."],
          ["Cited answers", "Each answer links back to the exact pages used."],
        ].map(([title, text]) => (
          <li key={title} className="rounded-lg border border-slate-200 bg-white p-4">
            <h3 className="font-semibold">{title}</h3>
            <p className="mt-1 text-sm text-slate-600">{text}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
