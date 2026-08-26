"""Backward-compatible facade; prefer app.modules.* for new code."""

from app.modules.cv.extraction import extract_raw_text as extract_text_from_upload
from app.modules.cv.skills import extract_skills_from_text as extract_skills
from app.modules.cv.storage import save_cv_file as save_cv
from app.services.recruitment_legacy import (
    candidate_match_score,
    candidate_match_score_for_entities,
    send_interview_email,
    split_skills,
)

__all__ = [
    "candidate_match_score",
    "candidate_match_score_for_entities",
    "extract_skills",
    "extract_text_from_upload",
    "save_cv",
    "send_interview_email",
    "split_skills",
]
