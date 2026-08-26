"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { SectionHeading } from "@/components/ui";
import { api, auth, formatDate, messageFromError } from "@/lib/api";
import { RequireAuth } from "@/components/require-auth";
import { useAuth } from "@/providers/auth-provider";
import { useNotice } from "@/providers/notice-provider";
import type { AuditLogEntry } from "@/types/recruitment";

const ROLES = ["", "admin", "recruiter", "student", "candidate"];

export default function AdminAuditLogsPage() {
  const { token } = useAuth();
  const { showNotice } = useNotice();
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [roleFilter, setRoleFilter] = useState("");
  const [actionFilter, setActionFilter] = useState("");

  const load = useCallback(async () => {
    if (!token) return;
    const params = new URLSearchParams({ limit: "100" });
    if (roleFilter) params.set("role", roleFilter);
    if (actionFilter.trim()) params.set("action", actionFilter.trim());
    setLogs(
      await api<AuditLogEntry[]>(
        `/admin/audit-logs?${params.toString()}`,
        auth(token.access_token),
      ),
    );
  }, [actionFilter, roleFilter, token]);

  useEffect(() => {
    load().catch((error) => showNotice(messageFromError(error)));
  }, [load, showNotice]);

  const actionOptions = useMemo(() => {
    const values = new Set(logs.map((log) => log.action));
    return Array.from(values).sort();
  }, [logs]);

  return (
    <RequireAuth role="admin">
      <section className="student-dashboard">
        <SectionHeading
          title="Journaux d'audit"
          text="Traçabilité complète des actions : connexions, candidatures, pipeline, entretiens, administration."
        />

        <div className="filters-row">
          <label>
            Rôle
            <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
              <option value="">Tous</option>
              {ROLES.filter(Boolean).map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </label>
          <label>
            Action
            <select value={actionFilter} onChange={(e) => setActionFilter(e.target.value)}>
              <option value="">Toutes</option>
              {actionOptions.map((action) => (
                <option key={action} value={action}>
                  {action}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="job-stack">
          {logs.length === 0 ? (
            <p>Aucun journal d&apos;audit pour ces filtres.</p>
          ) : (
            logs.map((log) => (
              <article className="job-card" key={log.id}>
                <p className="eyebrow">
                  {log.actor_role} · {log.actor_email} · {formatDate(log.created_at)}
                </p>
                <h3>{log.action_label || log.action}</h3>
                <p>{log.details || log.resource || "—"}</p>
                {log.resource ? <span className="tag">Ressource : {log.resource}</span> : null}
              </article>
            ))
          )}
        </div>
      </section>
    </RequireAuth>
  );
}
