import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores
from ranking.constants import DEFAULT_WEIGHTS

def evaluate_with_weights(candidates, weights):
    results = {}
    for c in candidates:
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        c["years_experience"] = years_exp
        fit, final, feat, trust = compute_scores(c, weights)
        results[c["candidate_id"]] = final
    return sorted(results.items(), key=lambda x: x[1], reverse=True)

def run_sensitivity(candidates):
    base_ranks = evaluate_with_weights(candidates, DEFAULT_WEIGHTS)
    base_order = [cid for cid, _ in base_ranks]
    
    variations = [0.9, 1.1, 0.8, 1.2]
    
    with open("weight_sensitivity_report.md", "w") as f:
        f.write("# Weight Sensitivity Report\n\n")
        f.write("Baseline ranks established.\n")
        
        for feature, base_weight in DEFAULT_WEIGHTS.items():
            f.write(f"\n## Perturbing '{feature}' (Base: {base_weight})\n")
            f.write("| Perturbation | Top 10 Overlap | Max Rank Shift |\n")
            f.write("|---|---|---|\n")
            
            for v in variations:
                new_weights = DEFAULT_WEIGHTS.copy()
                new_weights[feature] = base_weight * v
                
                # Normalize new weights so they sum to 1.0 roughly
                total = sum(new_weights.values())
                new_weights = {k: val/total for k, val in new_weights.items()}
                
                new_ranks = evaluate_with_weights(candidates, new_weights)
                new_order = [cid for cid, _ in new_ranks]
                
                top10_overlap = len(set(base_order[:10]).intersection(set(new_order[:10])))
                max_shift = max(abs(base_order.index(cid) - new_order.index(cid)) for cid in base_order)
                
                modifier = f"{(v - 1.0) * 100:+.0f}%"
                f.write(f"| {modifier} | {top10_overlap}/10 | {max_shift} positions |\n")
                
    print("Generated weight_sensitivity_report.md")

if __name__ == "__main__":
    with open("req/sample_candidates.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
    run_sensitivity(candidates)
