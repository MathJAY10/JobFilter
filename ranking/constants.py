from typing import List, Dict

MIN_TRUST_SCORE: float = 0.15

STRONG_RETRIEVAL_KEYWORDS: List[str] = [
    "learning to rank",
    "cross encoder",
    "cross-encoder",
    "ann",
    "hnsw",
    "custom ann"
]

MEDIUM_RETRIEVAL_KEYWORDS: List[str] = [
    "dense retrieval",
    "vector search",
    "bm25",
    "elasticsearch",
    "faiss",
    "pinecone",
    "qdrant",
    "weaviate",
    "milvus",
    "opensearch"
]

WEAK_RETRIEVAL_KEYWORDS: List[str] = [
    "rag",
    "langchain",
    "llamaindex"
]

RANKING_KEYWORDS: List[str] = [
    "ranking",
    "relevance",
    "search ranking",
    "reranker"
]

EVALUATION_KEYWORDS: List[str] = [
    "evaluation",
    "ndcg",
    "mrr",
    "map",
    "offline-to-online",
    "a/b test",
    "ab test"
]

PRODUCTION_KEYWORDS: List[str] = [
    "production systems",
    "production environment",
    "productionizing",
    "production ml",
    "deployed",
    "scale",
    "latency",
    "users",
    "monitoring",
    "reliability",
    "throughput",
    "qps"
]

STARTUP_KEYWORDS: List[str] = [
    "founding engineer",
    "0 to 1",
    "0-to-1",
    "co-founder"
]

NEGATIVE_KEYWORDS: List[str] = [
    "prompt engineer",
    "langchain only",
    "chatbot builder only",
    "wrapper"
]

# Explicit weights for behavior scoring based on Redrob Signals
BEHAVIOR_WEIGHTS: Dict[str, float] = {
    "recruiter_response_rate": 0.35,       # 0.0-1.0
    "github_activity_score": 0.25,         # -1 to 100
    "profile_completeness_score": 0.20,    # 0-100
    "interview_completion_rate": 0.20      # 0.0-1.0
}

DEFAULT_WEIGHTS: Dict[str, float] = {
    "semantic": 0.25,
    "retrieval": 0.25,
    "ranking": 0.10,
    "evaluation": 0.10,
    "production": 0.15,
    "startup": 0.05,
    "behavior": 0.10
}
