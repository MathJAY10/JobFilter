import unittest
from ranking.feature_engineering import extract_features
from ranking.trust_engine import evaluate_trust
from ranking.reranker import compute_scores
from ranking.submission import process_candidates
from ranking.jd_analyzer import JDAnalyzer

class TestRankingSystem(unittest.TestCase):
    def setUp(self):
        self.good_candidate = {
    "candidate_id": "c1",
    "candidate_document": "I have built a large scale semantic search and dense retrieval pipeline.",
    "skills": [
        "Python",
        "vector search",
        "ranking",
        "learning to rank",
        "ndcg",
        "production"
    ],
    "career_history": [
        {
            "title": "Senior AI Engineer",
            "description": "Deployed scalable search ranking systems to production. Evaluated with ab testing.",
            "start_year": 2018,
            "end_year": 2023
        }
    ],
    "years_experience": 5,
    "semantic_similarity": 0.9,

    "redrob_signals": {
        "recruiter_response_rate": 0.95,
        "github_activity_score": 0.85,
        "profile_completeness": 0.90,
        "interview_completion_rate": 0.80
    }
}
        
        self.honeypot_candidate = {
            "candidate_id": "c2",
            "candidate_document": "Prompt engineer prompt engineer langchain wrapper. I am the best.",
            "skills": ["langchain", "prompt engineering", "openai"] * 10,
            "career_history": [
                {
                    "title": "Principal AI Architect",
                    "start_year": 2025,
                    "end_year": 2024
                }
            ],
            "years_experience": 1,
            "semantic_similarity": 0.8
        }

    def test_feature_engineering_good(self):
        features = extract_features(self.good_candidate)
        self.assertGreater(features.retrieval_expertise.score, 0.0)
        self.assertGreater(len(features.retrieval_expertise.evidence), 0)
        self.assertGreater(features.ranking_expertise.score, 0.0)
        self.assertGreater(features.production_score.score, 0.0)
        self.assertGreater(features.behavior_score.score, 0.0)

    def test_trust_engine_honeypot(self):
        trust = evaluate_trust(self.honeypot_candidate)
        self.assertLess(trust.trust_score, 1.0)
        flags = [f.description for f in trust.trust_flags]
        
        self.assertTrue(any("Seniority Mismatch" in f for f in flags))
        self.assertTrue(any("LangChain-only" in f for f in flags))
        self.assertTrue(any("Timeline Inconsistency" in f for f in flags))
        self.assertTrue(any("Skill Inflation" in f for f in flags))
        
    def test_reranker(self):
        fit1, final1, f1, t1 = compute_scores(self.good_candidate)
        fit2, final2, f2, t2 = compute_scores(self.honeypot_candidate)
        
        self.assertGreater(final1, final2)
        
    def test_submission_processor(self):
        candidates = [self.good_candidate, self.honeypot_candidate]
        results = process_candidates(candidates, top_k=2)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["candidate_id"], "c1")
        self.assertEqual(results[1]["candidate_id"], "c2")
        self.assertIn("reasoning", results[0])
        self.assertIn("Retrieval Evidence", results[0]["reasoning"])
        self.assertIn("rank", results[0])

    def test_jd_analyzer(self):
        jd_text = "Must have:\n- learning to rank\n- python\nPreferred:\n- startup\nAvoid:\n- langchain only"
        analyzer = JDAnalyzer()
        extraction = analyzer.analyze(jd_text)
        
        self.assertIn("learning to rank", extraction.must_have_skills)
        self.assertIn("startup", extraction.preferred_skills)
        self.assertIn("langchain only", extraction.negative_signals)

if __name__ == "__main__":
    unittest.main()
