import json
import re
from collections import Counter
import pandas as pd
from typing import Any
from ranking.submission import process_candidates
from ranking.constants import (
    STRONG_RETRIEVAL_KEYWORDS, MEDIUM_RETRIEVAL_KEYWORDS,
    RANKING_KEYWORDS, EVALUATION_KEYWORDS, PRODUCTION_KEYWORDS
)

# Use JD-aligned tokens instead of generic ML keywords
IMPORTANT_TOKENS = set(
    STRONG_RETRIEVAL_KEYWORDS
    + MEDIUM_RETRIEVAL_KEYWORDS
    + RANKING_KEYWORDS
    + EVALUATION_KEYWORDS
    + ["faiss", "vector", "ann", "hnsw", "bm25", "dense retrieval",
       "cross encoder", "learning to rank", "reranker", "ndcg", "mrr"]
)

def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()

def normalize_list(values: Any) -> list:
    return values if isinstance(values, list) else []

def join_nonempty(values: list, separator: str = " | ") -> str:
    return separator.join([value for value in values if value])

def flatten_skills(record: dict) -> str:
    skills = normalize_list(record.get("skills"))
    names = []
    for skill in skills:
        if not isinstance(skill, dict): continue
        name = as_text(skill.get("name"))
        if not name: continue
        names.append(name)
    return " ".join(names)

def flatten_education(record: dict) -> str:
    education = normalize_list(record.get("education"))
    parts = []
    for item in education:
        if not isinstance(item, dict): continue
        fields = [
            as_text(item.get("degree")),
            as_text(item.get("field_of_study")),
            as_text(item.get("institution")),
        ]
        entry = join_nonempty([f for f in fields if f])
        if entry: parts.append(entry)
    return " ".join(parts)

def flatten_career_history(record: dict) -> str:
    career_history = normalize_list(record.get("career_history"))
    parts = []
    for item in career_history:
        if not isinstance(item, dict): continue
        summary = join_nonempty([
            as_text(item.get("title")),
            as_text(item.get("company")),
            as_text(item.get("description"))
        ])
        if summary: parts.append(summary)
    return " ".join(parts)

def compute_semantic_similarity(profile_text: str, skills_text: str,
                                 history_text: str, education_text: str) -> float:
    """JD-aligned semantic similarity using retrieval/ranking keywords."""
    combined = " ".join([profile_text, skills_text, history_text, education_text]).lower()
    if not combined.strip():
        return 0.0

    token_counts = Counter(re.findall(r"[a-z0-9+.#-]+", combined))
    if not token_counts:
        return 0.0

    # Score individual token hits from JD-aligned set
    hits = 0
    for token in IMPORTANT_TOKENS:
        # Multi-word tokens: check the full string
        if token in combined:
            hits += 1

    # Also score single-word token frequency
    freq_score = sum(token_counts.get(t, 0) for t in IMPORTANT_TOKENS if " " not in t)

    raw = (hits * 2 + freq_score) / max(len(token_counts), 1)
    return round(min(1.0, raw / 5.0), 4)

def main():
    print("Loading data...")
    candidates = []
    bad_lines = 0

    with open("req/candidates.jsonl", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError as e:
                bad_lines += 1
                print(f"[WARN] Skipping malformed line {i+1}: {e}")

    print(f"Loaded {len(candidates)} candidates. Skipped {bad_lines} bad lines.")
    print("Computing semantic similarity for all candidates...")

    for record in candidates:
        profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
        skills_text = flatten_skills(record)
        education_text = flatten_education(record)
        career_history_text = flatten_career_history(record)

        semantic_similarity = compute_semantic_similarity(
            as_text(profile.get("summary")),
            skills_text,
            career_history_text,
            education_text
        )
        record["semantic_similarity"] = semantic_similarity

    print("Ranking candidates...")
    ranked = process_candidates(candidates, top_k=100)

    print("Saving to submission.csv...")
    df = pd.DataFrame(ranked)
    # Ensure correct column order per submission spec
    df = df[["candidate_id", "rank", "score", "reasoning"]]
    df.to_csv("submission.csv", index=False, encoding="utf-8")
    print(f"Done! submission.csv written with {len(df)} rows.")

    # Auto-validate
    print("\nRunning submission validator...")
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, "req/validate_submission.py", "submission.csv"],
        capture_output=True, text=True
    )
    print(result.stdout or result.stderr)

if __name__ == "__main__":
    main()
