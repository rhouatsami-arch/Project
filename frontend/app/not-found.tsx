import Link from "next/link";

export default function NotFound() {
  return (
    <section className="auth-stage">
      <div className="auth-card">
        <p className="eyebrow">404</p>
        <h1>Page introuvable</h1>
        <p className="status-line">Cette page n&apos;existe pas ou a ete deplacee.</p>
        <Link className="primary-button" href="/">
          Retour a l&apos;accueil
        </Link>
      </div>
    </section>
  );
}
