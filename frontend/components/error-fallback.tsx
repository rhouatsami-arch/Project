"use client";

type ErrorFallbackProps = {
  title: string;
  message: string;
  actionLabel?: string;
  onRetry: () => void;
  compact?: boolean;
};

export function ErrorFallback({
  title,
  message,
  actionLabel = "Reessayer",
  onRetry,
  compact = false,
}: ErrorFallbackProps) {
  if (compact) {
    return (
      <div style={{ maxWidth: 420, padding: 24, textAlign: "center" }}>
        <h1 style={{ margin: "0 0 12px", fontSize: 24 }}>{title}</h1>
        <p style={{ margin: "0 0 20px", opacity: 0.85 }}>{message}</p>
        <button
          type="button"
          onClick={onRetry}
          style={{
            border: 0,
            borderRadius: 999,
            padding: "10px 18px",
            background: "#2563eb",
            color: "#fff",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          {actionLabel}
        </button>
      </div>
    );
  }

  return (
    <section className="auth-stage">
      <div className="auth-card">
        <p className="eyebrow">Erreur</p>
        <h1>{title}</h1>
        <p className="status-line">{message}</p>
        <button className="primary-button" type="button" onClick={onRetry}>
          {actionLabel}
        </button>
      </div>
    </section>
  );
}
