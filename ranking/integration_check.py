import json
import sys
import os

try:
    import pandas as pd
except ImportError:
    pd = None

def run_integration_check(filepath="top_10k_candidates.parquet"):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found. Running on sample data for testing.")
        filepath = "req/sample_candidates.json"
        
    candidates = []
    df = None
    
    try:
        if filepath.endswith(".parquet") and pd is not None:
            df = pd.read_parquet(filepath)
            candidates = df.to_dict('records')
        elif filepath.endswith(".jsonl"):
            with open(filepath, 'r', encoding='utf-8') as f:
                candidates = [json.loads(line) for line in f if line.strip()]
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
    except Exception as e:
        print(f"Failed to load data: {e}")
        return
            
    report = ["# Retrieval Integration Check Report\n"]
    report.append(f"**Input Data**: {filepath}")
    report.append(f"**Total Candidates**: {len(candidates)}\n")
    
    # 1. Required columns
    required = ["candidate_id", "semantic_similarity", "candidate_document"]
    if df is not None:
        columns = list(df.columns)
    elif candidates:
        columns = list(candidates[0].keys())
    else:
        columns = []
        
    missing = [c for c in required if c not in columns]
    report.append("## 1. Required Columns")
    if missing:
        report.append(f"**FAIL**: Missing required columns: {missing}\n")
    else:
        report.append("**PASS**: All required columns present.\n")
        
    # 2. Null analysis
    report.append("## 2. Null Analysis")
    nulls = {c: 0 for c in columns}
    for c in candidates:
        for col in columns:
            # check for true None or pandas NaN
            val = c.get(col)
            if val is None or (pd is not None and pd.isna(val)):
                nulls[col] += 1
    
    has_nulls = False
    for col, count in nulls.items():
        if count > 0:
            has_nulls = True
            report.append(f"- `{col}`: {count} null values")
    if not has_nulls:
        report.append("**PASS**: No null values found in any columns.\n")
    else:
        report.append("\n")
        
    # 4. Duplicate Candidate IDs
    report.append("## 4. Duplicate Candidate IDs")
    cids = [c.get("candidate_id") for c in candidates if c.get("candidate_id")]
    unique_cids = set(cids)
    duplicates = len(cids) - len(unique_cids)
    if duplicates > 0:
        report.append(f"**FAIL**: Found {duplicates} duplicate candidate IDs.\n")
    else:
        report.append("**PASS**: All candidate IDs are unique.\n")
        
    # 3 & 5. Semantic Similarity Distribution & Range
    report.append("## 3 & 5. Semantic Similarity")
    try:
        sims = [float(c.get("semantic_similarity", 0.0)) for c in candidates if c.get("semantic_similarity") is not None]
        if sims:
            sims.sort()
            import statistics
            report.append(f"- **Min**: {min(sims):.4f}")
            report.append(f"- **Max**: {max(sims):.4f}")
            report.append(f"- **Mean**: {statistics.mean(sims):.4f}\n")
            
            def get_p(data, p):
                if not data: return 0.0
                k = (len(data) - 1) * (p/100.0)
                f = int(k)
                c_idx = int(k) + 1 if int(k) + 1 < len(data) else int(k)
                return data[f] + (data[c_idx] - data[f]) * (k - f)
                
            report.append("**Distribution:**")
            report.append(f"- P50: {get_p(sims, 50):.4f}")
            report.append(f"- P75: {get_p(sims, 75):.4f}")
            report.append(f"- P90: {get_p(sims, 90):.4f}")
            report.append(f"- P95: {get_p(sims, 95):.4f}")
            report.append(f"- P99: {get_p(sims, 99):.4f}\n")
        else:
            report.append("**FAIL**: No semantic similarity scores found.\n")
    except Exception as e:
        report.append(f"**FAIL**: Error parsing semantic similarity: {e}\n")
        
    # 6. Missing Profile Fields
    report.append("## 6. Missing Profile Fields")
    missing_fields = {"profile": 0, "skills": 0, "career_history": 0}
    for c in candidates:
        for field in missing_fields:
            val = c.get(field)
            if not val or (isinstance(val, list) and len(val) == 0) or (isinstance(val, dict) and not val):
                missing_fields[field] += 1
                
    has_missing = False
    for field, count in missing_fields.items():
        if count > 0:
            has_missing = True
            report.append(f"- `{field}`: {count} candidates missing this field ({count/len(candidates)*100:.1f}%)")
            
    if not has_missing:
        report.append("**PASS**: All candidates have profile, skills, and career_history data.\n")
    else:
        report.append("\n")
        
    with open("ranking/integration_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Integration check completed. Output written to ranking/integration_report.md")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate retrieval output before ranking.")
    parser.add_argument("--input", type=str, default="top_10k_candidates.parquet", help="Path to input data (parquet, json, jsonl)")
    args = parser.parse_args()
    
    run_integration_check(args.input)
