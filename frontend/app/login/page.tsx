"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AuthExperience } from "@/components/auth-experience";
import { homeRouteForRole } from "@/lib/api";
import { useAuth } from "@/providers/auth-provider";

export default function LoginPage() {
  const router = useRouter();
  const { token, ready } = useAuth();

  useEffect(() => {
    if (!ready || !token) return;
    router.replace(homeRouteForRole(token.role));
  }, [ready, token, router]);

  // Pendant l'hydratation auth, on affiche un etat de chargement
  // (evite une page blanche qui peut etre prise pour une erreur).
  if (!ready) {
    return (
      <section className="auth-stage" aria-busy="true">
        <div className="auth-intro">
          <p className="eyebrow">MatiousHire</p>
          <h1>Chargement de la session...</h1>
        </div>
        <div className="auth-card">
          <p className="status-line">Preparation de la connexion</p>
        </div>
      </section>
    );
  }

  // Deja connecte : redirection en cours.
  if (token) {
    return (
      <section className="auth-stage" aria-busy="true">
        <div className="auth-card">
          <p className="status-line">Redirection vers votre espace...</p>
        </div>
      </section>
    );
  }

  return <AuthExperience />;
}
