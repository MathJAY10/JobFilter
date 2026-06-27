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
    profile = candidate.get("profile") or {}
    years_exp = float(profile.get("years_of_experience") or candidate.get("years_experience") or 0.0)
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
    profile = candidate.get("profile") or {}
    years_exp = float(profile.get("years_of_experience") or candidate.get("years_experience") or 0.0)
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

def _parse_year(val) -> int:
    """Parse a year from an int, ISO date string (YYYY-MM-DD), or year-only string."""
    if val is None:
        return 0
    try:
        return int(str(val)[:4])
    except (ValueError, TypeError):
        return 0

def check_timeline_inconsistency(candidate: Dict[str, Any]) -> List[TrustFlag]:
    """Checks for roles where end_date < start_date using ISO date strings."""
    career = candidate.get("career_history")
    if not isinstance(career, list):
        return []

    flags = []
    for role in career:
        if not isinstance(role, dict):
            continue
        # Schema fields: start_date / end_date (ISO strings). Fallback: start_year/end_year.
        start = role.get("start_date") or role.get("start_year")
        end   = role.get("end_date")   or role.get("end_year")
        # Skip current roles (end_date is null)
        if end is None or str(end).strip().lower() in ("", "null", "none", "present"):
            continue
        s_val = _parse_year(start)
        e_val = _parse_year(end)
        if s_val > 0 and e_val > 0 and s_val > e_val:
            flags.append(TrustFlag("Timeline Inconsistency: End date before start date.", "high", 0.3))
            break
    return flags

def check_experience_consistency(candidate: Dict[str, Any]) -> List[TrustFlag]:
    """Checks if total years of experience aligns with sum of role durations.
    Uses duration_months (always present in schema) as primary source,
    falling back to start_date/end_date parsing.
    """
    profile = candidate.get("profile") or {}
    years_exp = float(profile.get("years_of_experience") or candidate.get("years_experience") or 0.0)
    if years_exp <= 0:
        return []

    career = candidate.get("career_history")
    if not isinstance(career, list) or len(career) == 0:
        return []

    total_months = 0
    for role in career:
        if not isinstance(role, dict):
            continue
        # Primary: duration_months (always present per schema)
        dm = role.get("duration_months")
        if isinstance(dm, (int, float)) and dm >= 0:
            total_months += float(dm)
        else:
            # Fallback: derive from start_date / end_date
            start = role.get("start_date") or role.get("start_year")
            end   = role.get("end_date")   or role.get("end_year")
            if end is None or str(end).strip().lower() in ("", "null", "none", "present"):
                continue
            s_val = _parse_year(start)
            e_val = _parse_year(end)
            if s_val > 0 and e_val >= s_val:
                total_months += (e_val - s_val) * 12

    total_role_years = total_months / 12.0
    if total_role_years > 0 and abs(years_exp - total_role_years) > 5:
        return [TrustFlag(
            f"Experience Inconsistency: Stated {years_exp:.1f} yrs vs career timeline {total_role_years:.1f} yrs.",
            "medium", 0.2
        )]
    return []

def check_retrieval_vs_total_experience(candidate: Dict[str, Any], text: str) -> List[TrustFlag]:
    """Ensures a candidate doesn't claim massive retrieval experience if total experience is low."""
    profile = candidate.get("profile") or {}
    years_exp = float(profile.get("years_of_experience") or candidate.get("years_experience") or 0.0)
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
