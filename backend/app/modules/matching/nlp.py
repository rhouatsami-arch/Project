import math
import re
from collections import Counter

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "de",
    "des",
    "du",
    "en",
    "et",
    "for",
    "from",
    "in",
    "is",
    "it",
    "la",
    "le",
    "les",
    "of",
    "on",
    "or",
    "pour",
    "that",
    "the",
    "to",
    "un",
    "une",
    "with",
}

TOKEN_PATTERN = re.compile(r"[a-z0-9+#.]+", re.IGNORECASE)


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str | None) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    return [
        token.lower()
        for token in TOKEN_PATTERN.findall(normalized)
        if len(token) > 1 and token.lower() not in STOP_WORDS
    ]


def split_skill_tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    pieces = re.split(r"[,;\n|/]+", value.lower())
    return {piece.strip() for piece in pieces if piece.strip()}


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = left & right
    union = left | right
    return len(intersection) / len(union)


def cosine_similarity_counts(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0

    shared = set(left) & set(right)
    dot = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(count * count for count in left.values()))
    right_norm = math.sqrt(sum(count * count for count in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def tfidf_cosine_similarity(doc_a: str | None, doc_b: str | None) -> float:
    tokens_a = tokenize(doc_a)
    tokens_b = tokenize(doc_b)
    if not tokens_a or not tokens_b:
        return 0.0

    docs = [tokens_a, tokens_b]
    vocabulary = set(tokens_a) | set(tokens_b)
    idf: dict[str, float] = {}
    for token in vocabulary:
        doc_freq = sum(token in doc for doc in docs)
        idf[token] = math.log((len(docs) + 1) / (doc_freq + 1)) + 1.0

    def vectorize(tokens: list[str]) -> Counter[str]:
        counts = Counter(tokens)
        total = sum(counts.values()) or 1
        weighted: Counter[str] = Counter()
        for token, count in counts.items():
            tf = count / total
            weighted[token] = tf * idf[token]
        return weighted

    return cosine_similarity_counts(vectorize(tokens_a), vectorize(tokens_b))


def keyword_overlap_score(profile_text: str | None, job_text: str | None) -> float:
    profile_tokens = set(tokenize(profile_text))
    job_tokens = set(tokenize(job_text))
    return jaccard_similarity(profile_tokens, job_tokens)
