"""
Full 100K dataset audit against candidate_schema.json.
Checks: schema compliance, field coverage, trust engine field mapping,
timeline parsing, score distribution, and pipeline edge cases.
"""
import json
import re
import sys
from collections import defaultdict, Counter

CANDIDATE_ID_RE = re.compile(r"^CAND_[0-9]{7}$")
COMPANY_SIZE_ENUM = {"1-10","11-50","51-200","201-500","501-1000","1001-5000","5001-10000","10001+"}
PROFICIENCY_ENUM  = {"beginner","intermediate","advanced","expert"}
WORK_MODE_ENUM    = {"remote","hybrid","onsite","flexible"}
REQUIRED_TOP      = {"candidate_id","profile","career_history","education","skills","redrob_signals"}
REQUIRED_PROFILE  = {"anonymized_name","headline","summary","location","country",
                      "years_of_experience","current_title","current_company",
                      "current_company_size","current_industry"}
REQUIRED_SIGNALS  = {"profile_completeness_score","open_to_work_flag","profile_views_received_30d",
                      "applications_submitted_30d","recruiter_response_rate","avg_response_time_hours",
                      "github_activity_score","interview_completion_rate","offer_acceptance_rate",
                      "endorsements_received","notice_period_days","expected_salary_range_inr_lpa"}

def audit_dataset(path="req/candidates.jsonl", sample_size=None):
    issues         = defaultdict(int)
    field_coverage = defaultdict(int)
    yoe_vals       = []
    sem_sims       = []
    trust_flag_ctr = Counter()
    bad_timeline   = 0
    missing_signals= 0
    bad_cand_id    = 0
    no_career      = 0
    no_skills      = 0
    parse_errors   = 0
    total          = 0
    skipped        = 0

    print(f"Auditing {path}...")
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if sample_size and total >= sample_size:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                parse_errors += 1
                skipped += 1
                continue

            total += 1

            # --- 1. Required top-level keys ---
            for k in REQUIRED_TOP:
                if k not in rec:
                    issues[f"missing_top_key:{k}"] += 1
                else:
                    field_coverage[k] += 1

            # --- 2. candidate_id pattern ---
            cid = rec.get("candidate_id", "")
            if not CANDIDATE_ID_RE.match(str(cid)):
                bad_cand_id += 1

            # --- 3. profile fields ---
            profile = rec.get("profile") or {}
            if not isinstance(profile, dict):
                issues["profile_not_dict"] += 1
            else:
                for k in REQUIRED_PROFILE:
                    if not profile.get(k):
                        issues[f"missing_profile:{k}"] += 1
                yoe = profile.get("years_of_experience")
                if yoe is not None:
                    try:
                        yoe_vals.append(float(yoe))
                    except:
                        issues["yoe_not_numeric"] += 1
                # Check top-level years_experience (pipeline bug)
                if "years_experience" not in rec:
                    issues["missing_top_level_years_experience(pipeline_reads_this)"] += 1

            # --- 4. career_history ---
            career = rec.get("career_history", [])
            if not isinstance(career, list) or len(career) == 0:
                no_career += 1
            else:
                for role in career:
                    if not isinstance(role, dict): continue
                    # Schema uses start_date / end_date (strings), NOT start_year/end_year
                    has_start_date  = bool(role.get("start_date"))
                    has_end_date    = role.get("end_date") is not None
                    has_start_year  = role.get("start_year") is not None
                    has_end_year    = role.get("end_year")   is not None

                    if not has_start_date:
                        issues["career_missing_start_date"] += 1
                    if has_start_year:
                        field_coverage["career_has_start_year"] += 1
                    else:
                        issues["career_no_start_year(trust_timeline_uses_this)"] += 1

                    # Timeline parse check (what trust engine actually does)
                    start = role.get("start_year") or role.get("start_date")
                    end   = role.get("end_year")   or role.get("end_date")
                    if start and end:
                        try:
                            s_val = int(str(start)[:4])
                            e_val = int(str(end)[:4])
                            if s_val > e_val:
                                bad_timeline += 1
                        except:
                            issues["career_timeline_unparseable"] += 1

            # --- 5. skills ---
            skills = rec.get("skills", [])
            if not isinstance(skills, list) or len(skills) == 0:
                no_skills += 1
            else:
                for sk in skills:
                    if not isinstance(sk, dict): continue
                    p = sk.get("proficiency", "").lower()
                    if p not in PROFICIENCY_ENUM:
                        issues[f"invalid_proficiency:{p}"] += 1

            # --- 6. redrob_signals ---
            signals = rec.get("redrob_signals") or {}
            if not isinstance(signals, dict):
                issues["signals_not_dict"] += 1
            else:
                for k in REQUIRED_SIGNALS:
                    if signals.get(k) is None:
                        issues[f"missing_signal:{k}"] += 1
                rrr = signals.get("recruiter_response_rate")
                if rrr is not None and not (0 <= float(rrr) <= 1):
                    issues["rrr_out_of_range"] += 1
                gh = signals.get("github_activity_score")
                if gh is not None and float(gh) < -1:
                    issues["github_score_invalid"] += 1
                pc = signals.get("profile_completeness_score")
                if pc is not None and not (0 <= float(pc) <= 100):
                    issues["completeness_out_of_range"] += 1

            if total % 10000 == 0:
                print(f"  Processed {total:,} records...")

    print(f"\n{'='*60}")
    print(f"DATASET AUDIT COMPLETE")
    print(f"{'='*60}")
    print(f"Total records processed : {total:,}")
    print(f"Parse errors (skipped)  : {parse_errors:,}")
    print(f"Bad candidate_id format : {bad_cand_id:,}")
    print(f"No career history       : {no_career:,}")
    print(f"No skills               : {no_skills:,}")
    print(f"Bad timelines (end<start): {bad_timeline:,}")

    if yoe_vals:
        import statistics
        print(f"\nYears of Experience (profile.years_of_experience):")
        print(f"  Min: {min(yoe_vals):.1f} | Max: {max(yoe_vals):.1f}")
        print(f"  Mean: {statistics.mean(yoe_vals):.2f} | Median: {statistics.median(yoe_vals):.2f}")

    print(f"\n--- All Issues Found ({sum(issues.values())} total occurrences) ---")
    for k, v in sorted(issues.items(), key=lambda x: -x[1]):
        pct = v / total * 100
        flag = " *** CRITICAL ***" if v > total * 0.05 else ""
        print(f"  [{v:>7,} | {pct:5.1f}%] {k}{flag}")

    # Save report
    with open("reports/dataset_audit_report.md", "w", encoding="utf-8") as out:
        out.write("# Full 100K Dataset Audit Report\n\n")
        out.write(f"- **Total records**: {total:,}\n")
        out.write(f"- **Parse errors**: {parse_errors:,}\n")
        out.write(f"- **Bad candidate_id**: {bad_cand_id:,}\n")
        out.write(f"- **No career history**: {no_career:,}\n")
        out.write(f"- **No skills**: {no_skills:,}\n")
        out.write(f"- **Bad timelines**: {bad_timeline:,}\n\n")
        out.write("## Issues by Frequency\n\n")
        out.write("| Occurrences | % of Dataset | Issue |\n")
        out.write("|---|---|---|\n")
        for k, v in sorted(issues.items(), key=lambda x: -x[1]):
            pct = v / total * 100
            flag = " ⚠️ CRITICAL" if v > total * 0.05 else ""
            out.write(f"| {v:,} | {pct:.1f}% | `{k}`{flag} |\n")
    print(f"\nReport saved to reports/dataset_audit_report.md")

if __name__ == "__main__":
    audit_dataset()
