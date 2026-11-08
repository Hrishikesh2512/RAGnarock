import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { FormEvent } from "react";

import { ApiError, api } from "@/api/client";
import type { Citation } from "@/api/types";

type ChatMessage =
  | { role: "user"; content: string }
  | { role: "assistant"; answer: string; citations: Citation[] };

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState("");
  const [providerKey, setProviderKey] = useState("");

  const chat = useMutation({
    mutationFn: (value: string) => api.chat(value, providerKey.trim() || undefined),
    onSuccess: (response) => {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          answer: response.answer,
          citations: response.citations,
        },
      ]);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = question.trim();
    if (!value || chat.isPending) return;

    setMessages((current) => [...current, { role: "user", content: value }]);
    setQuestion("");
    chat.mutate(value);
  }

  const error = chat.error instanceof ApiError ? chat.error : null;

  return (
    <section className="flex min-h-[28rem] flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div>
        <h2 className="text-lg font-semibold">Ask your documents</h2>
        <p className="text-sm text-slate-400">
          Answers are grounded in the retrieved passages and cite them.
        </p>
      </div>

      <details className="rounded-lg border border-slate-800 p-3 text-sm">
        <summary className="cursor-pointer text-slate-300">
          Model key (OpenRouter)
        </summary>
        <label className="mt-3 block space-y-1">
          <span className="text-xs text-slate-400">
            Kept in memory for this tab; never sent anywhere except the provider.
          </span>
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-sky-500"
            type="password"
            placeholder="sk-or-…"
            value={providerKey}
            onChange={(event) => setProviderKey(event.target.value)}
          />
        </label>
      </details>

      <div className="flex-1 space-y-3 overflow-y-auto">
        {messages.length === 0 ? (
          <p className="text-sm text-slate-500">
            Upload a document, then ask a question about it.
          </p>
        ) : null}

        {messages.map((message, index) =>
          message.role === "user" ? (
            <p
              className="ml-auto max-w-[85%] rounded-2xl bg-sky-500/15 px-4 py-2 text-sm text-sky-100"
              key={`user-${index}`}
            >
              {message.content}
            </p>
          ) : (
            <article className="max-w-[95%] space-y-2" key={`answer-${index}`}>
              <p className="whitespace-pre-wrap rounded-2xl bg-slate-800/70 px-4 py-3 text-sm text-slate-100">
                {message.answer}
              </p>
              {message.citations.length > 0 ? (
                <ul className="space-y-2">
                  {message.citations.map((citation) => (
                    <li
                      className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-400"
                      key={citation.chunk_id}
                    >
                      <p className="font-medium text-slate-300">
                        {citation.filename} · chunk {citation.chunk_index} ·{" "}
                        {citation.score.toFixed(3)}
                      </p>
                      <p className="mt-1 line-clamp-3">{citation.snippet}</p>
                    </li>
                  ))}
                </ul>
              ) : null}
            </article>
          ),
        )}

        {chat.isPending ? (
          <p className="text-sm text-slate-500">Thinking…</p>
        ) : null}
      </div>

      {error ? (
        <p className="text-sm text-rose-400">
          {error.message}
          {error.code === "provider_key_required"
            ? " Add an OpenRouter key above."
            : null}
        </p>
      ) : null}

      <form className="flex gap-2" onSubmit={handleSubmit}>
        <input
          className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
          type="text"
          placeholder="What does the document say about…?"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button
          className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-slate-950 disabled:opacity-60"
          type="submit"
          disabled={!question.trim() || chat.isPending}
        >
          Ask
        </button>
      </form>
    </section>
  );
}
