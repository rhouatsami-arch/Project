"""Semantic skill synonyms for embedding-like matching."""

SKILL_SYNONYMS: dict[str, list[str]] = {
    "python": ["python3", "py", "django", "flask"],
    "machine learning": ["ml", "apprentissage automatique", "scikit-learn"],
    "deep learning": [
        "dl",
        "neural networks",
        "réseaux de neurones",
        "pytorch",
        "tensorflow",
    ],
    "nlp": [
        "natural language processing",
        "traitement automatique du langage",
        "text mining",
    ],
    "sql": ["postgresql", "mysql", "base de données", "database"],
    "fastapi": ["api rest", "rest api", "uvicorn"],
    "react": ["reactjs", "react.js", "next.js", "nextjs"],
    "typescript": ["ts", "javascript", "js"],
    "docker": ["conteneur", "container", "kubernetes", "k8s"],
    "aws": ["amazon web services", "cloud aws", "s3", "ec2"],
    "azure": ["microsoft azure", "cloud azure"],
    "data analysis": ["analyse de données", "data analytics", "pandas", "excel"],
    "java": ["spring", "spring boot", "jvm"],
    "git": ["github", "gitlab", "version control"],
    "ui ux": ["figma", "design", "interface utilisateur"],
}


def expand_skill_tokens(skills: set[str]) -> set[str]:
    expanded = set(skills)
    for skill in list(skills):
        for canonical, aliases in SKILL_SYNONYMS.items():
            if skill == canonical or skill in aliases:
                expanded.add(canonical)
                expanded.update(aliases)
    return expanded


def embedding_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    left_expanded = expand_skill_tokens(left)
    right_expanded = expand_skill_tokens(right)
    intersection = left_expanded & right_expanded
    union = left_expanded | right_expanded
    return len(intersection) / len(union) if union else 0.0
