"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BrandLogo } from "@/components/brand-logo";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  BriefcaseBusiness,
  Check,
  Clock3,
  GraduationCap,
  Mail,
  MapPin,
  Phone,
  Shield,
  UserRound,
} from "lucide-react";
import {
  adminPayload,
  api,
  candidatePayload,
  fetchOAuthProviders,
  loginResponseToToken,
  messageFromError,
  oauthAuthorizeUrl,
  recruiterPayload,
  studentPayload,
} from "@/lib/api";
import { STUDENT_INTERNSHIP_TYPE_OPTIONS } from "@/lib/applicant";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { LoginResponse, OAuthProvider, Role } from "@/types/recruitment";

type Mode = "login" | "register";

const roleCopy: Record<Role, { eyebrow: string; title: string }> = {
  student: {
    eyebrow: "Student access",
    title: "Build a profile recruiters can trust.",
  },
  candidate: {
    eyebrow: "Candidate access",
    title: "Showcase your skills and land the right role.",
  },
  recruiter: {
    eyebrow: "Recruiter access",
    title: "Move from applicants to interviews faster.",
  },
  admin: {
    eyebrow: "Administrator access",
    title: "Supervise users, data and platform performance.",
  },
};

function AuthExperienceContent() {
  const { login } = useAuth();
  const { showNotice } = useNotice();
  const searchParams = useSearchParams();
  const [role, setRole] = useState<Role>("student");
  const [mode, setMode] = useState<Mode>("login");
  const [oauthProviders, setOauthProviders] = useState<OAuthProvider[]>([]);
  const [requires2fa, setRequires2fa] = useState(false);
  const [loginChallenge, setLoginChallenge] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    company_name: "",
    university: "",
    field_of_study: "",
    internship_type: "",
    internship_duration: "",
  });

  useEffect(() => {
    fetchOAuthProviders()
      .then((data) => setOauthProviders(data.providers))
      .catch(() => setOauthProviders([]));
  }, []);

  useEffect(() => {
    const requires2fa = searchParams.get("requires_2fa") === "1";
    const oauthRole = searchParams.get("role") as Role | null;

    if (requires2fa) {
      setRequires2fa(true);
      setLoginChallenge(searchParams.get("login_challenge") || "");
    }

    if (oauthRole) {
      setRole(oauthRole);
    }
  }, [searchParams]);

  async function completeLogin(response: LoginResponse) {
    if (response.requires_2fa && response.login_challenge) {
      setRequires2fa(true);
      setLoginChallenge(response.login_challenge);
      if (response.role) setRole(response.role as Role);
      showNotice("Enter your 2FA code to continue.");
      return;
    }
    login(loginResponseToToken(response, role));
    showNotice(mode === "register" ? "Account created." : "Logged in.");
  }

  async function submit2fa(event: FormEvent) {
    event.preventDefault();
    try {
      const response = await api<LoginResponse>("/auth/2fa/verify-login", {
        method: "POST",
        body: JSON.stringify({
          login_challenge: loginChallenge,
          totp_code: totpCode,
        }),
      });
      login(loginResponseToToken(response, role));
      showNotice("2FA verified. Welcome back.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function attemptLogin() {
    const body = new URLSearchParams();
    body.set("username", form.email.trim().toLowerCase());
    body.set("password", form.password);
    if (role === "candidate") {
      body.set("client_id", "candidate");
    }
    const nextToken = await api<LoginResponse>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
      credentials: "include",
    });
    await completeLogin(nextToken);
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const email = form.email.trim().toLowerCase();
    if (!email.includes("@")) {
      showNotice("Enter a valid email address.");
      return;
    }
    if (form.password.length < 8) {
      showNotice("Password must be at least 8 characters.");
      return;
    }
    if (mode === "register" && !form.first_name.trim()) {
      showNotice("First name is required.");
      return;
    }
    if (mode === "register" && !form.last_name.trim()) {
      showNotice("Last name is required.");
      return;
    }
    if (mode === "register" && role === "recruiter" && !form.company_name.trim()) {
      showNotice("Company name is required for recruiters.");
      return;
    }
    try {
      if (mode === "register") {
        const registerPath =
          role === "student"
            ? "/auth/students/register"
            : role === "candidate"
              ? "/auth/candidates/register"
              : role === "admin"
                ? "/auth/admins/register"
                : "/auth/recruiters/register";
        const registerBody =
          role === "recruiter"
            ? recruiterPayload({ ...form, email })
            : role === "admin"
              ? adminPayload({ ...form, email })
              : role === "candidate"
                ? candidatePayload({ ...form, email })
                : studentPayload({ ...form, email });
        await api(registerPath, {
          method: "POST",
          body: JSON.stringify(registerBody),
        });
      }

      await attemptLogin();
    } catch (error) {
      const message = messageFromError(error);
      if (
        mode === "register" &&
        message.toLowerCase().includes("already registered")
      ) {
        try {
          showNotice("Account already exists. Signing you in...");
          setMode("login");
          await attemptLogin();
          return;
        } catch (loginError) {
          showNotice(
            `${messageFromError(loginError)} Try the Login tab with the same email and password.`,
          );
          setMode("login");
          return;
        }
      }
      showNotice(message);
    }
  }

  const isApplicant = role === "student" || role === "candidate";
  const internshipTypeOptions = STUDENT_INTERNSHIP_TYPE_OPTIONS;

  return (
    <div className="auth-page">
      <section className="auth-stage">
        <div className="auth-intro">
          <BrandLogo tagline="Student profiles. Candidate pipelines." />
          <p className="eyebrow">{roleCopy[role].eyebrow}</p>
          <h1>{roleCopy[role].title}</h1>
          <ul className="auth-features">
            <li>Clean profiles recruiters can scan in seconds</li>
            <li>Smart job matching and application tracking</li>
            <li>Secure login for students, candidates, and recruiters</li>
          </ul>
        </div>

        <form className="auth-card" onSubmit={requires2fa ? submit2fa : submit}>
          <div className="auth-card-top">
            <p className="eyebrow">{requires2fa ? "Two-factor authentication" : "Sign in"}</p>
            <ThemeToggle />
          </div>

          {!requires2fa && (
          <>
          <div className="choice-grid choice-grid--four">
            <button type="button" className={role === "student" ? "selected" : ""} onClick={() => setRole("student")}>
              <GraduationCap size={20} />
              <strong>Student</strong>
              <span>Profile and jobs</span>
            </button>
            <button type="button" className={role === "candidate" ? "selected" : ""} onClick={() => setRole("candidate")}>
              <UserRound size={20} />
              <strong>Candidate</strong>
              <span>Profile and apply</span>
            </button>
            <button type="button" className={role === "recruiter" ? "selected" : ""} onClick={() => setRole("recruiter")}>
              <BriefcaseBusiness size={20} />
              <strong>Recruiter</strong>
              <span>Jobs and hiring</span>
            </button>
            <button type="button" className={role === "admin" ? "selected" : ""} onClick={() => setRole("admin")}>
              <Shield size={20} />
              <strong>Admin</strong>
              <span>Platform control</span>
            </button>
          </div>

          <div className="segmented">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>
              Login
            </button>
            <button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>
              Register
            </button>
          </div>

          {mode === "register" && (
            <div className="form-grid two">
              <input placeholder="First name" value={form.first_name} onChange={(event) => setForm({ ...form, first_name: event.target.value })} />
              <input placeholder="Last name" value={form.last_name} onChange={(event) => setForm({ ...form, last_name: event.target.value })} />
              {isApplicant ? (
                <>
                  <input placeholder="University" value={form.university} onChange={(event) => setForm({ ...form, university: event.target.value })} />
                  <input placeholder="Field of study" value={form.field_of_study} onChange={(event) => setForm({ ...form, field_of_study: event.target.value })} />
                  {role === "student" && (
                    <>
                      <label className="field">
                        <span>Internship type</span>
                        <select value={form.internship_type} onChange={(event) => setForm({ ...form, internship_type: event.target.value })}>
                          <option value="">Choose type</option>
                          {internshipTypeOptions.map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label className="field">
                        <span>Internship duration</span>
                        <select value={form.internship_duration} onChange={(event) => setForm({ ...form, internship_duration: event.target.value })}>
                          <option value="">Choose duration</option>
                          <option value="Short-term (1 to 2 weeks)">Short-term (1 to 2 weeks)</option>
                          <option value="Lasting 1 to 3 months">Lasting 1 to 3 months</option>
                          <option value="Duration of 4 to 6 months">Duration of 4 to 6 months</option>
                        </select>
                      </label>
                    </>
                  )}
                </>
              ) : role === "admin" ? null : (
                <input placeholder="Company name" value={form.company_name} onChange={(event) => setForm({ ...form, company_name: event.target.value })} />
              )}
            </div>
          )}

          <input type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
          <input
            type="password"
            placeholder="Password (min. 8 characters)"
            minLength={8}
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            required
          />

          {oauthProviders.length > 0 && mode === "login" && (
            <div className="oauth-buttons">
              <p className="eyebrow">Or continue with</p>
              <div className="form-grid two">
                {oauthProviders.map((provider) => (
                  <a
                    key={provider.id}
                    className="secondary-button"
                    href={oauthAuthorizeUrl(provider.id, role)}
                  >
                    {provider.name}
                  </a>
                ))}
              </div>
            </div>
          )}

          <button className="primary-button" type="submit">
            <Check size={18} /> {mode === "register" ? "Create account" : "Enter workspace"}
          </button>
          </>
          )}

          {requires2fa && (
            <>
              <p>Enter the 6-digit code from your authenticator app.</p>
              <input
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                placeholder="123456"
                value={totpCode}
                onChange={(event) => setTotpCode(event.target.value)}
                required
              />
              <button className="primary-button" type="submit">
                <Shield size={18} /> Verify 2FA
              </button>
            </>
          )}
        </form>
      </section>

      <section className="auth-contact" aria-label="Contact info">
        <h2>Contact info</h2>
        <div className="auth-contact-grid">
          <article>
            <Phone size={22} aria-hidden />
            <div>
              <p className="auth-contact-label">Phone</p>
              <p>
                <a href="tel:+212661790436">+212 661 790 436</a>
              </p>
              <p>
                <a href="tel:+212808518588">+212 808 518 588</a>
              </p>
            </div>
          </article>
          <article>
            <MapPin size={22} aria-hidden />
            <div>
              <p className="auth-contact-label">Address</p>
              <p>Central Park, Im M, E2, N13</p>
              <p>Mohammedia, Morocco</p>
            </div>
          </article>
          <article>
            <Mail size={22} aria-hidden />
            <div>
              <p className="auth-contact-label">Email</p>
              <p>
                <a href="mailto:contact@matious.com">contact@matious.com</a>
              </p>
            </div>
          </article>
          <article>
            <Clock3 size={22} aria-hidden />
            <div>
              <p className="auth-contact-label">Response time</p>
              <p>Within 24 hours</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  );
}

export function AuthExperience() {
  return (
    <Suspense fallback={<div className="auth-page"><section className="auth-stage"><div className="auth-card"><p className="status-line">Loading sign-in experience...</p></div></section></div>}>
      <AuthExperienceContent />
    </Suspense>
  );
}
