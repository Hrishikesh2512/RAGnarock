import { isRouteErrorResponse, useRouteError } from "react-router-dom";

export function RouteErrorPage() {
  const error = useRouteError();

  const message = isRouteErrorResponse(error)
    ? `${error.status} ${error.statusText}`
    : error instanceof Error
      ? error.message
      : "Unexpected error";

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 p-6 text-slate-100">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-semibold">Something went wrong</h1>
        <p className="text-slate-400">{message}</p>
        <a className="text-sm text-sky-400 underline" href="/">
          Back to home
        </a>
      </div>
    </main>
  );
}
