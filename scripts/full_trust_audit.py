"""
Run ALL 100K candidates through the trust engine and feature engineering.
Reports: flag distribution, years_exp reading, field coverage, edge cases.
"""
import json
import sys
import os
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ranking.trust_engine import evaluate_trust, _parse_year
from ranking.feature_engineering import extract_features

def run_full_audit(path="req/candidates.jsonl"):
    total = 0
    parse_errors = 0

    # Trust engine stats
    flag_counter        = Counter()
    trust_score_buckets = Counter()  # <0.5, 0.5-0.7, 0.7-0.9, 1.0
    yoe_zero_count      = 0         # candidates where profile.years_of_experience resolved to 0
    yoe_vals            = []

    # Field reading verification
    top_level_yoe_exists  = 0       # should be 0 (confirms old bug is gone)
    profile_yoe_exists    = 0       # should be 100000
    start_date_exists     = 0       # should be large
    start_year_exists     = 0       # should be 0 (old field)
    duration_months_total = 0

    # Feature score stats
    fit_scores = []

    print(f"Running full 100K trust + feature audit...")
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue

            total += 1

            # --- Verify field reading ---
            profile = rec.get("profile") or {}
            if rec.get("years_experience") is not None:
                top_level_yoe_exists += 1
            yoe = profile.get("years_of_experience")
            if yoe is not None:
                profile_yoe_exists += 1
                try:
                    yoe_vals.append(float(yoe))
                    if float(yoe) == 0.0:
                        yoe_zero_count += 1
                except:
                    pass

            # Check career date fields
            for role in (rec.get("career_history") or []):
                if not isinstance(role, dict): continue
                if role.get("start_date"):
                    start_date_exists += 1
                if role.get("start_year") is not None:
                    start_year_exists += 1
                dm = role.get("duration_months")
                if isinstance(dm, (int, float)):
                    duration_months_total += dm

            # --- Run trust engine ---
            try:
                trust = evaluate_trust(rec)
                for flag in trust.trust_flags:
                    flag_counter[flag.description[:60]] += 1
                ts = trust.trust_score
                if ts >= 1.0:
                    trust_score_buckets["1.0 (clean)"] += 1
                elif ts >= 0.9:
                    trust_score_buckets["0.9-1.0"] += 1
                elif ts >= 0.7:
                    trust_score_buckets["0.7-0.9"] += 1
                elif ts >= 0.5:
                    trust_score_buckets["0.5-0.7"] += 1
                else:
                    trust_score_buckets["<0.5 (heavy penalty)"] += 1
            except Exception as e:
                flag_counter[f"TRUST_ENGINE_CRASH: {str(e)[:50]}"] += 1

            # --- Run feature engineering ---
            try:
                features = extract_features(rec)
                fit = (
                    0.25 * features.retrieval_expertise.score +
                    0.25 * features.retrieval_expertise.score +
                    0.10 * features.ranking_expertise.score +
                    0.10 * features.evaluation_score.score +
                    0.15 * features.production_score.score +
                    0.05 * features.startup_score.score +
                    0.10 * features.behavior_score.score
                )
                fit_scores.append(fit)
            except Exception as e:
                flag_counter[f"FEATURE_ENG_CRASH: {str(e)[:50]}"] += 1

            if total % 10000 == 0:
                print(f"  {total:,} processed...")

    # --- Report ---
    print(f"\n{'='*62}")
    print(f"FULL 100K TRUST + FEATURE AUDIT")
    print(f"{'='*62}")
    print(f"Total processed     : {total:,}")
    print(f"Parse errors        : {parse_errors:,}")
    print()

    print("--- Field Reading Verification ---")
    print(f"  top-level 'years_experience' key exists  : {top_level_yoe_exists:,}  (should be 0 — old buggy field)")
    print(f"  profile.years_of_experience exists       : {profile_yoe_exists:,}  (should be {total:,})")
    print(f"  career start_date exists (real field)    : {start_date_exists:,}")
    print(f"  career start_year exists (old field)     : {start_year_exists:,}  (should be 0)")
    if yoe_vals:
        import statistics
        print(f"  YoE min/max/mean : {min(yoe_vals):.1f} / {max(yoe_vals):.1f} / {statistics.mean(yoe_vals):.2f}")
        print(f"  YoE = 0.0 count  : {yoe_zero_count:,}  (false positives from old bug)")
    print()

    print("--- Trust Score Distribution ---")
    for bucket, count in sorted(trust_score_buckets.items(), reverse=True):
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {bucket:<22} : {count:>6,} ({pct:5.1f}%) {bar}")
    print()

    print(f"--- Trust Flags Fired (across all {total:,} candidates) ---")
    if flag_counter:
        for flag, count in flag_counter.most_common():
            pct = count / total * 100
            print(f"  [{count:>6,} | {pct:5.1f}%] {flag}")
    else:
        print("  No flags fired on any candidate.")
    print()

    if fit_scores:
        import statistics
        print("--- Feature Score Distribution ---")
        print(f"  Min  : {min(fit_scores):.4f}")
        print(f"  Max  : {max(fit_scores):.4f}")
        print(f"  Mean : {statistics.mean(fit_scores):.4f}")
        print(f"  Median: {statistics.median(fit_scores):.4f}")

    # Save report
    os.makedirs("reports", exist_ok=True)
    with open("reports/full_trust_audit_100k.md", "w", encoding="utf-8") as out:
        out.write("# Full 100K Trust Engine Audit\n\n")
        out.write(f"- **Total records**: {total:,}\n")
        out.write(f"- **Parse errors**: {parse_errors:,}\n\n")
        out.write("## Field Reading Verification\n\n")
        out.write(f"| Field | Count | Expected |\n|---|---|---|\n")
        out.write(f"| `top-level years_experience` (old bug) | {top_level_yoe_exists:,} | 0 |\n")
        out.write(f"| `profile.years_of_experience` (correct) | {profile_yoe_exists:,} | {total:,} |\n")
        out.write(f"| `career.start_date` (real schema) | {start_date_exists:,} | large |\n")
        out.write(f"| `career.start_year` (old field) | {start_year_exists:,} | 0 |\n\n")
        out.write("## Trust Score Distribution\n\n")
        out.write("| Bucket | Count | % |\n|---|---|---|\n")
        for bucket, count in sorted(trust_score_buckets.items(), reverse=True):
            out.write(f"| {bucket} | {count:,} | {count/total*100:.1f}% |\n")
        out.write("\n## Trust Flags Fired\n\n")
        out.write("| Flag | Count | % |\n|---|---|---|\n")
        for flag, count in flag_counter.most_common():
            out.write(f"| `{flag}` | {count:,} | {count/total*100:.1f}% |\n")
    print(f"\nReport saved: reports/full_trust_audit_100k.md")

if __name__ == "__main__":
    run_full_audit()
