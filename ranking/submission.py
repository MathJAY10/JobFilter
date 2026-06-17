import csv
from typing import List, Dict, Any
from .reranker import compute_scores
from .explanation import generate_explanation

def process_candidates(candidates: List[Dict[str, Any]], top_k: int = 100) -> List[Dict[str, Any]]:
    """Processes a list of candidates, returning the top K ranked candidates."""
    results = []
    
    for candidate in candidates:
        candidate_id = candidate.get("candidate_id", "unknown")
        
        fit_score, final_score, features, trust_result = compute_scores(candidate)
        explanation = generate_explanation(features, trust_result)
        
        results.append({
            "candidate_id": candidate_id,
            "score": final_score,
            "reasoning": explanation
        })
        
    # Sort by final score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Assign ranks
    top_results = results[:top_k]
    for i, res in enumerate(top_results):
        res["rank"] = i + 1
        
    return top_results

def generate_submission_file(candidates: List[Dict[str, Any]], output_path: str = "submission.csv", top_k: int = 100):
    """Generates the final submission CSV file."""
    ranked = process_candidates(candidates, top_k=top_k)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(ranked)
