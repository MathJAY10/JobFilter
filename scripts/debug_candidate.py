import json
from ranking.reranker import compute_scores
from ranking.explanation import generate_explanation
from ranking.tests.mock_candidates import ALL_MOCKS

def print_debug_info(candidate: dict):
    print("="*80)
    print(f"Debugging Candidate: {candidate.get('candidate_id')} - {candidate.get('profile', {}).get('summary', '')[:50]}...")
    print("="*80)
    
    fit_score, final_score, features, trust_result = compute_scores(candidate)
    explanation = generate_explanation(features, trust_result)
    
    print("\n--- Feature Scores ---")
    print(f"Retrieval Expertise: {features.retrieval_expertise.score:.2f}")
    if features.retrieval_expertise.evidence:
        print(f"  Evidence: {features.retrieval_expertise.evidence}")
        
    print(f"Ranking Expertise:   {features.ranking_expertise.score:.2f}")
    if features.ranking_expertise.evidence:
        print(f"  Evidence: {features.ranking_expertise.evidence}")
        
    print(f"Production Score:    {features.production_score.score:.2f}")
    if features.production_score.evidence:
        print(f"  Evidence: {features.production_score.evidence}")
        
    print(f"Startup Score:       {features.startup_score.score:.2f}")
    if features.startup_score.evidence:
        print(f"  Evidence: {features.startup_score.evidence}")
        
    print(f"Behavior Score:      {features.behavior_score.score:.2f}")
    
    print("\n--- Trust Engine ---")
    if trust_result.trust_flags:
        for flag in trust_result.trust_flags:
            print(f"  [{flag.severity.upper()}] {flag.description} (Penalty: -{flag.penalty})")
    else:
        print("  No flags detected. Candidate is clean.")
        
    print(f"Trust Score:         {trust_result.trust_score:.2f}")
    
    print("\n--- Final Scores ---")
    print(f"Base Fit Score:      {fit_score:.4f}")
    print(f"Final Score:         {final_score:.4f}")
    
    print("\n--- Explanation ---")
    print(explanation)
    print("\n\n")

if __name__ == "__main__":
    for mock in ALL_MOCKS:
        print_debug_info(mock)
