import { AuthPanel } from "@/features/auth/auth-panel";
import { useAuth } from "@/features/auth/auth-context";
import { ChatPanel } from "@/features/chat/chat-panel";
import { DocumentPanel } from "@/features/documents/document-panel";

export function WorkspacePage() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-400">
        <p>Loading…</p>
      </main>
    );
  }

  if (!user) {
    return <AuthPanel />;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">RAGnarok</h1>
            <p className="text-xs text-slate-500">
              Upload → chunk → embed → retrieve → answer
            </p>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="hidden text-slate-400 sm:inline">{user.email}</span>
            {/* Development auto-signs in as the local user, so signing out would dead-end. */}
            {import.meta.env.DEV ? null : (
              <button
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-slate-300 hover:border-slate-500"
                type="button"
                onClick={logout}
              >
                Sign out
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-6xl gap-6 p-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <DocumentPanel />
        <ChatPanel />
      </div>
    </main>
  );
}
