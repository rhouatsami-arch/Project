"use client";

import { useEffect } from "react";
import { ErrorFallback } from "@/components/error-fallback";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          fontFamily: "system-ui, sans-serif",
          background: "#0f172a",
          color: "#f8fafc",
        }}
      >
        <ErrorFallback
          compact
          title="MatiousHire"
          message="Une erreur inattendue est survenue. Rechargez la page pour continuer."
          onRetry={reset}
        />
      </body>
    </html>
  );
}
