"use client";

import Link from "next/link";
import { LogOut } from "lucide-react";
import { BrandLogo } from "@/components/brand-logo";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/providers/auth-provider";

export function AppHeader({
  label,
  title,
  subtitle,
}: {
  label: string;
  title: string;
  subtitle: string;
}) {
  const { logout } = useAuth();

  return (
    <header className="app-header">
      <BrandLogo compact showTagline tagline={label} />
      <div>
        <p className="eyebrow">{label}</p>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="header-actions">
        <ThemeToggle />
        <button className="ghost-button" type="button" onClick={logout}>
          <LogOut size={18} /> Logout
        </button>
      </div>
    </header>
  );
}

export function SectionHeading({ title, text }: { title: string; text: string }) {
  return (
    <div className="section-heading">
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}

export function Field({
  label,
  value,
  placeholder,
  onChange,
}: {
  label: string;
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <textarea placeholder={placeholder} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

export function ProfileLine({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | null }) {
  if (!value) return null;
  return (
    <p className="profile-line">
      {icon}
      <strong>{label}:</strong> {value}
    </p>
  );
}

export function WorkspaceTab({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link className={active ? "active" : ""} href={href}>
      {children}
    </Link>
  );
}
