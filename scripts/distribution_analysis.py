import json
import sys
import os
import statistics

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores

def get_percentile(data, p):
    if not data: return 0.0
    data = sorted(data)
    k = (len(data) - 1) * (p/100.0)
    f = int(k)
    c = int(k) + 1 if int(k) + 1 < len(data) else int(k)
    return data[f] + (data[c] - data[f]) * (k - f)

def run_distribution(filepath="top_10k_candidates.parquet"):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found. Running on sample data instead.")
        filepath = "req/sample_candidates.json"
        
    try:
        if filepath.endswith(".parquet"):
            import pandas as pd
            df = pd.read_parquet(filepath)
            candidates = df.to_dict('records')
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return
            
    sem_scores = []
    ret_scores = []
    trust_scores = []
    final_scores = []
    
    for c in candidates:
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
        
        sem = c.get("semantic_similarity", 0.0)
        sem_scores.append(float(sem))
        
        fit, final, feat, trust = compute_scores(c)
        ret_scores.append(feat.retrieval_expertise.score)
        trust_scores.append(trust.trust_score)
        final_scores.append(final)
        
    metrics = [
        ("semantic_similarity", sem_scores),
        ("retrieval_score", ret_scores),
        ("trust_score", trust_scores),
        ("final_score", final_scores)
    ]
    
    print("\n=== DISTRIBUTION ANALYSIS ===")
    for name, data in metrics:
        print(f"\n--- {name} ---")
        print(f"Min: {min(data):.4f}")
        print(f"Max: {max(data):.4f}")
        print(f"Mean: {statistics.mean(data):.4f}")
        print(f"P50: {get_percentile(data, 50):.4f}")
        print(f"P75: {get_percentile(data, 75):.4f}")
        print(f"P90: {get_percentile(data, 90):.4f}")
        print(f"P95: {get_percentile(data, 95):.4f}")
        print(f"P99: {get_percentile(data, 99):.4f}")

if __name__ == "__main__":
    run_distribution()
