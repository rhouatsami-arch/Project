import { ApplicantLayout } from "@/components/applicant/layout";

const config = {
  role: "candidate" as const,
  apiBase: "/candidates" as const,
  label: "Candidate workspace",
  subtitle: "Build your profile and apply to roles that match your skills.",
  basePath: "/candidate",
};

export default function CandidateLayout({ children }: { children: React.ReactNode }) {
  return <ApplicantLayout config={config}>{children}</ApplicantLayout>;
}
