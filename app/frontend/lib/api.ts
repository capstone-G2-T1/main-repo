const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
}

export async function login(
  email: string,
  password: string
): Promise<TokenResponse> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error((data as { detail?: string }).detail ?? "Login failed");
  }
  return res.json() as Promise<TokenResponse>;
}

export async function register(
  email: string,
  password: string
): Promise<UserResponse> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error((data as { detail?: string }).detail ?? "Registration failed");
  }
  return res.json() as Promise<UserResponse>;
}

export async function logout(): Promise<void> {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("refresh_token")
      : null;
  await fetch(`${API_URL}/auth/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ refresh_token: token }),
  });
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
}

// ── RAG ───────────────────────────────────────────────────────────────────────

export interface Citation {
  manual_name: string;
  page: number;
  section?: string;
}

export interface AskResponse {
  answer: string;
  confidence: "high" | "medium" | "low";
  citations: Citation[];
  intent?: string;
  entities?: Record<string, string>;
  latency_ms?: number;
}

export interface AskRequest {
  question: string;
  selected_vehicle?: string | null;
}

export async function askQuestion(
  request: AskRequest
): Promise<AskResponse> {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error((data as { detail?: string }).detail ?? "Request failed");
  }
  return res.json() as Promise<AskResponse>;
}

export function getArabicErrorMessage(error: unknown): string {
  if (error instanceof Error) return `حدث خطأ: ${error.message}`;
  return "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.";
}

export function formatConfidence(
  level: AskResponse["confidence"]
): string {
  const map: Record<AskResponse["confidence"], string> = {
    high: "High",
    medium: "Medium",
    low: "Low",
  };
  return map[level] ?? "Unknown";
}
