import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ranking.reranker import compute_scores
from ranking.stress_test import build_mock

def run_honeypot_benchmark():
    mocks = [
        # Keyword stuffing
        build_mock(
            "HONEYPOT_STUFFING",
            3.0,
            "learning to rank learning to rank learning to rank learning to rank learning to rank",
            [],
            [{"title": "Engineer", "description": "learning to rank " * 10}]
        ),
        # Title inflation
        build_mock(
            "HONEYPOT_TITLE",
            1.5,
            "Genius.",
            [],
            [{"title": "Principal Staff Director of AI", "description": "Pinecone."}]
        ),
        # Skill inflation
        build_mock(
            "HONEYPOT_SKILLS",
            1.0,
            "I know everything.",
            [{"name": f"Skill_{i}", "proficiency": "expert"} for i in range(25)],
            [{"title": "Intern", "description": "Did some stuff."}]
        ),
        # Fake retrieval
        build_mock(
            "HONEYPOT_FAKE_IR",
            3.0,
            "Prompt engineer langchain wrapper.",
            [{"name": "langchain", "proficiency": "expert"}],
            [{"title": "Prompt Engineer", "description": "Langchain only chatbot wrapper."}]
        )
    ]
    
    print("=== HONEYPOT BENCHMARK ===")
    for m in mocks:
        years_exp = m.get("profile", {}).get("years_of_experience", 0)
        m["years_experience"] = years_exp
        fit, final, feat, trust = compute_scores(m)
        
        reduction = fit - final
        
        print(f"\nCandidate: {m['candidate_id']}")
        print(f"Fit Score: {fit:.4f} -> Final Score: {final:.4f} (Reduction: {reduction:.4f})")
        print(f"Trust Score: {trust.trust_score:.4f}")
        for f in trust.trust_flags:
            print(f"  - [{f.severity.upper()}] {f.description} (Penalty: {f.penalty})")

if __name__ == "__main__":
    run_honeypot_benchmark()
