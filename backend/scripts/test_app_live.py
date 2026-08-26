#!/usr/bin/env python3
"""Live smoke tests against running MatiousHire API."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8000"
results: list[tuple[str, bool, str]] = []


def req(method: str, path: str, *, token: str | None = None, form=None, json_body=None):
    url = BASE + path
    headers: dict[str, str] = {}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as resp:
            body = resp.read().decode()
            payload = json.loads(body) if body else None
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            payload = json.loads(body)
        except Exception:
            payload = body[:200]
        return exc.code, payload


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    mark = "PASS" if ok else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{mark}] {name}{suffix}")


def main() -> int:
    status, data = req("GET", "/")
    check(
        "Health check",
        status == 200 and isinstance(data, dict) and data.get("status") == "ok",
        f"status={status}",
    )

    accounts = [
        ("student", "student.demo2026@example.com"),
        ("candidate", "candidate.demo2026@example.com"),
        ("recruiter", "recruiter.demo2026@example.com"),
        ("admin", "admin@matioushire.com"),
    ]
    tokens: dict[str, str] = {}
    for role, email in accounts:
        form = {"username": email, "password": "Password123"}
        if role == "candidate":
            form["client_id"] = "candidate"
        status, data = req("POST", "/auth/login", form=form)
        ok = (
            status == 200
            and isinstance(data, dict)
            and bool(data.get("access_token"))
            and data.get("role") == role
        )
        if ok:
            tokens[role] = data["access_token"]
        role_value = data.get("role") if isinstance(data, dict) else data
        check(f"Login {role}", ok, f"status={status}, role={role_value}")

    if "student" in tokens:
        for path in (
            "/students/me",
            "/jobs/",
            "/matching/students/me/recommendations",
        ):
            status, _ = req("GET", path, token=tokens["student"])
            check(f"Student GET {path}", status == 200, f"status={status}")

    if "candidate" in tokens:
        for path in (
            "/candidates/me",
            "/jobs/",
            "/matching/candidates/me/recommendations",
        ):
            status, _ = req("GET", path, token=tokens["candidate"])
            check(f"Candidate GET {path}", status == 200, f"status={status}")

    if "recruiter" in tokens:
        for path in (
            "/recruiters/me",
            "/recruiters/me/dashboard",
            "/jobs/recruiter/me",
        ):
            status, data = req("GET", path, token=tokens["recruiter"])
            detail = f"status={status}"
            if isinstance(data, list):
                detail += f", items={len(data)}"
            check(f"Recruiter GET {path}", status == 200, detail)
        status, jobs = req("GET", "/jobs/recruiter/me", token=tokens["recruiter"])
        if status == 200 and isinstance(jobs, list) and jobs:
            job_id = jobs[0]["id"]
            status, data = req(
                "GET",
                f"/recruiters/jobs/{job_id}/candidates",
                token=tokens["recruiter"],
            )
            detail = f"status={status}"
            if isinstance(data, list):
                detail += f", candidates={len(data)}"
            check("Recruiter GET job candidates pipeline", status == 200, detail)

    if "admin" in tokens:
        for path in (
            "/admin/me",
            "/admin/dashboard",
            "/admin/users/students",
            "/admin/users/candidates",
            "/admin/users/recruiters",
        ):
            status, _ = req("GET", path, token=tokens["admin"])
            check(f"Admin GET {path}", status == 200, f"status={status}")

    if "recruiter" in tokens:
        status, _ = req("GET", "/matching/pipeline", token=tokens["recruiter"])
        check("Matching pipeline info", status == 200, f"status={status}")
        status, _ = req("GET", "/llm/module", token=tokens["recruiter"])
        check("LLM module info", status == 200, f"status={status}")

    passed = sum(ok for _, ok, _ in results)
    failed = sum(not ok for _, ok, _ in results)
    print(f"\nAPI summary: {passed} passed, {failed} failed, {len(results)} total")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
