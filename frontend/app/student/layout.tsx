import { ApplicantLayout } from "@/components/applicant/layout";

const config = {
  role: "student" as const,
  apiBase: "/students" as const,
  label: "Student workspace",
  subtitle: "Complete your profile, then apply with confidence.",
  basePath: "/student",
};

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  return <ApplicantLayout config={config}>{children}</ApplicantLayout>;
}
