import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores
import ranking.feature_engineering as fe
import ranking.constants as constants

def eval_all(candidates):
    results = {}
    for c in candidates:
        # Patch candidate object
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        c["years_experience"] = years_exp
        
        fit_score, final_score, features, trust_result = compute_scores(c)
        results[c["candidate_id"]] = {
            "final_score": final_score,
            "production_score": features.production_score.score,
            "startup_score": features.startup_score.score,
            "profile": str(c.get("profile", {}).get("summary", "")) + " " + str([r.get('title') for r in c.get('career_history', [])])
        }
    return results

def write_report(before, after, rank_before, rank_after):
    lines = ["# Before / After Report: Production & Startup Fixes\n"]
    
    lines.append("## Top 20 Candidates: Before\n")
    for i, (cid, data) in enumerate(rank_before[:20]):
        lines.append(f"{i+1}. {cid} - Score: {data['final_score']:.4f} | Prod: {data['production_score']:.2f} | Startup: {data['startup_score']:.2f}")
        
    lines.append("\n## Top 20 Candidates: After\n")
    for i, (cid, data) in enumerate(rank_after[:20]):
        lines.append(f"{i+1}. {cid} - Score: {data['final_score']:.4f} | Prod: {data['production_score']:.2f} | Startup: {data['startup_score']:.2f}")

    lines.append("\n## Rank Changes\n")
    lines.append("| Candidate | Old Rank | New Rank | Old Score | New Score | Old Prod | New Prod | Old Startup | New Startup |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    
    b_map = {cid: idx+1 for idx, (cid, _) in enumerate(rank_before)}
    a_map = {cid: idx+1 for idx, (cid, _) in enumerate(rank_after)}
    
    demoted_marketing = []
    promoted_engineering = []
    
    for cid, data_after in after.items():
        data_before = before[cid]
        ra = b_map[cid]
        rn = a_map[cid]
        
        # Only show if rank or score changed significantly
        if ra != rn or data_before['final_score'] != data_after['final_score']:
            lines.append(f"| {cid} | {ra} | {rn} | {data_before['final_score']:.4f} | {data_after['final_score']:.4f} | {data_before['production_score']:.2f} | {data_after['production_score']:.2f} | {data_before['startup_score']:.2f} | {data_after['startup_score']:.2f} |")
            
            summary = data_before['profile'].lower()
            if rn > ra and (rn > 20 and ra <= 20):
                if 'marketing' in summary or 'content' in summary or 'design' in summary or 'writer' in summary:
                    demoted_marketing.append(cid)
            elif rn < ra and (rn <= 20 and ra > 20):
                promoted_engineering.append(cid)
                
    lines.append("\n## Highlights\n")
    lines.append("### Demoted Marketing/Content Candidates\n")
    if demoted_marketing:
        for cid in demoted_marketing:
            lines.append(f"- {cid}: Dropped out of Top 20 (Old Rank: {b_map[cid]}, New Rank: {a_map[cid]})")
    else:
        lines.append("- None detected crossing the Top 20 boundary, though scores dropped.")
        
    lines.append("\n### Promoted Engineering Candidates\n")
    if promoted_engineering:
        for cid in promoted_engineering:
            lines.append(f"- {cid}: Promoted into Top 20 (Old Rank: {b_map[cid]}, New Rank: {a_map[cid]})")
    else:
        lines.append("- None detected crossing the Top 20 boundary.")
        
    with open("ranking/before_after_report.md", "w", encoding='utf-8') as f:
        f.write("\n".join(lines))

def main():
    with open("req/sample_candidates.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
        
    before = eval_all(candidates)
    
    # Patch constants for the "After" run
    new_prod = [
        "production systems", "production environment", "productionizing", "production ml", 
        "deployed", "scale", "latency", "users", "monitoring", "reliability", "throughput", "qps"
    ]
    new_startup = [
        "founding engineer", "0 to 1", "0-to-1", "co-founder"
    ]
    
    fe.PRODUCTION_KEYWORDS = new_prod
    fe.STARTUP_KEYWORDS = new_startup
    
    after = eval_all(candidates)
    
    rank_before = sorted(before.items(), key=lambda x: x[1]["final_score"], reverse=True)
    rank_after = sorted(after.items(), key=lambda x: x[1]["final_score"], reverse=True)
    
    write_report(before, after, rank_before, rank_after)
    print("Generated ranking/before_after_report.md")

if __name__ == "__main__":
    main()
