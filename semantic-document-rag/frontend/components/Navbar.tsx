import Link from "next/link";

export default function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.svg" alt="" className="h-7 w-7" />
          DocuMind
        </Link>
        <div className="flex gap-5 text-sm text-slate-600">
          <Link href="/upload" className="hover:text-indigo-600">Documents</Link>
          <Link href="/chat" className="hover:text-indigo-600">Assistant</Link>
        </div>
      </nav>
    </header>
  );
}
