from app.modules.matching.scorer import ApplicantProfile, JobProfile, ScoreBreakdown


def build_strengths(
    profile: ApplicantProfile, job: JobProfile, breakdown: ScoreBreakdown
) -> list[str]:
    strengths: list[str] = []
    if breakdown.matched_skills:
        strengths.append(
            "Maîtrise de compétences clés : " + ", ".join(breakdown.matched_skills[:6])
        )
    if breakdown.experience_score >= 0.55:
        strengths.append("Expériences et projets en lien avec les missions du poste")
    if breakdown.education_score >= 0.55:
        strengths.append(
            f"Formation pertinente : {profile.field_of_study or 'domaine adapté'}"
        )
    if breakdown.semantic_score >= 0.55:
        strengths.append("Forte proximité sémantique entre le CV et l'offre")
    if breakdown.skills_score >= 0.7:
        strengths.append("Excellent recouvrement des compétences demandées")
    if not strengths:
        strengths.append(
            "Profil partiellement aligné — potentiel de montée en compétences"
        )
    return strengths


def build_score_justification(breakdown: ScoreBreakdown, score: int) -> str:
    parts = [
        f"Score global {score}% calculé ainsi : "
        f"compétences {round(breakdown.skills_score * 100)}%, "
        f"expérience {round(breakdown.experience_score * 100)}%, "
        f"sémantique {round(breakdown.semantic_score * 100)}%, "
        f"formation {round(breakdown.education_score * 100)}%, "
        f"localisation {round(breakdown.location_score * 100)}%, "
        f"disponibilité {round(breakdown.availability_score * 100)}%."
    ]
    if (
        breakdown.global_score_before_penalty is not None
        and breakdown.penalty_factor < 1.0
    ):
        before = round(breakdown.global_score_before_penalty * 100)
        parts.append(
            f" Score avant pénalités : {before}% "
            f"(facteur ×{breakdown.penalty_factor:.2f})."
        )
    if breakdown.penalties_applied:
        parts.append(" Pénalités : " + "; ".join(breakdown.penalties_applied) + ".")
    return "".join(parts)


def build_improvement_tips(breakdown: ScoreBreakdown) -> list[str]:
    tips: list[str] = []
    for skill in breakdown.missing_skills[:4]:
        tips.append(f"Acquérir ou mettre en avant la compétence : {skill}")
    if breakdown.experience_score < 0.5:
        tips.append("Enrichir le CV avec des projets ou stages liés au poste visé")
    if breakdown.education_score < 0.5:
        tips.append("Préciser la formation et les certifications pertinentes")
    if breakdown.semantic_score < 0.5:
        tips.append("Adapter le vocabulaire du CV aux termes utilisés dans l'offre")
    if not tips:
        tips.append(
            "Profil déjà bien aligné — postuler en mettant en avant les points forts"
        )
    return tips


def explain_compatibility(
    profile: ApplicantProfile,
    job: JobProfile,
    breakdown: ScoreBreakdown,
    score: int,
) -> str:
    gaps: list[str] = []

    if breakdown.missing_skills:
        gaps.append(
            "compétences manquantes : " + ", ".join(breakdown.missing_skills[:5])
        )
    if breakdown.location_score < 0.4 and job.location:
        gaps.append(f"localisation non alignée avec {job.location}")
    if breakdown.availability_score < 0.5:
        gaps.append("adéquation limitée sur disponibilité ou type de stage")

    text = (
        f"Le candidat présente une compatibilité de {score}% avec l'offre "
        f"« {job.title} » car il possède "
    )
    if breakdown.matched_skills:
        text += (
            "plusieurs compétences clés demandées, notamment "
            + ", ".join(breakdown.matched_skills[:4])
            + ". "
        )
    else:
        text += "un profil partiellement aligné. "

    if breakdown.experience_score >= 0.5:
        text += "Son expérience correspond aux missions décrites. "
    if breakdown.semantic_score >= 0.5:
        text += "L'analyse sémantique confirme la proximité CV–offre. "

    if gaps:
        text += "Le score est toutefois modéré en raison de : " + "; ".join(gaps) + ". "

    text += build_score_justification(breakdown, score)
    text += " " + (
        "Cette explication IA est une aide à la décision ; "
        "le recruteur reste responsable du choix final."
    )
    return text


def summarize_cv(profile: ApplicantProfile) -> str:
    sections: list[str] = [
        f"**Profil** : candidat orienté "
        f"{profile.field_of_study or 'développement professionnel'}."
    ]
    if profile.technical_skills:
        sections.append(f"**Compétences techniques** : {profile.technical_skills}.")
    if profile.soft_skills:
        sections.append(f"**Soft skills** : {profile.soft_skills}.")
    if profile.experiences:
        sections.append(f"**Expériences** : {profile.experiences[:220]}.")
    if profile.projects:
        sections.append(f"**Projets** : {profile.projects[:220]}.")
    if profile.certifications:
        sections.append(f"**Certifications** : {profile.certifications[:120]}.")
    if profile.cv_extracted_text:
        preview = profile.cv_extracted_text[:180].replace("\n", " ")
        sections.append(f"**Extrait CV** : {preview}...")
    return " ".join(sections)


def summarize_job(job: JobProfile) -> str:
    parts = [f"**Offre** : {job.title}"]
    if job.location:
        parts.append(f"à {job.location}")
    parts.append(f"— {job.description[:280]}")
    if job.required_skills:
        parts.append(f"**Compétences requises** : {job.required_skills}.")
    return " ".join(parts)


def interview_questions(
    profile: ApplicantProfile, job: JobProfile, breakdown: ScoreBreakdown
) -> list[str]:
    questions = [
        f"Décrivez une expérience concrète liée au poste « {job.title} ».",
        "Quel projet démontre le mieux vos compétences techniques ?",
    ]
    for skill in breakdown.missing_skills[:2]:
        questions.append(f"Comment développez-vous votre compétence en {skill} ?")
    if profile.internship_type:
        questions.append(f"Quelles attentes pour un stage {profile.internship_type} ?")
    return questions[:5]
