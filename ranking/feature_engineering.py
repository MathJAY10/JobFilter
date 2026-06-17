from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
from .constants import (
    STRONG_RETRIEVAL_KEYWORDS,
    MEDIUM_RETRIEVAL_KEYWORDS,
    WEAK_RETRIEVAL_KEYWORDS,
    RANKING_KEYWORDS,
    EVALUATION_KEYWORDS,
    PRODUCTION_KEYWORDS,
    STARTUP_KEYWORDS,
    BEHAVIOR_WEIGHTS
)

@dataclass
class ScoreWithEvidence:
    score: float
    evidence: List[str] = field(default_factory=list)

@dataclass
class CandidateFeatures:
    retrieval_expertise: ScoreWithEvidence
    ranking_expertise: ScoreWithEvidence
    evaluation_score: ScoreWithEvidence
    production_score: ScoreWithEvidence
    startup_score: ScoreWithEvidence
    behavior_score: ScoreWithEvidence

def extract_text_with_context(candidate: Dict[str, Any]) -> List[str]:
    """Safely extracts all searchable text chunks from a candidate record for evidence tracking."""
    chunks = []
    
    doc = candidate.get("candidate_document")
    if doc:
        chunks.extend([s.strip() for s in str(doc).split('.') if s.strip()])
        
    skills = candidate.get("skills")
    if isinstance(skills, list):
        # Handle dict format in real schema: {"name": "python", "proficiency": "expert"}
        for s in skills:
            if isinstance(s, dict) and "name" in s:
                chunks.append(str(s["name"]).strip())
            else:
                chunks.append(str(s).strip())
        
    career = candidate.get("career_history")
    if isinstance(career, list):
        for role in career:
            if isinstance(role, dict):
                chunks.append(str(role.get("title", "")).strip())
                desc = str(role.get("description", ""))
                chunks.extend([s.strip() for s in desc.split('.') if s.strip()])
            else:
                chunks.append(str(role).strip())
                
    profile = candidate.get("profile")
    if isinstance(profile, dict):
        summary = str(profile.get("summary", ""))
        chunks.extend([s.strip() for s in summary.split('.') if s.strip()])

    return [c.lower() for c in chunks if c]

def calculate_keyword_score_with_evidence(chunks: List[str], keywords: List[str], max_hits: int = 5, weight: float = 1.0) -> ScoreWithEvidence:
    """Calculates score and extracts evidence sentences containing the keywords."""
    hits = 0
    evidence = []
    
    for chunk in chunks:
        for kw in keywords:
            if kw in chunk and chunk not in evidence:
                hits += 1
                evidence.append(chunk)
                break 
                
    score = min(hits / max_hits, 1.0) * weight
    return ScoreWithEvidence(score=score, evidence=evidence[:max_hits])

def calculate_retrieval_score(chunks: List[str]) -> ScoreWithEvidence:
    """Calculates retrieval score across strong, medium, and weak tiers."""
    strong = calculate_keyword_score_with_evidence(chunks, STRONG_RETRIEVAL_KEYWORDS, max_hits=2, weight=1.0)
    medium = calculate_keyword_score_with_evidence(chunks, MEDIUM_RETRIEVAL_KEYWORDS, max_hits=3, weight=0.6)
    weak = calculate_keyword_score_with_evidence(chunks, WEAK_RETRIEVAL_KEYWORDS, max_hits=2, weight=0.2)
    
    total_score = min(strong.score + medium.score + weak.score, 1.0)
    
    evidence = strong.evidence + medium.evidence + weak.evidence
    seen = set()
    deduped_evidence = [x for x in evidence if not (x in seen or seen.add(x))]
    
    return ScoreWithEvidence(score=total_score, evidence=deduped_evidence[:4])

def extract_behavior_score(candidate: Dict[str, Any]) -> ScoreWithEvidence:
    """Extracts a behavior score by normalizing and weighting specific Redrob signals."""
    signals = candidate.get("redrob_signals")
    if not isinstance(signals, dict):
        return ScoreWithEvidence(score=0.0, evidence=["No behavior signals found."])
    
    total_score = 0.0
    evidence = []
    
    rrr = signals.get("recruiter_response_rate", 0.0)
    if isinstance(rrr, (int, float)):
        norm_rrr = min(max(float(rrr), 0.0), 1.0)
        total_score += norm_rrr * BEHAVIOR_WEIGHTS["recruiter_response_rate"]
        evidence.append(f"recruiter_response_rate: {norm_rrr:.2f}")

    gh = signals.get("github_activity_score", 0)
    if isinstance(gh, (int, float)):
        norm_gh = max(0.0, float(gh)) / 100.0
        norm_gh = min(norm_gh, 1.0)
        total_score += norm_gh * BEHAVIOR_WEIGHTS["github_activity_score"]
        evidence.append(f"github_activity_score: {gh}")

    pc = signals.get("profile_completeness_score", 0)
    if isinstance(pc, (int, float)):
        norm_pc = min(max(float(pc) / 100.0, 0.0), 1.0)
        total_score += norm_pc * BEHAVIOR_WEIGHTS["profile_completeness_score"]
        evidence.append(f"profile_completeness_score: {pc}")

    icr = signals.get("interview_completion_rate", 0.0)
    if isinstance(icr, (int, float)):
        norm_icr = min(max(float(icr), 0.0), 1.0)
        total_score += norm_icr * BEHAVIOR_WEIGHTS["interview_completion_rate"]
        evidence.append(f"interview_completion_rate: {norm_icr:.2f}")

    return ScoreWithEvidence(score=total_score, evidence=evidence)

def extract_features(candidate: Dict[str, Any]) -> CandidateFeatures:
    """Extracts features and evidence for the ranking model."""
    chunks = extract_text_with_context(candidate)
    
    return CandidateFeatures(
        retrieval_expertise=calculate_retrieval_score(chunks),
        ranking_expertise=calculate_keyword_score_with_evidence(chunks, RANKING_KEYWORDS, max_hits=3),
        evaluation_score=calculate_keyword_score_with_evidence(chunks, EVALUATION_KEYWORDS, max_hits=3),
        production_score=calculate_keyword_score_with_evidence(chunks, PRODUCTION_KEYWORDS, max_hits=5),
        startup_score=calculate_keyword_score_with_evidence(chunks, STARTUP_KEYWORDS, max_hits=2),
        behavior_score=extract_behavior_score(candidate)
    )
