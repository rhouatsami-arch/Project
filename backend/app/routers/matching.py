from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_candidate, get_current_recruiter, get_current_student
from app.database import get_db
from app.models.recruitment import Job, Recruiter, Student
from app.modules.matching.pipeline import MatchingPipeline
from app.modules.matching.scorer import ApplicantProfile, JobProfile
from app.modules.matching.service import MatchingService
from app.modules.platform.audit import AuditAction, record_audit
from app.schemas.matching import (
    CandidateRankingOut,
    JobRecommendationOut,
    MatchingCalculateOut,
    MatchResultOut,
    MatchScoreRequest,
    PipelineInfoOut,
    PipelineRunOut,
    PipelineStageExecutionOut,
    PipelineStageOut,
    ScoreBreakdownOut,
)
from app.schemas.recruitment import JobOut

router = APIRouter(prefix="/matching", tags=["matching", "ml-nlp", "recommendations"])


def _breakdown_out(result) -> ScoreBreakdownOut:
    breakdown = result.breakdown
    return ScoreBreakdownOut(
        skills_score=round(breakdown.skills_score * 100),
        experience_score=round(breakdown.experience_score * 100),
        semantic_score=round(breakdown.semantic_score * 100),
        education_score=round(breakdown.education_score * 100),
        location_score=round(breakdown.location_score * 100),
        availability_score=round(breakdown.availability_score * 100),
        matched_skills=breakdown.matched_skills,
        missing_skills=breakdown.missing_skills,
        matched_optional_skills=breakdown.matched_optional_skills or [],
        missing_optional_skills=breakdown.missing_optional_skills or [],
        global_score_before_penalty=(
            round(breakdown.global_score_before_penalty * 100)
            if breakdown.global_score_before_penalty is not None
            else None
        ),
        penalty_factor=breakdown.penalty_factor,
        penalties_applied=breakdown.penalties_applied or [],
    )


def _match_result_out(result) -> MatchResultOut:
    return MatchResultOut(
        compatibility_score=result.compatibility_score,
        rank_label=result.rank_label,
        breakdown=_breakdown_out(result),
        explanation=result.explanation,
    )


@router.get("/pipeline", response_model=PipelineInfoOut)
def get_pipeline_info():
    return PipelineInfoOut(
        title="MatiousHire ML/NLP Matching Pipeline",
        version="2.1.0",
        description=(
            "Pipeline IA de matching candidat ↔ offre : score hybride explicable, "
            "(score hybride explicable, pénalités métier, TF-IDF, feedback recruteur)."
        ),
        formula=(
            "S_global = 100 × (0.35×S_comp + 0.25×S_exp + 0.20×S_sem + 0.10×S_form "
            "+ 0.05×S_loc + 0.05×S_disp) ; "
            "S_comp = 0.70×obligatoires + 0.30×souhaitées ; "
            "S_final = S_global × pénalités"
        ),
        weights=MatchingPipeline.WEIGHTS,
        stages=[
            PipelineStageOut(
                name=stage.name,
                description=stage.description,
                technique=stage.technique,
            )
            for stage in MatchingPipeline.stages()
        ],
        algorithms=[
            "Dictionnaire de compétences CV",
            "Jaccard + embeddings synonymes (skills)",
            "TF-IDF cosine similarity (profil ↔ offre)",
            "Keyword overlap (expérience / projets)",
            "Fusion multi-critères pondérée",
            "Classement décroissant + libellés de rang",
        ],
        rank_labels={
            "85+": "Très forte compatibilité",
            "70+": "Bonne compatibilité",
            "55+": "Compatibilité moyenne",
            "40+": "Compatibilité faible",
            "<40": "Profil non recommandé",
        },
    )


@router.post("/pipeline/run", response_model=PipelineRunOut)
def run_matching_pipeline(payload: MatchScoreRequest):
    """Exécute le pipeline ML/NLP tracé (étapes + durées) pour la démo PFE."""
    profile, job = _profiles_from_payload(payload)
    traced = MatchingPipeline.run_traced(profile, job)
    result = traced.result
    return PipelineRunOut(
        compatibility_score=result.compatibility_score,
        rank_label=result.rank_label,
        breakdown=_breakdown_out(result),
        explanation=result.explanation,
        stages=[
            PipelineStageExecutionOut(
                name=stage.name,
                description=stage.description,
                technique=stage.technique,
                duration_ms=stage.duration_ms,
                status=stage.status,
            )
            for stage in traced.stages
        ],
        total_duration_ms=traced.total_duration_ms,
        algorithms_used=list(traced.algorithms_used),
    )


