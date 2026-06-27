import pandas as pd
import json

df = pd.read_parquet("top_10k_candidates.parquet")

def get_percentiles(series):
    return {
        "p50": float(series.quantile(0.50)),
        "p75": float(series.quantile(0.75)),
        "p90": float(series.quantile(0.90)),
        "p95": float(series.quantile(0.95)),
        "p99": float(series.quantile(0.99))
    }

report_data = {
    "semantic_similarity": get_percentiles(df["semantic_similarity"]),
    "retrieval_score": get_percentiles(df["retrieval_score"]),
    "skill_match": get_percentiles(df["skill_match"]),
}

lengths = df["candidate_document"].str.len()
report_data["document_length"] = {
    "mean": float(lengths.mean()),
    "p95": float(lengths.quantile(0.95)),
    "max": float(lengths.max())
}

df_sorted = df.sort_values(by="retrieval_score", ascending=False)
top_20 = df_sorted.head(20)[["candidate_id", "semantic_similarity", "skill_match", "retrieval_score"]]
report_data["top_20"] = top_20.to_dict(orient="records")

with open("report_data.json", "w") as f:
    json.dump(report_data, f, indent=2)

print("Report data generated!")
