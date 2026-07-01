from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def match_student_to_jobs(student_profile: str, jobs: list[dict]) -> list[dict]:
    student_emb = model.encode([student_profile])
    job_texts = [f"{j['title']} {j['description']}" for j in jobs]
    job_embs = model.encode(job_texts)
    scores = cosine_similarity(student_emb, job_embs)[0]
    ranked = sorted(zip(jobs, scores), key=lambda x: x[1], reverse=True)
    return [{"job": j, "score": round(float(s), 4)} for j, s in ranked]