import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, api } from "@/api/client";
import type { DocumentItem } from "@/api/types";
import { StatusBadge } from "@/features/documents/status-badge";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isActive(document: DocumentItem): boolean {
  return document.status === "pending" || document.status === "processing";
}

export function DocumentPanel() {
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);

  const documents = useQuery({
    queryKey: ["documents"],
    queryFn: api.listDocuments,
    refetchInterval: (query) =>
      query.state.data?.some(isActive) ? 1500 : false,
  });

  const upload = useMutation({
    mutationFn: api.uploadDocument,
    onSuccess: () => {
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const remove = useMutation({
    mutationFn: api.deleteDocument,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (file) upload.mutate(file);
  }

  const uploadError =
    upload.error instanceof ApiError
      ? upload.error.message
      : upload.error
        ? "Upload failed."
        : null;
  const removeError =
    remove.error instanceof ApiError ? remove.error.message : null;

  return (
    <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div>
        <h2 className="text-lg font-semibold">Documents</h2>
        <p className="text-sm text-slate-400">Upload a .txt or .md file to index it.</p>
      </div>

      <form className="flex flex-col gap-2 sm:flex-row" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm file:mr-3 file:rounded file:border-0 file:bg-slate-800 file:px-2 file:py-1 file:text-slate-200"
          type="file"
          accept=".txt,.md,text/plain,text/markdown"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <button
          className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-slate-950 disabled:opacity-60"
          type="submit"
          disabled={!file || upload.isPending}
        >
          {upload.isPending ? "Uploading…" : "Upload"}
        </button>
      </form>

      {uploadError ? <p className="text-sm text-rose-400">{uploadError}</p> : null}
      {removeError ? <p className="text-sm text-rose-400">{removeError}</p> : null}

      <ul className="divide-y divide-slate-800">
        {documents.data?.map((document) => (
          <li className="flex items-start justify-between gap-3 py-3" key={document.id}>
            <div className="min-w-0 space-y-1">
              <div className="flex items-center gap-2">
                <p className="truncate text-sm font-medium">{document.filename}</p>
                <StatusBadge status={document.status} />
              </div>
              <p className="text-xs text-slate-500">
                {formatBytes(document.size_bytes)} · {document.chunk_count} chunks
              </p>
              {document.error ? (
                <p className="text-xs text-rose-400">{document.error}</p>
              ) : null}
            </div>
            <button
              className="shrink-0 text-xs text-slate-400 underline hover:text-rose-300"
              type="button"
              onClick={() => remove.mutate(document.id)}
              disabled={remove.isPending}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      {documents.isLoading ? (
        <p className="text-sm text-slate-500">Loading documents…</p>
      ) : null}
      {documents.data?.length === 0 ? (
        <p className="text-sm text-slate-500">No documents yet.</p>
      ) : null}
    </section>
  );
}
