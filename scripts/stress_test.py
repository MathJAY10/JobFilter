import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores

def build_mock(cid, yoe, summary, skills, history, behavior=None):
    if behavior is None:
        behavior = {
            "recruiter_response_rate": 0.8,
            "github_activity_score": 80,
            "profile_completeness_score": 90,
            "interview_completion_rate": 1.0
        }
    return {
        "candidate_id": cid,
        "profile": {
            "years_of_experience": yoe,
            "summary": summary
        },
        "skills": skills,
        "career_history": history,
        "redrob_signals": behavior,
        "semantic_similarity": 0.8
    }

def run_stress_test():
    mocks = [
        # A: 20 YOE, no retrieval
        build_mock(
            "MOCK_A_20YOE_NO_IR",
            20.0,
            "Veteran software engineer with 20 years experience building Java monoliths.",
            [{"name": "Java", "proficiency": "expert"}],
            [{"title": "Senior Java Developer", "description": "Built big systems."}]
        ),
        # B: 2 YOE, all retrieval
        build_mock(
            "MOCK_B_2YOE_ALL_IR",
            2.0,
            "Junior engineer who loves learning to rank and cross encoders.",
            [{"name": "learning to rank", "proficiency": "expert"}, {"name": "pinecone", "proficiency": "expert"}],
            [{"title": "Junior ML", "description": "Used faiss and ndcg for a small project."}]
        ),
        # C: Strong retrieval, suspicious timeline
        build_mock(
            "MOCK_C_STRONG_IR_BAD_TIME",
            5.0,
            "Built scalable learning to rank systems and pinecone deployments.",
            [{"name": "learning to rank", "proficiency": "expert"}, {"name": "pinecone", "proficiency": "expert"}],
            [
                {"title": "Senior ML Engineer", "start_year": 2024, "end_year": 2023, "description": "Built learning to rank."}
            ]
        ),
        # D: Strong production, weak behavior
        build_mock(
            "MOCK_D_PROD_WEAK_BEHAVIOR",
            8.0,
            "Deployed large scale production systems.",
            [{"name": "production systems", "proficiency": "expert"}],
            [{"title": "Platform Engineer", "description": "Scale latency monitoring reliability."}],
            behavior={"recruiter_response_rate": 0.0, "github_activity_score": 0, "profile_completeness_score": 10, "interview_completion_rate": 0.0}
        )
    ]
    
    print("=== STRESS TEST ===")
    for m in mocks:
        years_exp = m.get("profile", {}).get("years_of_experience", 0)
        m["years_experience"] = years_exp
        fit, final, feat, trust = compute_scores(m)
        print(f"\nCandidate: {m['candidate_id']}")
        print(f"Fit: {fit:.4f} | Final: {final:.4f} | Trust: {trust.trust_score:.4f}")
        print(f"Flags: {[f.description for f in trust.trust_flags]}")
        print(f"IR Score: {feat.retrieval_expertise.score:.2f} | Prod Score: {feat.production_score.score:.2f} | Behavior: {feat.behavior_score.score:.2f}")

if __name__ == "__main__":
    run_stress_test()
