"use client";

import { useEffect } from "react";
import { ErrorFallback } from "@/components/error-fallback";

export default function Error({
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
    <ErrorFallback
      title="Impossible de charger cette page"
      message="Un probleme temporaire est survenu. Reessayez dans quelques secondes."
      onRetry={reset}
    />
  );
}
