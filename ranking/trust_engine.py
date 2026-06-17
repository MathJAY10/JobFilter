from dataclasses import dataclass, field
from typing import Dict, Any, List
from .constants import NEGATIVE_KEYWORDS, STRONG_RETRIEVAL_KEYWORDS, MEDIUM_RETRIEVAL_KEYWORDS, RANKING_KEYWORDS, MIN_TRUST_SCORE
from .feature_engineering import extract_text_with_context

@dataclass
class TrustFlag:
    description: str
    severity: str # 'low', 'medium', 'high'
    penalty: float

@dataclass
class TrustResult:
    trust_score: float
    trust_flags: List[TrustFlag] = field(default_factory=list)

def check_skill_inflation(candidate: Dict[str, Any], text: str) -> List[TrustFlag]:
    years_exp = candidate.get("years_experience", 0)
    if not isinstance(years_exp, (int, float)):
        years_exp = 0.0
        
    skills = candidate.get("skills", [])
    if not isinstance(skills, list):
        skills = []
        
    if len(skills) > 15 and years_exp < 2.0:
        return [TrustFlag("Skill Inflation Detected: Many skills but <2 years exp.", "high", 0.3)]
    return []

def check_title_progression(candidate: Dict[str, Any]) -> List[TrustFlag]:
    """Validates career progression and flags erratic jumps."""
    years_exp = candidate.get("years_experience", 0)
    if not isinstance(years_exp, (int, float)):
        years_exp = 0.0
        
    title_keywords = ["principal", "staff", "head of", "director", "vp", "chief"]
    
    career = candidate.get("career_history", [])
    flags = []
    if isinstance(career, list):
        for role in career:
            title = ""
            if isinstance(role, dict):
                title = str(role.get("title", "")).lower()
            elif isinstance(role, str):
                title = role.lower()
                
            if any(k in title for k in title_keywords) and years_exp < 4.0:
                flags.append(TrustFlag("Seniority Mismatch: Senior title with low total experience.", "high", 0.4))
                break
    return flags

def check_keyword_stuffing(text: str) -> List[TrustFlag]:
    words = text.split()
    if not words:
        return []
        
    word_counts = {}
    for w in words:
        if len(w) > 3:
            word_counts[w] = word_counts.get(w, 0) + 1
            
    max_freq = max(word_counts.values()) if word_counts else 0
    if max_freq > 20 and max_freq / len(words) > 0.05:
        return [TrustFlag("Keyword Stuffing Detected", "medium", 0.2)]
    return []

def check_langchain_only(text: str) -> List[TrustFlag]:
    negative_hits = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text)
    positive_hits = sum(1 for kw in STRONG_RETRIEVAL_KEYWORDS + MEDIUM_RETRIEVAL_KEYWORDS + RANKING_KEYWORDS if kw in text)
    
    if negative_hits > 0 and positive_hits == 0:
        return [TrustFlag("LangChain-only Profile without foundational IR skills.", "medium", 0.2)]
    return []

def check_timeline_inconsistency(candidate: Dict[str, Any]) -> List[TrustFlag]:
    career = candidate.get("career_history")
    if not isinstance(career, list):
        return []
        
    flags = []
    for role in career:
        if isinstance(role, dict):
            start = role.get("start_year") or role.get("start_date")
            end = role.get("end_year") or role.get("end_date")
            
            if isinstance(start, (int, str)) and isinstance(end, (int, str)):
                try:
                    s_val = int(str(start)[:4])
                    e_val = int(str(end)[:4])
                    if s_val > e_val:
                        flags.append(TrustFlag("Timeline Inconsistency: End date before start date.", "high", 0.3))
                        break
                except ValueError:
                    pass
    return flags

def check_experience_consistency(candidate: Dict[str, Any]) -> List[TrustFlag]:
    """Checks if total years of experience aligns with the sum of durations of individual roles."""
    years_exp = candidate.get("years_experience", 0)
    if not isinstance(years_exp, (int, float)):
        return []
        
    career = candidate.get("career_history")
    if not isinstance(career, list):
        return []
        
    total_role_years = 0
    for role in career:
        if isinstance(role, dict):
            start = role.get("start_year")
            end = role.get("end_year")
            if isinstance(start, (int, str)) and isinstance(end, (int, str)):
                try:
                    s_val = int(str(start)[:4])
                    e_val = int(str(end)[:4])
                    if e_val >= s_val:
                        total_role_years += (e_val - s_val)
                except ValueError:
                    pass
                    
    if total_role_years > 0 and abs(years_exp - total_role_years) > 5:
        return [TrustFlag("Experience Inconsistency: Stated years_experience vastly differs from career timeline.", "medium", 0.2)]
        
    return []

def check_retrieval_vs_total_experience(candidate: Dict[str, Any], text: str) -> List[TrustFlag]:
    """Ensures a candidate doesn't claim massive retrieval experience if total experience is low."""
    years_exp = candidate.get("years_experience", 0)
    if not isinstance(years_exp, (int, float)):
        years_exp = 0.0
        
    retrieval_hits = any(kw in text for kw in STRONG_RETRIEVAL_KEYWORDS + MEDIUM_RETRIEVAL_KEYWORDS)
    if retrieval_hits and years_exp < 1.0:
        return [TrustFlag("Retrieval vs Total Experience Mismatch: Claims retrieval skills but has very low total experience.", "low", 0.1)]
        
    return []

def evaluate_trust(candidate: Dict[str, Any]) -> TrustResult:
    flags = []
    chunks = extract_text_with_context(candidate)
    text = " ".join(chunks)
    
    flags.extend(check_skill_inflation(candidate, text))
    flags.extend(check_title_progression(candidate))
    flags.extend(check_keyword_stuffing(text))
    flags.extend(check_langchain_only(text))
    flags.extend(check_timeline_inconsistency(candidate))
    flags.extend(check_experience_consistency(candidate))
    flags.extend(check_retrieval_vs_total_experience(candidate, text))
    
    base_score = 1.0
    total_penalty = sum(f.penalty for f in flags)
    
    trust_score = max(MIN_TRUST_SCORE, base_score - total_penalty)
    
    return TrustResult(trust_score=trust_score, trust_flags=flags)
