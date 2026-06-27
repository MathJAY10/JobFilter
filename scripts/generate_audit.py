import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores
from ranking.explanation import generate_explanation

def load_candidates(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_audit(candidates):
    results = []
    
    for candidate in candidates:
        years_exp = candidate.get("profile", {}).get("years_of_experience", 0)
        candidate["years_experience"] = years_exp
        
        fit_score, final_score, features, trust_result = compute_scores(candidate)
        explanation = generate_explanation(features, trust_result)
        
        # Get top skills
        skills = candidate.get("skills", [])
        top_skills = []
        for s in skills:
            if isinstance(s, dict):
                top_skills.append(f"{s.get('name')} ({s.get('proficiency')})")
            else:
                top_skills.append(str(s))
        
        results.append({
            "candidate_id": candidate.get("candidate_id"),
            "years_experience": years_exp,
            "top_skills": top_skills[:5],
            "fit_score": fit_score,
            "final_score": final_score,
            "trust_score": trust_result.trust_score,
            "trust_flags": [f.description for f in trust_result.trust_flags],
            "features": features,
            "explanation": explanation
        })
        
    return results

def write_audit_report(results, output_path):
    # Sort by final score descending
    sorted_results = sorted(results, key=lambda x: x["final_score"], reverse=True)
    
    n = len(sorted_results)
    top_5 = sorted_results[:5]
    bottom_5 = sorted_results[-5:]
    mid_start = n // 2 - 2
    mid_5 = sorted_results[mid_start:mid_start+5]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Real Candidate Audit\n\n")
        
        def write_group(title, group):
            f.write(f"## {title}\n\n")
            for r in group:
                f.write(f"### Candidate ID: {r['candidate_id']}\n")
                f.write(f"- **Years Experience**: {r['years_experience']}\n")
                f.write(f"- **Top Skills**: {', '.join(r['top_skills'])}\n\n")
                
                feat = r['features']
                f.write("**Feature Scores:**\n")
                f.write(f"- Retrieval Score: {feat.retrieval_expertise.score:.4f}\n")
                f.write(f"- Ranking Score: {feat.ranking_expertise.score:.4f}\n")
                f.write(f"- Evaluation Score: {feat.evaluation_score.score:.4f}\n")
                f.write(f"- Production Score: {feat.production_score.score:.4f}\n")
                f.write(f"- Startup Score: {feat.startup_score.score:.4f}\n")
                f.write(f"- Behavior Score: {feat.behavior_score.score:.4f}\n\n")
                
                f.write("**Trust:**\n")
                f.write(f"- Trust Score: {r['trust_score']:.4f}\n")
                f.write(f"- Trust Flags: {r['trust_flags']}\n\n")
                
                f.write("**Ranking:**\n")
                f.write(f"- Fit Score: {r['fit_score']:.4f}\n")
                f.write(f"- Final Score: {r['final_score']:.4f}\n\n")
                
                f.write("**Top Evidence:**\n")
                evidences = []
                if feat.retrieval_expertise.evidence:
                    evidences.extend([f"Retrieval: {e}" for e in feat.retrieval_expertise.evidence[:2]])
                if feat.ranking_expertise.evidence:
                    evidences.extend([f"Ranking: {e}" for e in feat.ranking_expertise.evidence[:2]])
                if feat.production_score.evidence:
                    evidences.extend([f"Production: {e}" for e in feat.production_score.evidence[:2]])
                for e in evidences:
                    f.write(f"- {e}\n")
                f.write("\n")
                
                f.write("**Generated Explanation:**\n")
                f.write(f"> {r['explanation']}\n\n")
                f.write("---\n\n")
                
        write_group("Top 5 Candidates", top_5)
        write_group("Middle 5 Candidates", mid_5)
        write_group("Bottom 5 Candidates", bottom_5)

if __name__ == "__main__":
    candidates = load_candidates("req/sample_candidates.json")
    results = run_audit(candidates)
    write_audit_report(results, "ranking/real_candidate_audit.md")
    print("Audit generated at ranking/real_candidate_audit.md")
