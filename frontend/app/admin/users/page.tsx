"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Plus, Trash2, Users } from "lucide-react";
import { SectionHeading } from "@/components/ui";
import { api, auth, messageFromError } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { AdminApplicant, AdminRecruiterUser } from "@/types/recruitment";

type UserKind = "students" | "candidates" | "recruiters";

const emptyApplicant = {
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  university: "",
  field_of_study: "",
  internship_type: "",
  internship_duration: "",
  company_name: "",
  phone: "",
};

export default function AdminUsersPage() {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [kind, setKind] = useState<UserKind>("students");
  const [students, setStudents] = useState<AdminApplicant[]>([]);
  const [candidates, setCandidates] = useState<AdminApplicant[]>([]);
  const [recruiters, setRecruiters] = useState<AdminRecruiterUser[]>([]);
  const [form, setForm] = useState(emptyApplicant);

  const load = useCallback(async () => {
    if (!token) return;
    const headers = auth(token.access_token);
    const [nextStudents, nextCandidates, nextRecruiters] = await Promise.all([
      api<AdminApplicant[]>("/admin/users/students", headers),
      api<AdminApplicant[]>("/admin/users/candidates", headers),
      api<AdminRecruiterUser[]>("/admin/users/recruiters", headers),
    ]);
    setStudents(nextStudents);
    setCandidates(nextCandidates);
    setRecruiters(nextRecruiters);
  }, [token]);

  useEffect(() => {
    load().catch((error) => showNotice(messageFromError(error)));
  }, [load, showNotice]);

  async function createUser(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    try {
      const path =
        kind === "students"
          ? "/admin/users/students"
          : kind === "candidates"
            ? "/admin/users/candidates"
            : "/admin/users/recruiters";
      const body =
        kind === "recruiters"
          ? {
              email: form.email,
              password: form.password,
              first_name: form.first_name,
              last_name: form.last_name,
              company_name: form.company_name,
              phone: form.phone || null,
            }
          : kind === "students"
            ? {
                email: form.email,
                password: form.password,
                first_name: form.first_name,
                last_name: form.last_name,
                university: form.university || null,
                field_of_study: form.field_of_study || null,
                internship_type: form.internship_type || null,
                internship_duration: form.internship_duration || null,
              }
            : {
                email: form.email,
                password: form.password,
                first_name: form.first_name,
                last_name: form.last_name,
                university: form.university || null,
                field_of_study: form.field_of_study || null,
              };
      await api(path, {
        ...auth(token.access_token),
        method: "POST",
        body: JSON.stringify(body),
      });
      setForm(emptyApplicant);
      showNotice(
        kind === "students"
          ? "Student created."
          : kind === "candidates"
            ? "Candidate created."
            : "Recruiter created.",
      );
      await load();
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function removeUser(id: string) {
    if (!token) return;
    if (!window.confirm("Delete this account permanently?")) return;
    try {
      await api(`/admin/users/${kind}/${id}`, {
        ...auth(token.access_token),
        method: "DELETE",
      });
      showNotice("Account deleted.");
      await load();
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  const rows =
    kind === "students" ? students : kind === "candidates" ? candidates : recruiters;

  return (
    <section className="student-dashboard">
      <SectionHeading
        title="Gestion des utilisateurs"
        text="Créer et supprimer des comptes étudiants, candidats et recruteurs."
      />

      <div className="segmented">
        <button type="button" className={kind === "students" ? "active" : ""} onClick={() => setKind("students")}>
          Students ({students.length})
        </button>
        <button type="button" className={kind === "candidates" ? "active" : ""} onClick={() => setKind("candidates")}>
          Candidates ({candidates.length})
        </button>
        <button type="button" className={kind === "recruiters" ? "active" : ""} onClick={() => setKind("recruiters")}>
          Recruiters ({recruiters.length})
        </button>
      </div>

      <form className="job-composer admin-user-form" onSubmit={createUser}>
        <SectionHeading
          title={`Add ${kind === "students" ? "student" : kind === "candidates" ? "candidate" : "recruiter"}`}
          text="The account can sign in immediately with the password you set."
        />
        <div className="form-grid two">
          <input
            placeholder="First name"
            value={form.first_name}
            onChange={(event) => setForm({ ...form, first_name: event.target.value })}
            required
          />
          <input
            placeholder="Last name"
            value={form.last_name}
            onChange={(event) => setForm({ ...form, last_name: event.target.value })}
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            required
          />
          <input
            type="password"
            placeholder="Password (min 8)"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
            minLength={8}
            required
          />
          {kind === "recruiters" ? (
            <>
              <input
                placeholder="Company name"
                value={form.company_name}
                onChange={(event) => setForm({ ...form, company_name: event.target.value })}
                required
              />
              <input
                placeholder="Phone"
                value={form.phone}
                onChange={(event) => setForm({ ...form, phone: event.target.value })}
              />
            </>
          ) : (
            <>
              <input
                placeholder="University"
                value={form.university}
                onChange={(event) => setForm({ ...form, university: event.target.value })}
              />
              <input
                placeholder="Field of study"
                value={form.field_of_study}
                onChange={(event) => setForm({ ...form, field_of_study: event.target.value })}
              />
              {kind === "students" && (
                <>
                  <input
                    placeholder="Internship type"
                    value={form.internship_type}
                    onChange={(event) => setForm({ ...form, internship_type: event.target.value })}
                  />
                  <input
                    placeholder="Internship duration"
                    value={form.internship_duration}
                    onChange={(event) => setForm({ ...form, internship_duration: event.target.value })}
                  />
                </>
              )}
            </>
          )}
        </div>
        <button className="primary-button" type="submit">
          <Plus size={18} /> Create account
        </button>
      </form>

      <div className="job-stack">
        <SectionHeading
          title={`${kind[0].toUpperCase()}${kind.slice(1)} directory`}
          text="Delete removes related applications, meetings and saved jobs."
        />
        {rows.length === 0 ? (
          <p className="status-line">
            <Users size={16} /> No accounts in this category yet.
          </p>
        ) : (
          rows.map((row) => (
            <article className="job-card admin-user-row" key={row.id}>
              <div>
                <h3>
                  {row.first_name} {row.last_name}
                </h3>
                <p>{row.email}</p>
                {"company_name" in row ? (
                  <span>{(row as AdminRecruiterUser).company_name}</span>
                ) : (
                  <span>
                    {[
                      (row as AdminApplicant).university,
                      (row as AdminApplicant).field_of_study,
                    ]
                      .filter(Boolean)
                      .join(" · ") || "—"}
                  </span>
                )}
              </div>
              <button type="button" className="secondary-button danger-button" onClick={() => removeUser(row.id)}>
                <Trash2 size={16} /> Delete
              </button>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
