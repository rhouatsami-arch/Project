export type ApplicantApiBase = "/students" | "/candidates";
export type ApplicantVariant = "student" | "candidate";

export function applicantApiBase(role: "student" | "candidate"): ApplicantApiBase {
  return role === "candidate" ? "/candidates" : "/students";
}

export function variantFromApiBase(apiBase: ApplicantApiBase): ApplicantVariant {
  return apiBase === "/candidates" ? "candidate" : "student";
}

export const INTERNSHIP_TYPE_OPTIONS = [
  "Observation internship",
  "Operational internship",
  "Functional internship",
] as const;

export const STUDENT_INTERNSHIP_TYPE_OPTIONS = [
  "Observation internship",
  "Operational internship",
  "Functional internship",
] as const;

export const INTERNSHIP_DURATION_OPTIONS = [
  "Short-term (1 to 2 weeks)",
  "Lasting 1 to 3 months",
  "Duration of 4 to 6 months",
] as const;

export const STUDENT_INTERNSHIP_DURATION_OPTIONS = [
  "Short-term (1 to 2 weeks)",
  "Lasting 1 to 3 months",
  "Duration of 4 to 6 months",
] as const;

export function internshipTypeOptionsFor(apiBase: ApplicantApiBase) {
  return apiBase === "/students" ? STUDENT_INTERNSHIP_TYPE_OPTIONS : INTERNSHIP_TYPE_OPTIONS;
}

export function internshipDurationOptionsFor(apiBase: ApplicantApiBase) {
  return apiBase === "/students" ? STUDENT_INTERNSHIP_DURATION_OPTIONS : INTERNSHIP_DURATION_OPTIONS;
}

export type ProfileVariantConfig = {
  badge: string;
  accentClass: string;
  summaryTitle: string;
  summaryText: string;
  editorTitle: string;
  editorText: string;
  internshipSectionTitle: string;
  internshipTypeLabel: string;
  checklist: string[];
  focusPoints: { label: string; detail: string }[];
  bioPlaceholder: string;
  experiencePlaceholder: string;
  projectsPlaceholder: string;
};

export const PROFILE_VARIANT_CONFIG: Record<ApplicantVariant, ProfileVariantConfig> = {
  student: {
    badge: "Student profile",
    accentClass: "profile-panel--student",
    summaryTitle: "Academic readiness",
    summaryText:
      "Build a profile that highlights your studies, campus projects, and early internship experience for recruiters visiting campuses.",
    editorTitle: "Student details",
    editorText: "Focus on what you are learning now and the observation, operational or functional internships you are open to.",
    internshipSectionTitle: "School internship preferences",
    internshipTypeLabel: "Internship type (student)",
    checklist: [
      "Add university and field of study during registration",
      "Upload a CV or list skills from coursework",
      "Choose observation, operational or functional internship",
    ],
    focusPoints: [
      { label: "Goal", detail: "Show academic potential and learning path" },
      { label: "Internships", detail: "Observation, operational & functional" },
      { label: "Best for", detail: "Students still in school or university" },
    ],
    bioPlaceholder: "What you study, what you enjoy building, and the kind of internship you want while studying.",
    experiencePlaceholder: "School projects, clubs, volunteering, part-time work, responsibilities",
    projectsPlaceholder: "Course projects, hackathons, personal builds, team assignments",
  },
  candidate: {
    badge: "Candidate profile",
    accentClass: "profile-panel--candidate",
    summaryTitle: "Career readiness",
    summaryText:
      "Present a job-ready profile with proven experience and skills recruiters use to shortlist applicants.",
    editorTitle: "Candidate details",
    editorText: "Highlight experience, projects, and the skills that make you hire-ready.",
    internshipSectionTitle: "Career preferences",
    internshipTypeLabel: "Internship type",
    checklist: [
      "Complete technical and soft skills",
      "Add real projects and work experience",
      "Upload a clear CV recruiters can scan quickly",
    ],
    focusPoints: [
      { label: "Goal", detail: "Prove you are ready to be hired or placed" },
      { label: "Profile", detail: "Skills, projects and professional experience" },
      { label: "Best for", detail: "Graduates and active job seekers" },
    ],
    bioPlaceholder: "Your professional summary: strengths, target roles, and what you bring to a team.",
    experiencePlaceholder: "Jobs, freelance work, leadership roles, measurable outcomes",
    projectsPlaceholder: "Production apps, client work, open source, portfolio highlights",
  },
};

export function profileVariantConfig(apiBase: ApplicantApiBase): ProfileVariantConfig {
  return PROFILE_VARIANT_CONFIG[variantFromApiBase(apiBase)];
}

export function matchingApiBase(apiBase: ApplicantApiBase): "/matching/students" | "/matching/candidates" {
  return apiBase === "/candidates" ? "/matching/candidates" : "/matching/students";
}
