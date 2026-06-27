import json
import re
from collections import Counter
from typing import Any
import pandas as pd

SKILL_WEIGHT = {"beginner": 1.0, "intermediate": 2.0, "advanced": 3.0, "expert": 4.0}

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

def parse_jsonl(path: str) -> list:
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def flatten_skills(record: dict) -> tuple:
    skills = normalize_list(record.get("skills"))
    names = []
    weighted_score = 0.0
    for skill in skills:
        if not isinstance(skill, dict): continue
        name = as_text(skill.get("name"))
        if not name: continue
        names.append(name)
        proficiency = as_text(skill.get("proficiency")).lower()
        endorsements = skill.get("endorsements", 0) or 0
        duration_months = skill.get("duration_months", 0) or 0
        weighted_score += SKILL_WEIGHT.get(proficiency, 0.5) + min(float(endorsements), 25.0) / 25.0 + min(float(duration_months), 60.0) / 60.0
    return ", ".join(names), weighted_score, names

def flatten_education(record: dict) -> str:
    education = normalize_list(record.get("education"))
    parts = []
    for item in education:
        if not isinstance(item, dict): continue
        fields = [
            as_text(item.get("degree")),
            as_text(item.get("field_of_study")),
            as_text(item.get("institution")),
            f"{item.get('start_year', '')}-{item.get('end_year', '')}".strip("-"),
        ]
        entry = join_nonempty([f for f in fields if f and f != "-"])
        if entry: parts.append(entry)
    return join_nonempty(parts, " || ")

def flatten_career_history(record: dict) -> str:
    career_history = normalize_list(record.get("career_history"))
    parts = []
    for item in career_history:
        if not isinstance(item, dict): continue
        summary = join_nonempty([as_text(item.get("title")), as_text(item.get("company")), as_text(item.get("industry")), as_text(item.get("description"))])
        if summary: parts.append(summary)
    return join_nonempty(parts, " || ")

def compute_semantic_similarity(profile_text: str, skills_text: str, history_text: str, education_text: str) -> float:
    parts = [profile_text, skills_text, history_text, education_text]
    token_counts = Counter()
    for part in parts:
        token_counts.update(re.findall(r"[a-z0-9+.#-]+", part.lower()))
    if not token_counts: return 0.0
    important_tokens = {
        "python", "sql", "spark", "airflow", "ml", "machine", "learning", "llm", "nlp", "opencv",
        "tensorflow", "pytorch", "kubernetes", "docker", "aws", "gcp", "azure", "react", "node",
        "fastapi", "flask", "databricks", "snowflake", "faiss", "vector", "search",
    }
    weighted = sum(token_counts[token] for token in token_counts if token in important_tokens)
    raw = weighted / max(len(token_counts), 1)
    return round(min(1.0, raw / 4.0), 4)

def compute_retrieval_score(record: dict, skill_weighted_score: float) -> float:
    profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
    redrob = record.get("redrob_signals") if isinstance(record.get("redrob_signals"), dict) else {}
    years_experience = float(profile.get("years_of_experience") or 0.0)
    completeness = float(redrob.get("profile_completeness_score") or 0.0)
    activity = 0.0
    if redrob.get("open_to_work_flag"): activity += 5.0
    activity += min(float(redrob.get("profile_views_received_30d") or 0.0), 200.0) / 20.0
    activity += min(float(redrob.get("applications_submitted_30d") or 0.0), 20.0) / 10.0
    activity += min(float(redrob.get("recruiter_response_rate") or 0.0), 1.0) * 10.0
    score = (
        completeness * 0.25
        + years_experience * 2.0
        + skill_weighted_score * 4.0
        + activity
        + min(float(redrob.get("endorsements_received") or 0.0), 200.0) / 8.0
    )
    return round(score, 4)

print("Loading data...")
records = parse_jsonl("req/candidates.jsonl")
rows = []

