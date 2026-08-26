"use client";

import { Brain, ShieldCheck, Sparkles } from "lucide-react";
import type { LlmExplanation } from "@/types/recruitment";

export function LlmExplanationPanel({ insight }: { insight: LlmExplanation }) {
  return (
    <div className="job-card" style={{ marginTop: "0.75rem", background: "var(--surface-muted, #f8fafc)" }}>
      <p className="eyebrow">
        <Brain size={14} style={{ display: "inline", verticalAlign: "middle" }} /> Explication IA — {insight.rank_label}
      </p>
      <p style={{ fontSize: "0.92rem", lineHeight: 1.5 }}>{insight.explanation}</p>

      <div
        style={{
          marginTop: "0.65rem",
          display: "flex",
          gap: "0.5rem",
          flexWrap: "wrap",
          fontSize: "0.82rem",
        }}
      >
        <span className="chip">
          <ShieldCheck size={12} style={{ display: "inline", verticalAlign: "middle" }} />{" "}
          Confiance {insight.confidence_score}%
        </span>
        <span className="chip">{insight.grounded ? "Ancré sur les sources" : "Analyse prudente"}</span>
      </div>

      {insight.guard_warnings.length > 0 && (
        <ul style={{ marginTop: "0.65rem", paddingLeft: "1.2rem", fontSize: "0.82rem", opacity: 0.9 }}>
          {insight.guard_warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}

      <details style={{ marginTop: "0.75rem" }}>
        <summary>
          <Sparkles size={14} style={{ display: "inline", verticalAlign: "middle" }} /> Détails LLM (résumés, compétences, conseils)
        </summary>
        <div style={{ marginTop: "0.75rem", display: "grid", gap: "0.75rem" }}>
          <div>
            <strong>Résumé CV</strong>
            <p style={{ fontSize: "0.88rem" }}>{insight.cv_summary}</p>
          </div>
          <div>
            <strong>Résumé offre</strong>
            <p style={{ fontSize: "0.88rem" }}>{insight.job_summary}</p>
          </div>
          <div>
            <strong>Points forts</strong>
            <ul style={{ paddingLeft: "1.2rem", fontSize: "0.88rem" }}>
              {insight.strengths.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          </div>
          {insight.missing_skills.length > 0 && (
            <div>
              <strong>Compétences manquantes</strong>
              <div className="chips" style={{ marginTop: "0.35rem" }}>
                {insight.missing_skills.map((skill) => (
                  <span key={skill}>{skill}</span>
                ))}
              </div>
            </div>
          )}
          <div>
            <strong>Justification du score</strong>
            <p style={{ fontSize: "0.88rem" }}>{insight.score_justification}</p>
          </div>
          <div>
            <strong>Recommandations d&apos;amélioration</strong>
            <ul style={{ paddingLeft: "1.2rem", fontSize: "0.88rem" }}>
              {insight.improvement_tips.map((tip) => (
                <li key={tip}>{tip}</li>
              ))}
            </ul>
          </div>
          {insight.grounded_sources.length > 0 && (
            <div>
              <strong>Sources utilisées</strong>
              <div className="chips" style={{ marginTop: "0.35rem" }}>
                {insight.grounded_sources.slice(0, 8).map((source) => (
                  <span key={source}>{source}</span>
                ))}
              </div>
            </div>
          )}
          <p style={{ fontSize: "0.8rem", opacity: 0.75 }}>{insight.disclaimer}</p>
        </div>
      </details>
    </div>
  );
}
