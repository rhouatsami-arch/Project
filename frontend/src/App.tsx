import {
  BriefcaseBusiness,
  CalendarClock,
  Check,
  ClipboardList,
  FileUp,
  Filter,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  Mail,
  Plus,
  Search,
  Send,
  Sparkles,
  Star,
  UserRound,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

type Role = "student" | "recruiter";
type Mode = "login" | "register";
type StudentTab = "profile" | "jobs";
type RecruiterTab = "pipeline" | "jobs";

type Token = {
  access_token: string;
  role: Role;
};

type Job = {
  id: number;
  recruiter_id: string;
  title: string;
  description: string;
  required_skills: string | null;
  location: string | null;
  employment_type: string | null;
  status: "open" | "closed";
  created_at: string;
};

type Student = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  university: string | null;
  field_of_study: string | null;
  graduation_year: number | null;
  bio: string | null;
  skills: string | null;
  technical_skills: string | null;
  soft_skills: string | null;
  experiences: string | null;
  projects: string | null;
  certifications: string | null;
  languages: string | null;
  cv_filename: string | null;
};

type Recruiter = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name: string;
  phone: string | null;
};

type Application = {
  id: number;
  job_id: number;
  student_id: string;
  status: string;
  match_score: number;
  interview_at: string | null;
  created_at: string;
};

type SavedJob = {
  id: number;
  job: Job;
  created_at: string;
};

type Candidate = {
  application_id: number;
  student_id: string;
  full_name: string;
  email: string;
  phone: string | null;
  university: string | null;
  field_of_study: string | null;
  skills: string | null;
  technical_skills: string | null;
  soft_skills: string | null;
  experiences: string | null;
  projects: string | null;
  certifications: string | null;
  languages: string | null;
  cv_filename: string | null;
  application_status: string;
  match_score: number;
};

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [token, setToken] = useState<Token | null>(() => {
    const stored = localStorage.getItem("recruitment_token");
    return stored ? JSON.parse(stored) : null;
  });
  const [notice, setNotice] = useState("");

  function saveToken(next: Token) {
    setToken(next);
    localStorage.setItem("recruitment_token", JSON.stringify(next));
  }

  function logout() {
    setToken(null);
    localStorage.removeItem("recruitment_token");
  }

  return (
    <main className="app-shell">
      {notice && <div className="notice">{notice}</div>}
      {!token ? (
        <AuthExperience onToken={saveToken} onNotice={setNotice} />
      ) : token.role === "student" ? (
        <StudentWorkspace token={token.access_token} onNotice={setNotice} onLogout={logout} />
      ) : (
        <RecruiterWorkspace token={token.access_token} onNotice={setNotice} onLogout={logout} />
      )}
    </main>
  );
}

function AuthExperience({
  onToken,
  onNotice,
}: {
  onToken: (token: Token) => void;
  onNotice: (message: string) => void;
}) {
  const [role, setRole] = useState<Role>("student");
  const [mode, setMode] = useState<Mode>("login");
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    company_name: "",
    university: "",
    field_of_study: "",
  });

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      if (mode === "register") {
        await api(role === "student" ? "/auth/students/register" : "/auth/recruiters/register", {
          method: "POST",
          body: JSON.stringify(role === "student" ? studentPayload(form) : recruiterPayload(form)),
        });
      }

      const body = new URLSearchParams();
      body.set("username", form.email);
      body.set("password", form.password);
      const nextToken = await api<Token>("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      onToken(nextToken);
      onNotice(mode === "register" ? "Account created." : "Logged in.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  return (
    <section className="auth-stage">
      <div className="auth-intro">
        <div className="brand-row">
          <div className="brand-mark">R</div>
          <div>
            <strong>Recruitment Workspace</strong>
            <span>Student profiles. Recruiter pipelines.</span>
          </div>
        </div>
        <p className="eyebrow">{role === "student" ? "Student access" : "Recruiter access"}</p>
        <h1>{role === "student" ? "Build a profile recruiters can trust." : "Move from applicants to interviews faster."}</h1>
      </div>

      <form className="auth-card" onSubmit={submit}>
        <div className="choice-grid">
          <button type="button" className={role === "student" ? "selected" : ""} onClick={() => setRole("student")}>
            <GraduationCap size={20} />
            <strong>Student</strong>
            <span>Profile and jobs</span>
          </button>
          <button type="button" className={role === "recruiter" ? "selected" : ""} onClick={() => setRole("recruiter")}>
            <BriefcaseBusiness size={20} />
            <strong>Recruiter</strong>
            <span>Jobs and candidates</span>
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
            {role === "student" ? (
              <>
                <input placeholder="University" value={form.university} onChange={(event) => setForm({ ...form, university: event.target.value })} />
                <input placeholder="Field of study" value={form.field_of_study} onChange={(event) => setForm({ ...form, field_of_study: event.target.value })} />
              </>
            ) : (
              <input placeholder="Company name" value={form.company_name} onChange={(event) => setForm({ ...form, company_name: event.target.value })} />
            )}
          </div>
        )}

        <input type="email" placeholder="Email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
        <input type="password" placeholder="Password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
        <button className="primary-button" type="submit">
          <Check size={18} /> {mode === "register" ? "Create account" : "Enter workspace"}
        </button>
      </form>
    </section>
  );
}

