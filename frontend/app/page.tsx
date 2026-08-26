"use client";

import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, CalendarClock, ShieldCheck, Sparkles, UserRound } from "lucide-react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { BrandLogo } from "@/components/brand-logo";
import { ThemeToggle } from "@/components/theme-toggle";
import { homeRouteForRole } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";

const highlights = [
  {
    title: "Matching intelligent",
    text: "Pipeline ML/NLP : TF-IDF, compétences, score multi-critères et classement automatique.",
    icon: Sparkles,
  },
  {
    title: "Pipeline recruteur",
    text: "Classement des candidats, suivi des candidatures et decisions plus rapides.",
    icon: BriefcaseBusiness,
  },
  {
    title: "Entretiens structures",
    text: "Planification, disponibilites, confirmation et historique des reunions.",
    icon: CalendarClock,
  },
];

const personas = [
  {
    title: "Etudiant",
    text: "Construire un profil clair, charger le CV et recevoir des recommandations adaptees.",
    icon: UserRound,
  },
  {
    title: "Candidat",
    text: "Postuler plus vite, suivre les entretiens et mieux comprendre le matching.",
    icon: Sparkles,
  },
  {
    title: "Recruteur",
    text: "Comparer les profils, piloter le pipeline et planifier les entretiens depuis un seul espace.",
    icon: BriefcaseBusiness,
  },
  {
    title: "Admin",
    text: "Superviser les utilisateurs, les activites et les indicateurs de la plateforme.",
    icon: ShieldCheck,
  },
];

export default function HomePage() {
  const router = useRouter();
  const { token, ready } = useAuth();

  useEffect(() => {
    if (!ready || !token) return;
    router.replace(homeRouteForRole(token.role));
  }, [ready, token, router]);

  if (ready && token) {
    return (
      <section className="home-stage">
        <div className="home-copy">
          <p className="eyebrow">MatiousHire platform</p>
          <h1>Redirection vers votre espace...</h1>
        </div>
      </section>
    );
  }

  return (
    <section className="home-stage">
      <header className="home-nav">
        <BrandLogo tagline="Smart recruitment for students and recruiters." />
        <div className="header-actions">
          <ThemeToggle />
          <Link className="ghost-button" href="/login">
            Login
          </Link>
          <Link className="primary-button" href="/login">
            Start now <ArrowRight size={17} />
          </Link>
        </div>
      </header>

      <div className="home-hero">
        <div className="home-copy">
          <p className="eyebrow">MatiousHire platform</p>
          <h1>Une page d&apos;accueil plus claire pour presenter la plateforme RH intelligente.</h1>
          <p className="home-lead">
            MatiousHire aide les etudiants, candidats et recruteurs a mieux se
            rencontrer grace au matching IA, au suivi des candidatures et a la
            planification intelligente des entretiens.
          </p>
          <div className="home-actions">
            <Link className="primary-button" href="/login">
              Acceder a la plateforme <ArrowRight size={17} />
            </Link>
            <Link className="secondary-button" href="/login">
              Creer un compte
            </Link>
          </div>
        </div>

        <aside className="home-summary">
          <p className="eyebrow">Vue d&apos;ensemble</p>
          <div className="home-summary-grid">
            <article>
              <strong>4 roles</strong>
              <span>Etudiant, candidat, recruteur, administrateur</span>
            </article>
            <article>
              <strong>IA explicable</strong>
              <span>Matching, score de compatibilite et aide a la decision</span>
            </article>
            <article>
              <strong>Entretiens</strong>
              <span>Disponibilites, proposition de creneau, confirmation</span>
            </article>
            <article>
              <strong>Suivi centralise</strong>
              <span>Pipeline, notifications et historique en un seul espace</span>
            </article>
          </div>
        </aside>
      </div>

      <section className="home-section">
        <div className="section-heading">
          <h2>Fonctionnalites principales</h2>
          <p>Une structure simple pour comprendre rapidement ce que fait la plateforme.</p>
        </div>
        <div className="home-grid home-grid--three">
          {highlights.map(({ title, text, icon: Icon }) => (
            <article className="home-card" key={title}>
              <Icon size={20} />
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-section">
        <div className="section-heading">
          <h2>Espaces utilisateurs</h2>
          <p>Chaque role dispose d&apos;un parcours adapte a ses besoins metier.</p>
        </div>
        <div className="home-grid home-grid--four">
          {personas.map(({ title, text, icon: Icon }) => (
            <article className="home-card" key={title}>
              <Icon size={20} />
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-cta">
        <div>
          <p className="eyebrow">Ready to explore</p>
          <h2>Connectez-vous pour acceder au dashboard correspondant a votre role.</h2>
        </div>
        <Link className="primary-button" href="/login">
          Ouvrir la connexion <ArrowRight size={17} />
        </Link>
      </section>
    </section>
  );
}
