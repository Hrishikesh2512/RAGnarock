import type { DocumentStatus } from "@/api/types";

const STYLES: Record<DocumentStatus, string> = {
  pending: "bg-amber-500/10 text-amber-300",
  processing: "bg-sky-500/10 text-sky-300",
  ready: "bg-emerald-500/10 text-emerald-300",
  failed: "bg-rose-500/10 text-rose-300",
};

export function StatusBadge({ status }: { status: DocumentStatus }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${STYLES[status]}`}
    >
      {status}
    </span>
  );
}
