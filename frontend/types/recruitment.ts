export type Role = "student" | "candidate" | "recruiter" | "admin";

export type Token = {
  access_token: string;
  refresh_token?: string;
  role: Role;
};

export type LoginResponse = {
  access_token?: string | null;
  refresh_token?: string | null;
  token_type?: string;
  role?: Role | null;
  requires_2fa?: boolean;
  login_challenge?: string | null;
};

export type OAuthProvider = {
  id: string;
  name: string;
  enabled: boolean;
  authorize_path: string;
};

export type Job = {
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

export type Student = {
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
  internship_type: string | null;
  internship_duration: string | null;
  cv_filename: string | null;
};

export type Recruiter = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name: string;
  phone: string | null;
};

export type Application = {
  id: number;
  job_id: number;
  student_id: string;
  status: string;
  match_score: number;
  interview_at: string | null;
  created_at: string;
};

export type DashboardApplication = Application & {
  job_title: string;
  job_location: string | null;
  job_employment_type: string | null;
};

export type SavedJob = {
  id: number;
  job: Job;
  created_at: string;
};

export type StudentDashboard = {
  total_applications: number;
  interview_invites: number;
  saved_jobs_count: number;
  applications: DashboardApplication[];
  saved_jobs: SavedJob[];
};

export type CandidateDashboard = StudentDashboard;

export type CandidateProfile = {
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
  internship_type: string | null;
  internship_duration: string | null;
  cv_filename: string | null;
  created_at: string;
};

export type JobRecommendation = {
  job: Job;
  compatibility_score: number;
  rank_label: string;
  breakdown: {
    skills_score: number;
    experience_score: number;
    semantic_score: number;
    education_score: number;
    location_score: number;
    availability_score: number;
    matched_skills: string[];
    missing_skills: string[];
  };
  explanation: string;
};

export type PipelineCandidate = {
  application_id: number;
  id: string;
  first_name: string;
  last_name: string;
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
  rank?: number | null;
  rank_label?: string | null;
  breakdown?: JobRecommendation["breakdown"] | null;
  explanation?: string | null;
};

export type MatchingPipelineInfo = {
  title: string;
  version: string;
  description: string;
  formula: string;
  weights: Record<string, number>;
  stages: { name: string; description: string; technique: string }[];
  algorithms: string[];
  rank_labels: Record<string, string>;
};

export type CandidateRanking = {
  application_id: number;
  student_id: string;
  first_name: string;
  last_name: string;
  email: string;
  compatibility_score: number;
  rank: number;
  rank_label: string;
  breakdown: JobRecommendation["breakdown"];
  explanation: string;
};

export type RecruiterDashboard = {
  open_jobs: number;
  closed_jobs: number;
  total_applications: number;
  applied_count: number;
  shortlisted_count: number;
  interview_count: number;
  rejected_count: number;
  hired_count: number;
  upcoming_meetings: number;
  average_match_score: number;
  recent_applications: {
    application_id: number;
    job_id: number;
    job_title: string;
    candidate_name: string;
    candidate_email: string;
    status: string;
    match_score: number;
    created_at: string;
  }[];
  upcoming_meeting_list: {
    meeting_id: number;
    job_id: number;
    scheduled_at: string;
    status: string;
    location: string | null;
    candidate_name: string;
  }[];
};

export type AdminDashboard = {
  total_students: number;
  total_candidates: number;
  total_recruiters: number;
  total_jobs: number;
  total_applications: number;
  total_meetings: number;
  total_recommendations: number;
  recent_audit_logs: AuditLogEntry[];
};

export type AuditLogEntry = {
  id: number;
  actor_email: string;
  actor_role: string;
  action: string;
  action_label?: string | null;
  resource: string | null;
  details: string | null;
  created_at: string;
};

export type AdminApplicant = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  university: string | null;
  field_of_study: string | null;
  account_kind: string;
  created_at: string;
};

export type AdminRecruiterUser = {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name: string;
  phone: string | null;
  created_at: string;
};

export type Meeting = {
  id: number;
  application_id: number;
  job_id: number;
  scheduled_at: string;
  location: string | null;
  notes: string | null;
  status: string;
  slot_id?: number | null;
  updated_at?: string | null;
  google_event_link?: string | null;
  google_meet_link?: string | null;
};

export type GoogleCalendarStatus = {
  configured: boolean;
  connected: boolean;
  google_email?: string | null;
};

export type InterviewSlot = {
  id: number;
  starts_at: string;
  ends_at: string;
  is_booked: boolean;
};

export type CandidateAvailability = {
  id: number;
  starts_at: string;
  ends_at: string;
};

export type LlmExplanation = {
  compatibility_score: number;
  rank_label: string;
  explanation: string;
  cv_summary: string;
  job_summary: string;
  matched_skills: string[];
  missing_skills: string[];
  strengths: string[];
  score_justification: string;
  improvement_tips: string[];
  interview_questions: string[];
  disclaimer: string;
  confidence_score: number;
  grounded: boolean;
  guard_warnings: string[];
  grounded_sources: string[];
};

export type ProfileForm = {
  technical_skills: string;
  soft_skills: string;
  experiences: string;
  projects: string;
  certifications: string;
  languages: string;
  bio: string;
  internship_type: string;
  internship_duration: string;
};
