import type { LoginResponse, OAuthProvider, Role, Token } from "@/types/recruitment";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type AuthHandlers = {
  onTokenRefreshed?: (token: Token) => void;
  onAuthFailed?: () => void;
};

let authHandlers: AuthHandlers = {};

export function setAuthHandlers(handlers: AuthHandlers) {
  authHandlers = handlers;
}

function hasAuthHeader(init: RequestInit) {
  const { headers } = init;
  if (!headers) return false;
  if (headers instanceof Headers) return headers.has("Authorization");
  if (Array.isArray(headers)) return headers.some(([key]) => key.toLowerCase() === "authorization");
  // `headers` may be a plain object mapping header names to values
  return Object.prototype.hasOwnProperty.call(headers, "Authorization") || Object.prototype.hasOwnProperty.call(headers, "authorization");
}

export function homeRouteForRole(role: Role) {
  if (role === "student") return "/student/profile";
  if (role === "candidate") return "/candidate/profile";
  if (role === "admin") return "/admin/dashboard";
  return "/recruiter/dashboard";
}

export function authHeader(token: string) {
  return { Authorization: `Bearer ${token}` };
}

export function auth(token: string): RequestInit {
  return { headers: { ...authHeader(token), "Content-Type": "application/json" } };
}

export async function api<T = unknown>(
  path: string,
  init: RequestInit = {},
  retried = false,
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(init.headers || {}),
    },
  });

  if (
    response.status === 401 &&
    !retried &&
    !path.startsWith("/auth/login") &&
    !path.startsWith("/auth/refresh") &&
    hasAuthHeader(init)
  ) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const headers = new Headers(init.headers || {});
      headers.set("Authorization", `Bearer ${refreshed.access_token}`);
      return api<T>(path, { ...init, headers }, true);
    }
    authHandlers.onAuthFailed?.();
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const errorBody = payload.error as
      | { message?: string; details?: { fields?: Array<{ field?: string; message?: string }> } }
      | undefined;
    const fieldMessages = errorBody?.details?.fields
      ?.map((item) => (item.field ? `${item.field}: ${item.message}` : item.message))
      .filter(Boolean)
      .join("; ");
    if (fieldMessages) throw new Error(fieldMessages);
    const detail = payload.detail ?? errorBody?.message;
    if (typeof detail === "string") throw new Error(detail);
    if (Array.isArray(detail)) {
      throw new Error(detail.map((item: { msg?: string }) => item.msg || "Validation error").join(", "));
    }
    throw new Error(`Request failed: ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

export function messageFromError(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong";
}

const TOKEN_KEY = "recruitment_token";
const SESSION_TOKEN_KEY = "recruitment_token_session";

export function loadToken(): Token | null {
  if (typeof window === "undefined") return null;
  const stored =
    localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(SESSION_TOKEN_KEY);
  return stored ? (JSON.parse(stored) as Token) : null;
}

export function saveToken(token: Token, persist = true) {
  const serialized = JSON.stringify(token);
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(SESSION_TOKEN_KEY);

  if (persist) {
    localStorage.setItem(TOKEN_KEY, serialized);
    return;
  }

  sessionStorage.setItem(SESSION_TOKEN_KEY, serialized);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(SESSION_TOKEN_KEY);
}

export function oauthAuthorizeUrl(provider: string, role: Role) {
  return `${API_URL}/auth/oauth/${provider}/authorize?role=${role}`;
}

export async function fetchOAuthProviders() {
  return api<{ providers: OAuthProvider[] }>("/auth/oauth/providers");
}

export async function refreshAccessToken(refreshToken: string) {
  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    credentials: "include",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message =
      payload.detail ??
      payload.error?.message ??
      "Session expired. Please sign in again.";
    throw new Error(typeof message === "string" ? message : "Session expired.");
  }
  const pair = (await response.json()) as {
    access_token: string;
    refresh_token: string;
    role: Role;
  };
  const current = loadToken();
  const next: Token = {
    access_token: pair.access_token,
    refresh_token: pair.refresh_token,
    role: pair.role || current?.role || "student",
  };
  saveToken(next, !!localStorage.getItem(TOKEN_KEY));
  authHandlers.onTokenRefreshed?.(next);
  return next;
}

async function tryRefreshToken(): Promise<Token | null> {
  const current = loadToken();
  if (!current?.refresh_token) return null;
  try {
    return await refreshAccessToken(current.refresh_token);
  } catch {
    return null;
  }
}

export function loginResponseToToken(response: LoginResponse, fallbackRole: Role): Token {
  return {
    access_token: response.access_token || "",
    refresh_token: response.refresh_token || undefined,
    role: (response.role as Role) || fallbackRole,
  };
}

export function stripEmpty(values: Record<string, string>) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value.trim()));
}

export function formatDate(value: string) {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function chips(value: string | null) {
  return (value || "")
    .split(",")
    .map((chip) => chip.trim())
    .filter(Boolean)
    .slice(0, 8);
}

export function studentProfileScore(profile: { technical_skills?: string | null; soft_skills?: string | null; experiences?: string | null; projects?: string | null; bio?: string | null; cv_filename?: string | null } | null) {
  if (!profile) return 0;
  const fields = [profile.technical_skills, profile.soft_skills, profile.experiences, profile.projects, profile.bio, profile.cv_filename];
  return Math.round((fields.filter(Boolean).length / fields.length) * 100);
}

export function emptyProfileForm() {
  return {
    technical_skills: "",
    soft_skills: "",
    experiences: "",
    projects: "",
    certifications: "",
    languages: "",
    bio: "",
    internship_type: "",
    internship_duration: "",
  };
}

export function studentToForm(student: {
  technical_skills?: string | null;
  skills?: string | null;
  soft_skills?: string | null;
  experiences?: string | null;
  projects?: string | null;
  certifications?: string | null;
  languages?: string | null;
  bio?: string | null;
  internship_type?: string | null;
  internship_duration?: string | null;
}) {
  return {
    technical_skills: student.technical_skills || student.skills || "",
    soft_skills: student.soft_skills || "",
    experiences: student.experiences || "",
    projects: student.projects || "",
    certifications: student.certifications || "",
    languages: student.languages || "",
    bio: student.bio || "",
    internship_type: student.internship_type || "",
    internship_duration: student.internship_duration || "",
  };
}

export function studentPayload(form: Record<string, string>) {
  return {
    email: form.email,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
    university: form.university || null,
    field_of_study: form.field_of_study || null,
    internship_type: form.internship_type || null,
    internship_duration: form.internship_duration || null,
  };
}

export function candidatePayload(form: Record<string, string>) {
  return {
    email: form.email,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
    university: form.university || null,
    field_of_study: form.field_of_study || null,
  };
}

export function recruiterPayload(form: Record<string, string>) {
  return {
    email: form.email,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
    company_name: form.company_name,
  };
}

export function adminPayload(form: Record<string, string>) {
  return {
    email: form.email,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
  };
}

export function candidateName(candidate: { first_name: string; last_name: string }) {
  return `${candidate.first_name} ${candidate.last_name}`.trim();
}
