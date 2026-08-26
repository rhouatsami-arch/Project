"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Check, FileUp, GraduationCap, UserRound } from "lucide-react";
import { Field, SectionHeading } from "@/components/ui";
import {
  api,
  auth,
  authHeader,
  emptyProfileForm,
  messageFromError,
  studentProfileScore,
  studentToForm,
} from "@/lib/api";
import {
  internshipDurationOptionsFor,
  internshipTypeOptionsFor,
  profileVariantConfig,
  type ApplicantApiBase,
} from "@/lib/applicant";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { CandidateProfile, ProfileForm, Student } from "@/types/recruitment";

type Profile = Student | CandidateProfile;

export function ApplicantProfilePanel({ apiBase }: { apiBase: ApplicantApiBase }) {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [profileForm, setProfileForm] = useState<ProfileForm>(emptyProfileForm());
  const config = profileVariantConfig(apiBase);
  const isStudent = apiBase === "/students";
  const RoleIcon = isStudent ? GraduationCap : UserRound;

  const loadProfile = useCallback(async () => {
    if (!token) return;
    const me = await api<Profile>(`${apiBase}/me`, auth(token.access_token));
    setProfile(me);
    setProfileForm(studentToForm(me));
  }, [apiBase, token]);

  useEffect(() => {
    loadProfile().catch((error) => showNotice(messageFromError(error)));
  }, [loadProfile, showNotice]);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    try {
      const updated = await api<Profile>(`${apiBase}/me`, {
        ...auth(token.access_token),
        method: "PATCH",
        body: JSON.stringify({ ...profileForm, skills: profileForm.technical_skills }),
      });
      setProfile(updated);
      setProfileForm(studentToForm(updated));
      showNotice("Profile saved.");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  async function uploadCv(file: File | null) {
    if (!file || !token) return;
    const body = new FormData();
    body.append("file", file);
    try {
      const result = await api<{ profile: Profile; skills_detected: string[]; extracted_char_count: number }>(
        `${apiBase}/me/cv`,
        {
          method: "POST",
          headers: authHeader(token.access_token),
          body,
        },
      );
      setProfile(result.profile);
      setProfileForm(studentToForm(result.profile));
      const skillsNote = result.skills_detected.length
        ? ` Skills detected: ${result.skills_detected.join(", ")}.`
        : "";
      showNotice(`CV uploaded.${skillsNote} (${result.extracted_char_count} chars extracted)`);
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  const profileScore = useMemo(() => studentProfileScore(profile), [profile]);
  const internshipTypeOptions = internshipTypeOptionsFor(apiBase);
  const internshipDurationOptions = internshipDurationOptionsFor(apiBase);

  return (
    <section className={`student-profile-grid profile-panel ${config.accentClass}`}>
      <aside className="profile-summary">
        <span className="profile-role-badge">
          <RoleIcon size={16} />
          {config.badge}
        </span>
        <div className="profile-ring">
          <span>{profileScore}%</span>
          <small>ready</small>
        </div>
        <div>
          <h2>{config.summaryTitle}</h2>
          <p>{config.summaryText}</p>
        </div>
        {profile && (
          <div className="profile-identity">
            <strong>
              {profile.first_name} {profile.last_name}
            </strong>
            {profile.university && <span>{profile.university}</span>}
            {profile.field_of_study && <span>{profile.field_of_study}</span>}
          </div>
        )}
        <ul className="profile-checklist">
          {config.checklist.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <label className="upload-button">
          <FileUp size={18} /> Upload CV
          <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={(event) => uploadCv(event.target.files?.[0] || null)} />
        </label>
        {profile?.cv_filename && <p className="file-note">{profile.cv_filename}</p>}
      </aside>

      <form className="profile-editor" onSubmit={saveProfile}>
        <div className="profile-diff-banner">
          {config.focusPoints.map((point) => (
            <div className="profile-diff-item" key={point.label}>
              <strong>{point.label}</strong>
              <span>{point.detail}</span>
            </div>
          ))}
        </div>

        <SectionHeading title={config.editorTitle} text={config.editorText} />

        <div className="form-grid two">
          <Field
            label="Technical skills"
            value={profileForm.technical_skills}
            onChange={(value) => setProfileForm({ ...profileForm, technical_skills: value })}
            placeholder={isStudent ? "Coursework, labs, tools you use in class" : "Python, FastAPI, PostgreSQL, React"}
          />
          <Field
            label="Soft skills"
            value={profileForm.soft_skills}
            onChange={(value) => setProfileForm({ ...profileForm, soft_skills: value })}
            placeholder="Communication, ownership, teamwork"
          />
          <Field
            label="Experience"
            value={profileForm.experiences}
            onChange={(value) => setProfileForm({ ...profileForm, experiences: value })}
            placeholder={config.experiencePlaceholder}
          />
          <Field
            label="Projects"
            value={profileForm.projects}
            onChange={(value) => setProfileForm({ ...profileForm, projects: value })}
            placeholder={config.projectsPlaceholder}
          />
          <Field
            label="Certifications"
            value={profileForm.certifications}
            onChange={(value) => setProfileForm({ ...profileForm, certifications: value })}
            placeholder="AWS, Cisco, Google, university certificates"
          />
          <Field
            label="Languages"
            value={profileForm.languages}
            onChange={(value) => setProfileForm({ ...profileForm, languages: value })}
            placeholder="Arabic, French, English"
          />
        </div>

        {isStudent && (
          <div className="profile-internship-section">
            <h3>{config.internshipSectionTitle}</h3>
            <div className="form-grid two">
              <label className="field">
                <span>{config.internshipTypeLabel}</span>
                <select
                  value={profileForm.internship_type}
                  onChange={(event) => setProfileForm({ ...profileForm, internship_type: event.target.value })}
                >
                  <option value="">Select internship type</option>
                  {internshipTypeOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Internship duration</span>
                <select
                  value={profileForm.internship_duration}
                  onChange={(event) => setProfileForm({ ...profileForm, internship_duration: event.target.value })}
                >
                  <option value="">Select duration</option>
                  {internshipDurationOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>
        )}

        <Field
          label="Short bio"
          value={profileForm.bio}
          onChange={(value) => setProfileForm({ ...profileForm, bio: value })}
          placeholder={config.bioPlaceholder}
        />
        <button className="primary-button" type="submit">
          <Check size={18} /> Save profile
        </button>
      </form>
    </section>
  );
}
