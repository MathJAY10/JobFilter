from .feature_engineering import CandidateFeatures
from .trust_engine import TrustResult

def generate_explanation(features: CandidateFeatures, trust_result: TrustResult) -> str:
    """Generates an evidence-based explanation of the candidate's ranking."""
    statements = []
    
    # Extract evidence (limit to top 1 evidence per category for conciseness)
    if features.retrieval_expertise.evidence:
        ev = features.retrieval_expertise.evidence[0]
        statements.append(f"Retrieval Evidence: '{ev}'.")
        
    if features.ranking_expertise.evidence:
        ev = features.ranking_expertise.evidence[0]
        statements.append(f"Ranking Evidence: '{ev}'.")
        
    if features.production_score.evidence:
        ev = features.production_score.evidence[0]
        statements.append(f"Production Evidence: '{ev}'.")
        
    if features.startup_score.evidence:
        ev = features.startup_score.evidence[0]
        statements.append(f"Startup Evidence: '{ev}'.")
        
    if features.behavior_score.evidence:
        ev = features.behavior_score.evidence[0]
        statements.append(f"Behavior Evidence: '{ev}'.")
        
    if not statements:
        statements.append("Moderate experience across standard AI requirements without strong text evidence.")
        
    # Trust flags
    if trust_result.trust_flags:
        flags_str = "; ".join(f"{f.severity.upper()}: {f.description}" for f in trust_result.trust_flags)
        statements.append(f"Flags detected: {flags_str}.")
        
    return " ".join(statements)
