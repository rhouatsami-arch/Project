"use client";

import { InterviewsPanel } from "@/components/applicant/interviews-panel";

export default function CandidateInterviewsPage() {
  return (
    <InterviewsPanel
      apiBase="/candidates"
      meetingsPath="/meetings/candidates/me"
      availabilityListPath="/meetings/availability/me"
      availabilityCreatePath="/meetings/availability"
      confirmPath={(id) => `/meetings/${id}/confirm`}
      refusePath={(id) => `/meetings/${id}/refuse`}
    />
  );
}
