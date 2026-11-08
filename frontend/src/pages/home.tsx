export function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-6 text-slate-100">
      <div className="max-w-xl space-y-3 text-center">
        <h1 className="text-4xl font-semibold tracking-tight">RAGnarock</h1>
        <p className="text-slate-400">
          Retrieval-augmented generation over your own documents.
        </p>
        <p className="text-xs text-slate-500">
          Application shell only — document and chat features are not implemented yet.
        </p>
      </div>
    </main>
  );
}