print("Processing records...")
for idx, record in enumerate(records):
    profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
    skills_text, skill_weighted_score, skill_names = flatten_skills(record)
    education_text = flatten_education(record)
    career_history_text = flatten_career_history(record)
    
    candidate_document_parts = [
        as_text(profile.get("headline")),
        as_text(profile.get("summary")),
        skills_text,
        career_history_text,
        education_text,
        as_text(record.get("profile", {}).get("location")),
        as_text(record.get("profile", {}).get("current_title")),
        as_text(record.get("profile", {}).get("current_company")),
    ]
    candidate_document = join_nonempty(candidate_document_parts, "\n")
    
    semantic_similarity = compute_semantic_similarity(
        as_text(profile.get("summary")), skills_text, career_history_text, education_text
    )
    retrieval_score = compute_retrieval_score(record, skill_weighted_score)
    candidate_id = as_text(record.get("candidate_id")) or f"CAND_{len(rows) + 1:07d}"
    
    rows.append({
        "candidate_id": candidate_id,
        "candidate_document_len": len(candidate_document),
        "semantic_similarity": semantic_similarity,
        "retrieval_score": retrieval_score,
        "skill_match": round(skill_weighted_score, 4),
        "years_experience": float(profile.get("years_of_experience") or 0.0)
    })

print("Creating DataFrame...")
df = pd.DataFrame(rows)

print("Normalizing...")
df["semantic_similarity"] = df["semantic_similarity"].clip(0, 1)
skill_match_max = df["skill_match"].max()
if skill_match_max > 1: df["skill_match"] = df["skill_match"] / skill_match_max
df["skill_match"] = df["skill_match"].clip(0, 1)
retrieval_max = df["retrieval_score"].max()
if retrieval_max > 1: df["retrieval_score"] = df["retrieval_score"] / retrieval_max
df["retrieval_score"] = df["retrieval_score"].clip(0, 1)

# Hybrid retrieval score fallback
df["hybrid_score"] = 0.40 * df["semantic_similarity"] + 0.35 * df["skill_match"] + 0.25 * (df["years_experience"] / 20.0).clip(0, 1)

df = df.sort_values(["hybrid_score", "semantic_similarity", "skill_match"], ascending=[False, False, False]).reset_index(drop=True)

report_data = {
    "semantic_similarity": {
        "p50": float(df["semantic_similarity"].quantile(0.50)),
        "p75": float(df["semantic_similarity"].quantile(0.75)),
        "p90": float(df["semantic_similarity"].quantile(0.90)),
        "p95": float(df["semantic_similarity"].quantile(0.95)),
        "p99": float(df["semantic_similarity"].quantile(0.99))
    },
    "retrieval_score": {
        "p50": float(df["hybrid_score"].quantile(0.50)),
        "p75": float(df["hybrid_score"].quantile(0.75)),
        "p90": float(df["hybrid_score"].quantile(0.90)),
        "p95": float(df["hybrid_score"].quantile(0.95)),
        "p99": float(df["hybrid_score"].quantile(0.99))
    },
    "skill_match": {
        "p50": float(df["skill_match"].quantile(0.50)),
        "p75": float(df["skill_match"].quantile(0.75)),
        "p90": float(df["skill_match"].quantile(0.90)),
        "p95": float(df["skill_match"].quantile(0.95)),
        "p99": float(df["skill_match"].quantile(0.99))
    },
    "document_length": {
        "mean": float(df["candidate_document_len"].mean()),
        "p95": float(df["candidate_document_len"].quantile(0.95)),
        "max": float(df["candidate_document_len"].max())
    },
    "top_20": df.head(20)[["candidate_id", "semantic_similarity", "skill_match", "hybrid_score"]].rename(columns={"hybrid_score": "retrieval_score"}).to_dict(orient="records")
}

with open("report_data.json", "w") as f:
    json.dump(report_data, f, indent=2)

print("Report data generated successfully!")
