type ScoreBreakdown = {
  skills_score: number;
  experience_score: number;
  semantic_score: number;
  education_score: number;
  location_score: number;
  availability_score: number;
  matched_skills: string[];
  missing_skills: string[];
};

const DIMENSIONS: { key: keyof ScoreBreakdown; label: string }[] = [
  { key: "skills_score", label: "Compétences" },
  { key: "experience_score", label: "Expérience" },
  { key: "semantic_score", label: "Sémantique TF-IDF" },
  { key: "education_score", label: "Formation" },
  { key: "location_score", label: "Localisation" },
  { key: "availability_score", label: "Disponibilité" },
];

export function MatchScoreBreakdown({
  breakdown,
  explanation,
}: {
  breakdown: ScoreBreakdown;
  explanation?: string | null;
}) {
  return (
    <div className="match-breakdown">
      {explanation ? <p className="match-breakdown-explanation">{explanation}</p> : null}
      <ul className="match-breakdown-list">
        {DIMENSIONS.map((dimension) => {
          const value = breakdown[dimension.key];
          if (typeof value !== "number") return null;
          return (
            <li key={dimension.key}>
              <span>{dimension.label}</span>
              <strong>{value}%</strong>
              <span className="match-breakdown-bar" aria-hidden>
                <span style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
              </span>
            </li>
          );
        })}
      </ul>
      {breakdown.matched_skills.length > 0 ? (
        <p className="match-breakdown-skills ok">
          Match : {breakdown.matched_skills.join(", ")}
        </p>
      ) : null}
      {breakdown.missing_skills.length > 0 ? (
        <p className="match-breakdown-skills miss">
          Manquantes : {breakdown.missing_skills.join(", ")}
        </p>
      ) : null}
    </div>
  );
}
