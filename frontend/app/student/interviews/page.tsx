"use client";

import { InterviewsPanel } from "@/components/applicant/interviews-panel";

export default function StudentInterviewsPage() {
  return (
    <InterviewsPanel
      apiBase="/students"
      meetingsPath="/meetings/students/me"
      availabilityListPath="/meetings/students/availability/me"
      availabilityCreatePath="/meetings/students/availability"
      confirmPath={(id) => `/meetings/students/${id}/confirm`}
      refusePath={(id) => `/meetings/students/${id}/refuse`}
    />
  );
}
