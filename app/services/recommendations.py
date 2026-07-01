import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

N_COMPONENTS     = 20
MIN_INTERACTIONS = 3
TOP_NEIGHBOURS   = 8
APPLY_WEIGHT     = 3.0


def _build_matrix(applications: list[dict]) -> tuple[np.ndarray, list, list]:
    student_ids = sorted({a["student_id"] for a in applications})
    job_ids     = sorted({a["job_id"]     for a in applications})
    s_idx = {s: i for i, s in enumerate(student_ids)}
    j_idx = {j: i for i, j in enumerate(job_ids)}
    matrix = np.zeros((len(student_ids), len(job_ids)), dtype=np.float32)
    for a in applications:
        matrix[s_idx[a["student_id"]], j_idx[a["job_id"]]] = APPLY_WEIGHT
    return matrix, student_ids, job_ids


def _svd_scores(matrix, student_ids, job_ids, student_id):
    if student_id not in student_ids:
        return {}
    k   = min(N_COMPONENTS, matrix.shape[0]-1, matrix.shape[1]-1)
    if k < 1:
        return {}
    svd = TruncatedSVD(n_components=k, random_state=42)
    U   = svd.fit_transform(matrix)
    row = list(student_ids).index(student_id)
    scores = (U @ svd.components_)[row]
    return {int(job_ids[i]): float(scores[i]) for i in range(len(job_ids))}


def _user_user_scores(matrix, student_ids, job_ids, student_id):
    if student_id not in student_ids:
        return {}
    row  = list(student_ids).index(student_id)
    sim  = cosine_similarity(normalize(matrix, norm="l2"))[row]
    sim[row] = -1.0
    top  = np.argsort(sim)[::-1][:TOP_NEIGHBOURS]
    w    = sim[top]
    if w.sum() == 0:
        return {}
    scores = (matrix[top] * w[:, None]).sum(axis=0) / w.sum()
    return {int(job_ids[i]): float(scores[i]) for i in range(len(job_ids))}


def get_collaborative_recommendations(
    student_id:   int,
    applications: list[dict],
    all_jobs:     list[dict],
    applied_ids:  set[int],
    top_k:        int = 5,
) -> list[dict]:
    if not applications:
        return []
    matrix, student_ids, job_ids = _build_matrix(applications)
    if student_id not in student_ids:
        return []
    n_applied = int((matrix[list(student_ids).index(student_id)] > 0).sum())
    if n_applied >= MIN_INTERACTIONS and matrix.shape[0] > N_COMPONENTS:
        scores = _svd_scores(matrix, student_ids, job_ids, student_id)
    else:
        scores = _user_user_scores(matrix, student_ids, job_ids, student_id)
    if not scores:
        return []
    job_lookup = {j["id"]: j for j in all_jobs}
    candidates = []
    for job_id, score in scores.items():
        if job_id in applied_ids or job_id not in job_lookup or score <= 0.01:
            continue
        job = dict(job_lookup[job_id])
        job["rec_score"] = round(score, 4)
        candidates.append(job)
    candidates.sort(key=lambda j: j["rec_score"], reverse=True)
    return candidates[:top_k]
