"use client";

import { FormEvent, useState } from "react";
import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { SectionHeading } from "@/components/ui";
import { api, auth, messageFromError } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";

export default function RecruiterJobsPage() {
  const router = useRouter();
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [jobForm, setJobForm] = useState({
    title: "",
    description: "",
    required_skills: "",
    location: "",
    employment_type: "full_time",
  });

  async function createJob(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    try {
      await api("/jobs/", { ...auth(token.access_token), method: "POST", body: JSON.stringify(jobForm) });
      setJobForm({ title: "", description: "", required_skills: "", location: "", employment_type: "full_time" });
      showNotice("Job created.");
      router.push("/recruiter/pipeline");
    } catch (error) {
      showNotice(messageFromError(error));
    }
  }

  return (
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
  );
}
