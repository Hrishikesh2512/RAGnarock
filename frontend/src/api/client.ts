import type {
  ApiErrorBody,
  AuthResponse,
  ChatResponse,
  DocumentItem,
  User,
} from "@/api/types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api").replace(/\/$/, "");
const TOKEN_KEY = "ragnarok.access_token";

export class ApiError extends Error {
  status: number;
  code: string;
  details: Record<string, unknown> | null;

  constructor(
    status: number,
    code: string,
    message: string,
    details: Record<string, unknown> | null = null,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function getToken(): string | null {
  return window.sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) {
    window.sessionStorage.setItem(TOKEN_KEY, token);
  } else {
    window.sessionStorage.removeItem(TOKEN_KEY);
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (response.status === 204) {
    return undefined as T;
  }

  const payload = (await response.json().catch(() => null)) as T | ApiErrorBody | null;
  if (!response.ok) {
    const error = (payload as ApiErrorBody | null)?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "request_failed",
      error?.message ?? response.statusText,
      error?.details ?? null,
    );
  }

  return payload as T;
}

export const api = {
  me: () => request<User>("/auth/me"),
  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  listDocuments: () => request<DocumentItem[]>("/documents"),
  uploadDocument: (file: File) => {
    const form = new FormData();
    const contentType =
      file.type && file.type !== "application/octet-stream"
        ? file.type
        : file.name.endsWith(".md") || file.name.endsWith(".markdown")
          ? "text/markdown"
          : "text/plain";
    const uploadFile =
      file.type === contentType
        ? file
        : new File([file], file.name, { type: contentType });
    form.append("file", uploadFile);
    return request<DocumentItem>("/documents", { method: "POST", body: form });
  },
  deleteDocument: (id: string) =>
    request<void>(`/documents/${id}`, { method: "DELETE" }),
  chat: (question: string, providerKey?: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      headers: providerKey ? { "X-Provider-Key": providerKey } : undefined,
      body: JSON.stringify({ question }),
    }),
};
