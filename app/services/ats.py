import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def calculate_ats_score(cv_text: str, job_description: str) -> dict:
    cv_doc = nlp(cv_text.lower())
    jd_doc = nlp(job_description.lower())

    cv_keywords = {t.lemma_ for t in cv_doc if not t.is_stop and t.is_alpha}
    jd_keywords = {t.lemma_ for t in jd_doc if not t.is_stop and t.is_alpha}

    matched = cv_keywords & jd_keywords
    missing = jd_keywords - cv_keywords
    score = round(len(matched) / max(len(jd_keywords), 1) * 100, 2)

    return {
        "score": score,
        "matched_keywords": list(matched)[:20],
        "missing_keywords": list(missing)[:20]
    }