function StudentWorkspace({
  token,
  onNotice,
  onLogout,
}: {
  token: string;
  onNotice: (message: string) => void;
  onLogout: () => void;
}) {
  const [tab, setTab] = useState<StudentTab>("profile");
  const [profile, setProfile] = useState<Student | null>(null);
  const [profileForm, setProfileForm] = useState(emptyProfileForm());
  const [jobs, setJobs] = useState<Job[]>([]);
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [filters, setFilters] = useState({ search: "", location: "", skill: "" });

  async function refresh() {
    const query = new URLSearchParams(stripEmpty(filters));
    const [me, jobList, saved, apps] = await Promise.all([
      api<Student>("/students/me", auth(token)),
      api<Job[]>(`/jobs/?${query}`, auth(token)),
      api<SavedJob[]>("/students/me/saved-jobs", auth(token)),
      api<Application[]>("/students/me/applications", auth(token)),
    ]);
    setProfile(me);
    setProfileForm(studentToForm(me));
    setJobs(jobList);
    setSavedJobs(saved);
    setApplications(apps);
  }

  useEffect(() => {
    refresh().catch((error) => onNotice(messageFromError(error)));
  }, []);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    try {
      const updated = await api<Student>("/students/me", {
        ...auth(token),
        method: "PATCH",
        body: JSON.stringify({ ...profileForm, skills: profileForm.technical_skills }),
      });
      setProfile(updated);
      setProfileForm(studentToForm(updated));
      onNotice("Profile saved.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  async function uploadCv(file: File | null) {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    try {
      const updated = await api<Student>("/students/me/cv", {
        method: "POST",
        headers: authHeader(token),
        body,
      });
      setProfile(updated);
      setProfileForm(studentToForm(updated));
      onNotice("CV uploaded and skills updated.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  async function apply(jobId: number) {
    try {
      await api(`/students/jobs/${jobId}/apply`, { ...auth(token), method: "POST", body: JSON.stringify({ cover_letter: "" }) });
      await refresh();
      onNotice("Application sent.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  async function save(jobId: number) {
    try {
      await api(`/students/jobs/${jobId}/save`, { ...auth(token), method: "POST" });
      await refresh();
      onNotice("Job saved.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  const appliedIds = new Set(applications.map((application) => application.job_id));
  const savedIds = new Set(savedJobs.map((saved) => saved.job.id));
  const profileScore = useMemo(() => studentProfileScore(profile), [profile]);

  return (
    <div className="workspace-shell">
      <AppHeader
        label="Student workspace"
        title={profile ? `${profile.first_name} ${profile.last_name}` : "Student"}
        subtitle="Complete your profile, then apply with confidence."
        onLogout={onLogout}
      />
      <div className="workspace-tabs">
        <button className={tab === "profile" ? "active" : ""} onClick={() => setTab("profile")}>
          <UserRound size={18} /> Profile
        </button>
        <button className={tab === "jobs" ? "active" : ""} onClick={() => setTab("jobs")}>
          <BriefcaseBusiness size={18} /> Jobs
        </button>
      </div>

      {tab === "profile" ? (
        <section className="student-profile-grid">
          <aside className="profile-summary">
            <div className="profile-ring">
              <span>{profileScore}%</span>
              <small>ready</small>
            </div>
            <div>
              <h2>Profile strength</h2>
              <p>Recruiters need fast signals: technical skills, proof of work, soft skills, and a readable CV.</p>
            </div>
            <label className="upload-button">
              <FileUp size={18} /> Upload CV
              <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={(event) => uploadCv(event.target.files?.[0] || null)} />
            </label>
            {profile?.cv_filename && <p className="file-note">{profile.cv_filename}</p>}
          </aside>

          <form className="profile-editor" onSubmit={saveProfile}>
            <SectionHeading title="Student details" text="This is the information recruiters will scan before inviting you." />
            <div className="form-grid two">
              <Field label="Technical skills" value={profileForm.technical_skills} onChange={(value) => setProfileForm({ ...profileForm, technical_skills: value })} placeholder="Python, FastAPI, PostgreSQL, React" />
              <Field label="Soft skills" value={profileForm.soft_skills} onChange={(value) => setProfileForm({ ...profileForm, soft_skills: value })} placeholder="Communication, ownership, teamwork" />
              <Field label="Experience" value={profileForm.experiences} onChange={(value) => setProfileForm({ ...profileForm, experiences: value })} placeholder="Internships, freelance, volunteering, responsibilities" />
              <Field label="Projects" value={profileForm.projects} onChange={(value) => setProfileForm({ ...profileForm, projects: value })} placeholder="Project name, stack, what you shipped, outcome" />
              <Field label="Certifications" value={profileForm.certifications} onChange={(value) => setProfileForm({ ...profileForm, certifications: value })} placeholder="AWS, Cisco, Google, university certificates" />
              <Field label="Languages" value={profileForm.languages} onChange={(value) => setProfileForm({ ...profileForm, languages: value })} placeholder="Arabic, French, English" />
            </div>
            <Field label="Short bio" value={profileForm.bio} onChange={(value) => setProfileForm({ ...profileForm, bio: value })} placeholder="A short summary of what you can do and what you are looking for." />
            <button className="primary-button" type="submit">
              <Check size={18} /> Save profile
            </button>
          </form>
        </section>
      ) : (
        <section className="jobs-experience">
          <div className="jobs-toolbar">
            <div>
              <p className="eyebrow">Opportunities</p>
              <h2>Available jobs</h2>
            </div>
            <div className="filter-bar">
              <input placeholder="Search" value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} />
              <input placeholder="Location" value={filters.location} onChange={(event) => setFilters({ ...filters, location: event.target.value })} />
              <input placeholder="Skill" value={filters.skill} onChange={(event) => setFilters({ ...filters, skill: event.target.value })} />
              <button className="icon-button" onClick={() => refresh().catch((error) => onNotice(messageFromError(error)))}>
                <Filter size={18} />
              </button>
            </div>
          </div>
          <div className="jobs-grid">
            {jobs.map((job) => (
              <article className="job-card" key={job.id}>
                <p className="eyebrow">{job.location || "Remote"} · {job.employment_type || "full time"}</p>
                <h3>{job.title}</h3>
                <p>{job.description}</p>
                <div className="chips">{chips(job.required_skills)}</div>
                <div className="card-actions">
                  <button className="secondary-button" disabled={savedIds.has(job.id)} onClick={() => save(job.id)}>
                    <Star size={17} /> {savedIds.has(job.id) ? "Saved" : "Save"}
                  </button>
                  <button className="primary-button" disabled={appliedIds.has(job.id)} onClick={() => apply(job.id)}>
                    <Send size={17} /> {appliedIds.has(job.id) ? "Applied" : "Apply"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function RecruiterWorkspace({
  token,
  onNotice,
  onLogout,
}: {
  token: string;
  onNotice: (message: string) => void;
  onLogout: () => void;
}) {
  const [tab, setTab] = useState<RecruiterTab>("pipeline");
  const [profile, setProfile] = useState<Recruiter | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobForm, setJobForm] = useState({
    title: "",
    description: "",
    required_skills: "",
    location: "",
    employment_type: "full_time",
  });

  async function refresh() {
    const [me, myJobs] = await Promise.all([api<Recruiter>("/recruiters/me", auth(token)), api<Job[]>("/jobs/recruiter/me", auth(token))]);
    setProfile(me);
    setJobs(myJobs);
    const nextSelected = selectedJobId || myJobs[0]?.id || null;
    setSelectedJobId(nextSelected);
    if (nextSelected) await loadCandidates(nextSelected);
  }

  async function loadCandidates(jobId: number) {
    setCandidates(await api<Candidate[]>(`/recruiters/jobs/${jobId}/candidates`, auth(token)));
  }

  useEffect(() => {
    refresh().catch((error) => onNotice(messageFromError(error)));
  }, []);

  async function createJob(event: FormEvent) {
    event.preventDefault();
    try {
      await api("/jobs/", { ...auth(token), method: "POST", body: JSON.stringify(jobForm) });
      setJobForm({ title: "", description: "", required_skills: "", location: "", employment_type: "full_time" });
      await refresh();
      setTab("pipeline");
      onNotice("Job created.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  async function shortlist(applicationId: number) {
    try {
      await api(`/recruiters/applications/${applicationId}/shortlist`, { ...auth(token), method: "POST" });
      if (selectedJobId) await loadCandidates(selectedJobId);
      onNotice("Candidate shortlisted.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  async function invite(applicationId: number) {
    try {
      await api(`/recruiters/applications/${applicationId}/invite`, {
        ...auth(token),
        method: "POST",
        body: JSON.stringify({
          interview_at: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(),
          message: "Please join us for an interview.",
        }),
      });
      if (selectedJobId) await loadCandidates(selectedJobId);
      onNotice("Interview invite sent.");
    } catch (error) {
      onNotice(messageFromError(error));
    }
  }

  return (
    <div className="workspace-shell">
      <AppHeader
        label="Recruiter workspace"
        title={profile?.company_name || "Hiring desk"}
        subtitle="Post roles, compare applicants, and move the right students to interviews."
        onLogout={onLogout}
      />
      <div className="workspace-tabs">
        <button className={tab === "pipeline" ? "active" : ""} onClick={() => setTab("pipeline")}>
          <LayoutDashboard size={18} /> Pipeline
        </button>
        <button className={tab === "jobs" ? "active" : ""} onClick={() => setTab("jobs")}>
          <Plus size={18} /> Create job
        </button>
      </div>

      {tab === "jobs" ? (
        <form className="job-composer" onSubmit={createJob}>
          <SectionHeading title="Create a focused role" text="Clear required skills make candidate ranking more useful." />
          <div className="form-grid two">
            <input placeholder="Job title" value={jobForm.title} onChange={(event) => setJobForm({ ...jobForm, title: event.target.value })} required />
            <input placeholder="Location" value={jobForm.location} onChange={(event) => setJobForm({ ...jobForm, location: event.target.value })} />
            <input placeholder="Required skills" value={jobForm.required_skills} onChange={(event) => setJobForm({ ...jobForm, required_skills: event.target.value })} />
            <select value={jobForm.employment_type} onChange={(event) => setJobForm({ ...jobForm, employment_type: event.target.value })}>
              <option value="full_time">Full time</option>
              <option value="internship">Internship</option>
              <option value="part_time">Part time</option>
              <option value="remote">Remote</option>
            </select>
          </div>
          <textarea placeholder="Role description" value={jobForm.description} onChange={(event) => setJobForm({ ...jobForm, description: event.target.value })} required />
          <button className="primary-button" type="submit">
            <Plus size={18} /> Publish job
          </button>
        </form>
      ) : (
        <section className="recruiter-pipeline">
          <aside className="job-stack">
            <SectionHeading title="Open roles" text={`${jobs.length} roles in this workspace`} />
            {jobs.map((job) => (
              <button
                className={`job-row ${selectedJobId === job.id ? "active" : ""}`}
                key={job.id}
                onClick={() => {
                  setSelectedJobId(job.id);
                  loadCandidates(job.id).catch((error) => onNotice(messageFromError(error)));
                }}
              >
                <strong>{job.title}</strong>
                <span>{job.required_skills || "No skills listed"}</span>
              </button>
            ))}
          </aside>
          <div className="candidate-board">
            <SectionHeading title="Candidate shortlist" text="Ranked by overlap with the role's required technical skills." />
            <div className="candidate-grid">
              {candidates.map((candidate) => (
                <article className="candidate-card" key={candidate.application_id}>
                  <div className="candidate-head">
                    <div>
                      <h3>{candidate.full_name}</h3>
                      <p>{candidate.email}</p>
                    </div>
                    <span className="score">{candidate.match_score}%</span>
                  </div>
                  <div className="chips">{chips(candidate.technical_skills || candidate.skills)}</div>
                  <ProfileLine icon={<Sparkles size={16} />} label="Soft" value={candidate.soft_skills} />
                  <ProfileLine icon={<ClipboardList size={16} />} label="Projects" value={candidate.projects} />
                  <ProfileLine icon={<CalendarClock size={16} />} label="Experience" value={candidate.experiences} />
                  <p className="status-line">{candidate.application_status}</p>
                  <div className="card-actions">
                    <button className="secondary-button" onClick={() => shortlist(candidate.application_id)}>
                      <CalendarClock size={17} /> Shortlist
                    </button>
                    <button className="primary-button" onClick={() => invite(candidate.application_id)}>
                      <Mail size={17} /> Invite
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}

function AppHeader({ label, title, subtitle, onLogout }: { label: string; title: string; subtitle: string; onLogout: () => void }) {
  return (
    <header className="app-header">
      <div className="brand-row compact">
        <div className="brand-mark">R</div>
        <div>
          <strong>Recruitment</strong>
          <span>{label}</span>
        </div>
      </div>
      <div>
        <p className="eyebrow">{label}</p>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <button className="ghost-button" onClick={onLogout}>
        <LogOut size={18} /> Logout
      </button>
    </header>
  );
}

function SectionHeading({ title, text }: { title: string; text: string }) {
  return (
    <div className="section-heading">
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}

function Field({ label, value, placeholder, onChange }: { label: string; value: string; placeholder: string; onChange: (value: string) => void }) {
  return (
    <label className="field">
      <span>{label}</span>
      <textarea placeholder={placeholder} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function ProfileLine({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | null }) {
  if (!value) return null;
  return (
    <p className="profile-line">
      {icon}
      <strong>{label}:</strong> {value}
    </p>
  );
}

function chips(value: string | null) {
  return (value || "")
    .split(",")
    .map((chip) => chip.trim())
    .filter(Boolean)
    .slice(0, 8)
    .map((chip) => <span key={chip}>{chip}</span>);
}

function studentProfileScore(profile: Student | null) {
  if (!profile) return 0;
  const fields = [
    profile.technical_skills,
    profile.soft_skills,
    profile.experiences,
    profile.projects,
    profile.bio,
    profile.cv_filename,
  ];
  return Math.round((fields.filter(Boolean).length / fields.length) * 100);
}

function emptyProfileForm() {
  return {
    technical_skills: "",
    soft_skills: "",
    experiences: "",
    projects: "",
    certifications: "",
    languages: "",
    bio: "",
  };
}

function studentToForm(student: Student) {
  return {
    technical_skills: student.technical_skills || student.skills || "",
    soft_skills: student.soft_skills || "",
    experiences: student.experiences || "",
    projects: student.projects || "",
    certifications: student.certifications || "",
    languages: student.languages || "",
    bio: student.bio || "",
  };
}

function skillCount(value?: string | null) {
  return value ? value.split(",").filter((skill) => skill.trim()).length : 0;
}

function studentPayload(form: Record<string, string>) {
  return {
    email: form.email,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
    university: form.university || null,
    field_of_study: form.field_of_study || null,
  };
}

function recruiterPayload(form: Record<string, string>) {
  return {
    email: form.email,
    password: form.password,
    first_name: form.first_name,
    last_name: form.last_name,
    company_name: form.company_name,
  };
}

function stripEmpty(values: Record<string, string>) {
  return Object.fromEntries(Object.entries(values).filter(([, value]) => value.trim()));
}

function auth(token: string): RequestInit {
  return { headers: { ...authHeader(token), "Content-Type": "application/json" } };
}

function authHeader(token: string) {
  return { Authorization: `Bearer ${token}` };
}

async function api<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(init.headers || {}),
    },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

function messageFromError(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong";
}

export default App;