@router.post("/calculate", response_model=MatchingCalculateOut)
def calculate_matching_score_endpoint(payload: MatchScoreRequest):
    """
    Pseudo-code doc. §10.1 — ``calculate_matching_score(candidate, job)``.

    Retourne ``(final_score, explanation_data)`` comme dans la documentation.
    """
    profile, job = _profiles_from_payload(payload)
    from app.modules.matching.matching_score_service import calculate_matching_score
    from app.modules.matching.scorer import _to_matching_candidate, _to_matching_job

    final_score, explanation_data = calculate_matching_score(
        _to_matching_candidate(profile),
        _to_matching_job(job),
    )
    return MatchingCalculateOut(
        final_score=final_score,
        explanation_data=explanation_data,
    )


@router.post("/score", response_model=MatchResultOut)
def compute_match_score(payload: MatchScoreRequest):
    profile, job = _profiles_from_payload(payload)
    return _match_result_out(MatchingPipeline.run(profile, job))


def _profiles_from_payload(payload: MatchScoreRequest):
    profile = ApplicantProfile(
        technical_skills=payload.technical_skills,
        soft_skills=payload.soft_skills,
        skills=payload.skills,
        cv_extracted_text=payload.cv_extracted_text,
        field_of_study=payload.field_of_study,
        experiences=payload.experiences,
        projects=payload.projects,
        bio=payload.bio,
        internship_type=payload.internship_type,
        location=payload.location,
    )
    job = JobProfile(
        title=payload.job_title,
        description=payload.job_description,
        required_skills=payload.required_skills,
        optional_skills=payload.optional_skills,
        location=payload.job_location,
        employment_type=payload.employment_type,
        remote_policy=payload.employment_type,
        required_experience=payload.job_description,
        required_education=payload.job_description,
    )
    return profile, job


@router.get("/students/me/recommendations", response_model=list[JobRecommendationOut])
def student_job_recommendations(
    limit: int = Query(10, ge=1, le=50),
    min_score: int = Query(0, ge=0, le=100),
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _recommendations(db, current, limit, min_score)


@router.get("/candidates/me/recommendations", response_model=list[JobRecommendationOut])
def candidate_job_recommendations(
    limit: int = Query(10, ge=1, le=50),
    min_score: int = Query(0, ge=0, le=100),
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return _recommendations(db, current, limit, min_score)


@router.get(
    "/recruiters/jobs/{job_id}/ranking",
    response_model=list[CandidateRankingOut],
)
def recruiter_candidate_ranking(
    job_id: int,
    min_score: int = Query(0, ge=0, le=100),
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    from sqlalchemy.orm import joinedload

    from app.models.recruitment import Application

    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = (
        db.query(Application)
        .options(joinedload(Application.student))
        .filter(Application.job_id == job.id)
        .all()
    )
    ranked = MatchingService.rank_applications(applications, job, min_score=min_score)
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.RANK_CANDIDATES,
        resource=str(job.id),
        details=f"{len(ranked)} candidats classés",
    )
    output: list[CandidateRankingOut] = []
    for index, (application, result) in enumerate(ranked, start=1):
        application.match_score = result.compatibility_score
        student = application.student
        output.append(
            CandidateRankingOut(
                application_id=application.id,
                student_id=str(student.id),
                first_name=student.first_name,
                last_name=student.last_name,
                email=student.email,
                compatibility_score=result.compatibility_score,
                rank=index,
                rank_label=result.rank_label,
                breakdown=_breakdown_out(result),
                explanation=result.explanation,
            )
        )
    db.commit()
    return output


def _recommendations(
    db: Session, student: Student, limit: int, min_score: int
) -> list[JobRecommendationOut]:
    ranked = MatchingService.recommend_jobs(
        db, student, limit=limit, min_score=min_score
    )
    MatchingService.record_recommendations(db, student, ranked)
    db.commit()
    return [
        JobRecommendationOut(
            job=JobOut.model_validate(job),
            compatibility_score=result.compatibility_score,
            rank_label=result.rank_label,
            breakdown=_breakdown_out(result),
            explanation=result.explanation,
        )
        for job, result in ranked
    ]
