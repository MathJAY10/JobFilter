from typing import Dict, Any, Tuple
from .feature_engineering import CandidateFeatures, extract_features
from .trust_engine import TrustResult, evaluate_trust
from .constants import DEFAULT_WEIGHTS

def compute_scores(candidate: Dict[str, Any], weights: Dict[str, float] = None) -> Tuple[float, float, CandidateFeatures, TrustResult]:
    """Computes fit score and final score based on configurable weights and features."""
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Feature Engineering
    features = extract_features(candidate)
    
    # Base retrieval similarity provided by upstream
    semantic_similarity = candidate.get("semantic_similarity", 0.0)
    if not isinstance(semantic_similarity, (float, int)):
        semantic_similarity = 0.0
    
    # Fit Score calculation uses .score of ScoreWithEvidence
    fit_score = (
        weights["semantic"] * float(semantic_similarity) +
        weights["retrieval"] * features.retrieval_expertise.score +
        weights["ranking"] * features.ranking_expertise.score +
        weights["evaluation"] * features.evaluation_score.score +
        weights["production"] * features.production_score.score +
        weights["startup"] * features.startup_score.score +
        weights["behavior"] * features.behavior_score.score
    )
    
    # Trust Engine
    trust_result = evaluate_trust(candidate)
    
    # Final Score
    final_score = fit_score * trust_result.trust_score
    
    return fit_score, final_score, features, trust_result
