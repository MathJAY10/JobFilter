import json
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores

def audit_candidate(candidate: dict):
    # Patch candidate object so trust_engine uses the correct years_exp path safely
    years_exp = candidate.get("profile", {}).get("years_of_experience", 0)
    candidate["years_experience"] = years_exp
    
    fit_score, final_score, features, trust_result = compute_scores(candidate)
    
    print("="*80)
    print(f"Candidate ID: {candidate.get('candidate_id')}")
    print("="*80)
    
    print("\n--- Feature Scores ---")
    print(f"Retrieval:   {features.retrieval_expertise.score:.4f}")
    print(f"Ranking:     {features.ranking_expertise.score:.4f}")
    print(f"Evaluation:  {features.evaluation_score.score:.4f}")
    print(f"Production:  {features.production_score.score:.4f}")
    print(f"Startup:     {features.startup_score.score:.4f}")
    print(f"Behavior:    {features.behavior_score.score:.4f}")
    
    print("\n--- Trust ---")
    print(f"Trust Score: {trust_result.trust_score:.4f}")
    print("Trust Flags:")
    if not trust_result.trust_flags:
        print("  - None")
    else:
        for f in trust_result.trust_flags:
            print(f"  - [{f.severity.upper()}] {f.description} (Penalty: -{f.penalty})")
            
    print("\n--- Ranking ---")
    print(f"Fit Score:   {fit_score:.4f}")
    print(f"Final Score: {final_score:.4f}")
    
    print("\n--- Evidence ---")
    print("Retrieval Evidence:")
    if features.retrieval_expertise.evidence:
        for e in features.retrieval_expertise.evidence:
            print(f"  * {e}")
    else:
        print("  * None")
        
    print("Ranking Evidence:")
    if features.ranking_expertise.evidence:
        for e in features.ranking_expertise.evidence:
            print(f"  * {e}")
    else:
        print("  * None")

    print("Production Evidence:")
    if features.production_score.evidence:
        for e in features.production_score.evidence:
            print(f"  * {e}")
    else:
        print("  * None")
    print("\n")

def main():
    parser = argparse.ArgumentParser(description="Audit a candidate's ranking decisions.")
    parser.add_argument("--candidate_id", type=str, help="Candidate ID to audit")
    parser.add_argument("--file", type=str, default="req/sample_candidates.json", help="Path to candidates JSON file")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            candidates = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find file {args.file}")
        sys.exit(1)
        
    if args.candidate_id:
        target = next((c for c in candidates if c.get("candidate_id") == args.candidate_id), None)
        if target:
            audit_candidate(target)
        else:
            print(f"Candidate {args.candidate_id} not found in {args.file}.")
    else:
        # Audit all if none specified
        for c in candidates:
            audit_candidate(c)

if __name__ == "__main__":
    main()
