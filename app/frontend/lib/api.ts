import { getAccessToken, setAccessToken, clearAccessToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function extractErrorMessage(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => (item && typeof item === "object" && "msg" in item ? String((item as { msg: unknown }).msg) : null))
        .filter((msg): msg is string => Boolean(msg));
      if (messages.length > 0) return messages.join(" ");
    }
  }
  return fallback;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      extractErrorMessage(body, "Something went wrong. Please try again."),
      response.status,
    );
  }

  return body as T;
}

// --- Auth -------------------------------------------------------------

export interface UserResponse {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
}

export async function registerUser(email: string, password: string): Promise<UserResponse> {
  return request<UserResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function loginUser(email: string, password: string): Promise<TokenResponse> {
  const tokens = await request<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAccessToken(tokens.access_token);
  return tokens;
}

export async function refreshAccessToken(): Promise<TokenResponse> {
  const tokens = await request<TokenResponse>("/auth/refresh", { method: "POST" });
  setAccessToken(tokens.access_token);
  return tokens;
}

export async function logoutUser(): Promise<void> {
  try {
    await request<void>("/auth/logout", { method: "POST" });
  } finally {
    clearAccessToken();
  }
}

// --- Ask AI -------------------------------------------------------------

export interface Citation {
  manual_name: string;
  page: number;
  section?: string;
}

export interface AskRequest {
  question: string;
  selected_vehicle?: string | null;
}

export interface AskResponse {
  answer: string;
  citations: Citation[];
  confidence: "high" | "medium" | "low";
  latency_ms: number;
  intent?: string | null;
  entities?: Record<string, string> | null;
}

/** Thrown when /ask is called without (or with an expired) session, so the UI can prompt login. */
export class UnauthenticatedError extends Error {
  constructor() {
    super("You need to be logged in to ask a question.");
    this.name = "UnauthenticatedError";
  }
}

async function askOnce(payload: AskRequest, token: string): Promise<AskResponse> {
  return request<AskResponse>("/ask", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  });
}

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  let token = getAccessToken();
  if (!token) {
    throw new UnauthenticatedError();
  }

  try {
    return await askOnce(payload, token);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      try {
        const refreshed = await refreshAccessToken();
        token = refreshed.access_token;
      } catch {
        clearAccessToken();
        throw new UnauthenticatedError();
      }
      return await askOnce(payload, token);
    }
    throw error;
  }
}

export function getArabicErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return `حدث خطأ: ${error.message}`;
  }
  return "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.";
}

export function formatConfidence(level: AskResponse["confidence"]): string {
  const map: Record<AskResponse["confidence"], string> = {
    high: "High",
    medium: "Medium",
    low: "Low",
  };
  return map[level] || "Unknown";
}
