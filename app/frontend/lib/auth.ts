const ACCESS_TOKEN_KEY = "dalilak_access_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
  } else {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  }
}

export function clearAccessToken(): void {
  setAccessToken(null);
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function getUserEmail(): string | null {
  const token = getAccessToken();
  if (!token) return null;
  const email = decodeJwtPayload(token)?.email;
  return typeof email === "string" ? email : null;
}

/** Derives a display name from the account email (e.g. "omar@mail.com" -> "Omar"). */
export function getUserDisplayName(): string | null {
  const localPart = getUserEmail()?.split("@")[0];
  if (!localPart) return null;
  return localPart.charAt(0).toUpperCase() + localPart.slice(1);
}
