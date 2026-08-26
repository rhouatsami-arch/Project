import re

SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "vue",
    "angular",
    "node",
    "express",
    "fastapi",
    "django",
    "flask",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "aws",
    "azure",
    "gcp",
    "machine learning",
    "data analysis",
    "excel",
    "power bi",
    "tableau",
    "html",
    "css",
    "figma",
    "rest api",
    "graphql",
    "testing",
    "communication",
    "leadership",
    "project management",
    "scrum",
    "agile",
}


def extract_skills_from_text(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.lower())
    found = {
        skill
        for skill in SKILL_KEYWORDS
        if re.search(rf"\b{re.escape(skill)}\b", normalized)
    }
    return sorted(found)
