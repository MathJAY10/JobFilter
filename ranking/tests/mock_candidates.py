"""Mock candidates for standalone evaluation based on candidate_schema.json."""

def create_base_candidate(cid: str) -> dict:
    return {
        "candidate_id": cid,
        "profile": {
            "years_of_experience": 5,
            "summary": "AI Engineer"
        },
        "years_experience": 5, # Flat field for backwards compatibility with our engine
        "career_history": [],
        "education": [],
        "skills": [],
        "redrob_signals": {
            "github_activity_score": 80,
            "profile_completeness_score": 90,
            "recruiter_response_rate": 0.8
        },
        "semantic_similarity": 0.85
    }

strong_candidate = create_base_candidate("CAND_0000001")
strong_candidate["profile"]["summary"] = "Senior AI Engineer with deep experience in building custom ANN and cross-encoder models for production search systems. Strong focus on learning to rank and NDCG optimization."
strong_candidate["years_experience"] = 6
strong_candidate["career_history"] = [
    {
        "company": "Tech Corp",
        "title": "Senior Machine Learning Engineer",
        "start_date": "2020-01-01",
        "end_date": "2024-01-01",
        "start_year": 2020,
        "end_year": 2024,
        "description": "Deployed learning to rank systems. Improved NDCG by 15%. Handled production latency and scale."
    },
    {
        "company": "Startup Inc",
        "title": "Machine Learning Engineer",
        "start_date": "2018-01-01",
        "end_date": "2020-01-01",
        "start_year": 2018,
        "end_year": 2020,
        "description": "Built dense retrieval and vector search using HNSW."
    }
]
strong_candidate["skills"] = [
    {"name": "learning to rank", "proficiency": "expert", "endorsements": 10},
    {"name": "cross encoder", "proficiency": "expert", "endorsements": 8},
    {"name": "production", "proficiency": "advanced", "endorsements": 5}
]

weak_candidate = create_base_candidate("CAND_0000002")
weak_candidate["years_experience"] = 2
weak_candidate["profile"]["summary"] = "Software engineer interested in AI and RAG."
weak_candidate["career_history"] = [
    {
        "title": "Software Engineer",
        "start_year": 2022,
        "end_year": 2024,
        "description": "Worked on backend microservices. Built a small RAG chatbot."
    }
]
weak_candidate["skills"] = [
    {"name": "rag", "proficiency": "beginner", "endorsements": 1},
    {"name": "python", "proficiency": "intermediate", "endorsements": 2}
]
weak_candidate["semantic_similarity"] = 0.60

honeypot_candidate = create_base_candidate("CAND_0000003")
honeypot_candidate["years_experience"] = 1
honeypot_candidate["profile"]["summary"] = "I am the best principal staff director of AI. Learning to rank learning to rank learning to rank learning to rank learning to rank learning to rank learning to rank learning to rank learning to rank learning to rank."
honeypot_candidate["career_history"] = [
    {
        "title": "Principal AI Director",
        "start_year": 2024,
        "end_year": 2023, # Timeline inconsistency
        "description": "Learning to rank learning to rank learning to rank."
    }
]
# Skill inflation
honeypot_candidate["skills"] = [{"name": f"Skill_{i}", "proficiency": "expert", "endorsements": 0} for i in range(20)]

langchain_only_candidate = create_base_candidate("CAND_0000004")
langchain_only_candidate["years_experience"] = 3
langchain_only_candidate["profile"]["summary"] = "Prompt engineer specializing in langchain and chatbot wrapper development."
langchain_only_candidate["career_history"] = [
    {
        "title": "Prompt Engineer",
        "start_year": 2021,
        "end_year": 2024,
        "description": "Built langchain wrappers for openai. Only langchain."
    }
]
langchain_only_candidate["skills"] = [
    {"name": "langchain", "proficiency": "expert", "endorsements": 5},
    {"name": "prompt engineering", "proficiency": "expert", "endorsements": 5}
]

startup_candidate = create_base_candidate("CAND_0000005")
startup_candidate["years_experience"] = 4
startup_candidate["profile"]["summary"] = "Founding engineer at a 0 to 1 early stage startup. Owned the entire vector search pipeline."
startup_candidate["career_history"] = [
    {
        "title": "Founding Engineer",
        "start_year": 2020,
        "end_year": 2024,
        "description": "0 to 1 early stage startup. Built dense retrieval and vector search from scratch."
    }
]
startup_candidate["skills"] = [
    {"name": "vector search", "proficiency": "advanced", "endorsements": 3},
    {"name": "startup", "proficiency": "expert", "endorsements": 10}
]

ALL_MOCKS = [
    strong_candidate,
    weak_candidate,
    honeypot_candidate,
    langchain_only_candidate,
    startup_candidate
]
