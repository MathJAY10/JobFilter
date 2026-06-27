import json
import statistics
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores
from ranking.explanation import generate_explanation

def load_candidates(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_calibration(candidates):
    results = []
    
    for candidate in candidates:
        # Patch candidate object so trust_engine uses the correct years_exp path safely
        years_exp = candidate.get("profile", {}).get("years_of_experience", 0)
        candidate["years_experience"] = years_exp
        
        fit_score, final_score_a, features, trust_result = compute_scores(candidate)
        explanation = generate_explanation(features, trust_result)
        
        # Formula B
        final_score_b = fit_score * (0.7 + 0.3 * trust_result.trust_score)
        
        results.append({
            "candidate_id": candidate["candidate_id"],
            "fit_score": fit_score,
            "trust_score": trust_result.trust_score,
            "final_score_a": final_score_a,
            "final_score_b": final_score_b,
            "trust_flags": [f.description for f in trust_result.trust_flags],
            "explanation": explanation,
            "features": features
        })
        
    return results

def generate_score_distribution(results):
    dist = {}
    for key in ["fit_score", "trust_score", "final_score_a", "final_score_b"]:
        scores = [r[key] for r in results]
        dist[key] = {
            "min": min(scores),
            "max": max(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores)
        }
    return dist

def print_candidate_info(results):
    for r in results:
        print(f"Candidate ID: {r['candidate_id']}")
        print(f"Fit Score: {r['fit_score']:.4f}")
        print(f"Trust Score: {r['trust_score']:.4f}")
        print(f"Final Score A: {r['final_score_a']:.4f}")
        print(f"Final Score B: {r['final_score_b']:.4f}")
        print(f"Trust Flags: {r['trust_flags']}")
        print(f"Explanation: {r['explanation']}\n")

def generate_feature_report(results):
    lines = ["# Feature Contribution Report\n"]
    for r in results:
        f = r["features"]
        lines.append(f"## {r['candidate_id']}")
        lines.append(f"- Retrieval: {f.retrieval_expertise.score:.4f}")
        lines.append(f"- Ranking: {f.ranking_expertise.score:.4f}")
        lines.append(f"- Production: {f.production_score.score:.4f}")
        lines.append(f"- Startup: {f.startup_score.score:.4f}")
        lines.append(f"- Behavior: {f.behavior_score.score:.4f}\n")
    
    with open("feature_contribution_report.md", "w", encoding='utf-8') as f:
        f.write("\n".join(lines))

def generate_comparison_report(results):
    # Rank A
    ranked_a = sorted(results, key=lambda x: x["final_score_a"], reverse=True)
    rank_map_a = {r["candidate_id"]: idx + 1 for idx, r in enumerate(ranked_a)}
    
    # Rank B
    ranked_b = sorted(results, key=lambda x: x["final_score_b"], reverse=True)
    rank_map_b = {r["candidate_id"]: idx + 1 for idx, r in enumerate(ranked_b)}
    
    lines = ["# Formula A vs B Comparison\n"]
    lines.append("| Candidate ID | Rank A | Rank B | Score A | Score B | Diff Rank |")
    lines.append("|---|---|---|---|---|---|")
    
    for r in results:
        cid = r["candidate_id"]
        ra = rank_map_a[cid]
        rb = rank_map_b[cid]
        sa = r["final_score_a"]
        sb = r["final_score_b"]
        diff = ra - rb
        lines.append(f"| {cid} | {ra} | {rb} | {sa:.4f} | {sb:.4f} | {diff} |")
        
    with open("comparison_report.md", "w", encoding='utf-8') as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    candidates = load_candidates("req/sample_candidates.json")
    results = run_calibration(candidates)
    
    print_candidate_info(results)
    
    dist = generate_score_distribution(results)
    print("\n--- Score Distribution ---")
    print(json.dumps(dist, indent=2))
    
    generate_feature_report(results)
    generate_comparison_report(results)
    print("\nReports generated: feature_contribution_report.md, comparison_report.md")
