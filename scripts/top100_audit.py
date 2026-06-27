import json
import sys
import os

try:
    import pandas as pd
except ImportError:
    pd = None

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores

def load_data(filepath):
    if filepath.endswith(".parquet") and pd is not None:
        df = pd.read_parquet(filepath)
        return df.to_dict('records')
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

def run_top100(filepath="top_10k_candidates.parquet"):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found. Running on sample_candidates.json for testing.")
        filepath = "req/sample_candidates.json"
        
    candidates = load_data(filepath)
    results = []
    for c in candidates:
        # Some parquet parsing might be needed if fields are strings
        if isinstance(c.get("profile"), str):
            c["profile"] = json.loads(c["profile"])
        if isinstance(c.get("skills"), str):
            c["skills"] = json.loads(c["skills"])
        if isinstance(c.get("career_history"), str):
            c["career_history"] = json.loads(c["career_history"])
        if isinstance(c.get("redrob_signals"), str):
            c["redrob_signals"] = json.loads(c["redrob_signals"])
            
        years_exp = c.get("profile", {}).get("years_of_experience", 0)
        c["years_experience"] = years_exp
        
        fit, final, feat, trust = compute_scores(c)
        
        evidences = []
        if feat.retrieval_expertise.evidence:
            evidences.append(feat.retrieval_expertise.evidence[0])
        elif feat.ranking_expertise.evidence:
            evidences.append(feat.ranking_expertise.evidence[0])
        elif feat.production_score.evidence:
            evidences.append(feat.production_score.evidence[0])
            
        top_ev = evidences[0].replace("\n", " ") if evidences else "None"
        
        results.append({
            "candidate_id": c.get("candidate_id"),
            "fit_score": fit,
            "trust_score": trust.trust_score,
            "trust_flags": [f.description for f in trust.trust_flags],
            "final_score": final,
            "top_evidence": top_ev
        })
        
    results = sorted(results, key=lambda x: x["final_score"], reverse=True)
    top_100 = results[:100]
    
    with open("ranking/top100_audit.md", "w", encoding="utf-8") as f:
        f.write("# Top 100 Candidates Audit\n\n")
        f.write("| Rank | Candidate ID | Final Score | Fit Score | Trust Score | Flags | Top Evidence |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(top_100):
            flags = ", ".join(r["trust_flags"]) if r["trust_flags"] else "None"
            f.write(f"| {i+1} | {r['candidate_id']} | {r['final_score']:.4f} | {r['fit_score']:.4f} | {r['trust_score']:.4f} | {flags} | {r['top_evidence'][:80]} |\n")
            
    print("Generated ranking/top100_audit.md")

if __name__ == "__main__":
    run_top100()
