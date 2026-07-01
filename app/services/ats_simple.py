import re

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for",
    "of","with","by","from","is","are","was","were","be","been",
    "have","has","had","do","does","did","will","would","could",
    "should","may","might","shall","can","need","must","i","we",
    "you","he","she","it","they","this","that","these","those"
}

def _keywords(text: str) -> set:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return {w for w in words if w not in STOP_WORDS}

def ats_score(cv_text: str, job_description: str, requirements: str = "") -> dict:
    jd_full  = f"{job_description} {requirements or ''}"
    cv_kw    = _keywords(cv_text)
    jd_kw    = _keywords(jd_full)
    matched  = cv_kw & jd_kw
    missing  = jd_kw - cv_kw
    score    = round(len(matched) / max(len(jd_kw), 1) * 100, 1)
    if score >= 70:   rec = "Strong match — shortlist"
    elif score >= 45: rec = "Moderate match — consider"
    else:             rec = "Weak match — likely skip"
    return {
        "score":            score,
        "matched_keywords": sorted(matched)[:20],
        "missing_keywords": sorted(missing)[:20],
        "recommendation":   rec,
    }
