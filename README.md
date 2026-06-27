# JobFilter — AI Candidate Ranking Pipeline

> End-to-end pipeline for the **Intelligent Candidate Discovery & Ranking Challenge**.  
> Processes 100,000 candidate profiles and produces a ranked Top-100 submission.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Folder Structure](#folder-structure)
5. [How to Run](#how-to-run)
6. [Pipeline Flow](#pipeline-flow)
7. [Scoring System](#scoring-system)
8. [Trust Engine](#trust-engine)
9. [Running Tests](#running-tests)
10. [Validation & Auditing](#validation--auditing)
11. [Submission Format](#submission-format)
12. [Key Files to Study](#key-files-to-study)

---

## Project Overview

JobFilter ranks 100,000 AI/ML candidates against a Job Description for an **Information Retrieval Engineer** role.

Each candidate is scored across 7 dimensions:
- **Semantic Similarity** — JD-aligned keyword matching
- **Retrieval Expertise** — FAISS, BM25, ANN, HNSW, vector search, cross-encoders
- **Ranking Expertise** — LTR, reranking, relevance scoring
- **Evaluation Score** — NDCG, MRR, A/B testing
- **Production Score** — deployed systems, scale, latency, QPS
- **Startup Score** — founding engineer, 0-to-1 experience
- **Behavior Score** — recruiter response rate, GitHub activity, completeness

Candidates are also filtered through a **Trust Engine** that detects skill inflation, seniority mismatch, fake timelines, and keyword stuffing.

---

## Prerequisites

- Python 3.9+
- pip

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/MathJAY10/JobFilter.git
cd JobFilter
```

### 2. Install dependencies
```bash
pip install pandas openpyxl
```

### 3. Place the dataset
Put the challenge dataset file in the `req/` folder:
```
req/candidates.jsonl      ← 100K candidate dataset (from challenge)
```

> **Note:** `req/` is gitignored. You must obtain the dataset from the challenge platform.

---

## Folder Structure

```
JobFilter/
│
├── generate_final_submission.py   ← ENTRY POINT (run this to produce output)
├── preprocessing.ipynb            ← EDA and data exploration notebook
├── submission.csv                 ← Final output (Top 100 ranked candidates)
├── submission.xlsx                ← XLSX version for portal upload
├── README.md
├── .gitignore
│
├── ranking/                       ← Core ranking engine (Python package)
│   ├── __init__.py
│   ├── constants.py               ← Keywords, weights, thresholds (tune here)
│   ├── feature_engineering.py     ← Extract all 6 feature dimensions
│   ├── trust_engine.py            ← Detect fake/inflated profiles
│   ├── reranker.py                ← Combine features + trust into final score
│   ├── submission.py              ← Sort, rank, and format Top-K output
│   ├── explanation.py             ← Generate reasoning text
│   ├── jd_analyzer.py             ← Job description keyword analysis
│   └── tests/
│       ├── mock_candidates.py     ← Synthetic test fixtures
│       └── test_ranking.py        ← 5 unit tests
│
├── req/                           ← Challenge inputs (gitignored, read-only)
│   ├── candidates.jsonl           ← 100K candidate dataset
│   ├── candidate_schema.json      ← Official JSON schema
│   ├── job_description.docx       ← Job description
│   ├── submission_spec.docx       ← Submission rules
│   ├── validate_submission.py     ← Official validator script
│   └── sample_candidates.json    ← Small sample for local testing
│
├── scripts/                       ← Audit, diagnostic, and validation tools
│   ├── audit_dataset.py           ← Full 100K schema compliance check
│   ├── full_trust_audit.py        ← Trust engine across all 100K records
│   ├── calibration.py             ← Score calibration
│   ├── stress_test.py             ← Edge-case tests
│   ├── honeypot_benchmark.py      ← Synthetic honeypot trust tests
│   ├── weight_sensitivity.py      ← Weight perturbation stability
│   ├── distribution_analysis.py   ← Score distribution analysis
│   ├── integration_check.py       ← Pre-ranking data validation
│   ├── top100_audit.py            ← Final Top-100 audit
│   └── debug_candidate.py         ← Debug a single candidate by ID
│
└── reports/                       ← Auto-generated reports (do not edit)
    ├── full_trust_audit_100k.md
    ├── dataset_audit_report.md
    ├── feature_contribution_report.md
    └── ...
```

---

## How to Run

### Step 1 — Generate the submission
```bash
python generate_final_submission.py
```
This will:
- Load all 100,000 candidates from `req/candidates.jsonl`
- Compute JD-aligned semantic similarity for each candidate
- Score and rank all candidates using the full ranking engine
- Output `submission.csv` (Top 100 candidates)
- Auto-validate the output using the official validator

### Step 2 — Convert to XLSX for portal upload
```bash
python -c "import pandas as pd; df = pd.read_csv('submission.csv'); df.to_excel('submission.xlsx', index=False)"
```

### Step 3 — Validate submission
```bash
python req/validate_submission.py submission.csv
```

---

## Pipeline Flow

```
req/candidates.jsonl  (100,000 records)
          │
          ▼
generate_final_submission.py
  ├── Skip malformed JSON lines (with warning)
  ├── compute_semantic_similarity()  ← JD-aligned IR keyword scoring
  └── ranking/submission.py → process_candidates(top_k=100)
                │
                ▼
          ranking/reranker.py → compute_scores()
            │
            ├── ranking/feature_engineering.py → extract_features()
            │     ├── Retrieval Expertise  (weight: 0.25)
            │     ├── Ranking Expertise    (weight: 0.10)
            │     ├── Evaluation Score     (weight: 0.10)
            │     ├── Production Score     (weight: 0.15)
            │     ├── Startup Score        (weight: 0.05)
            │     └── Behavior Score       (weight: 0.10)
            │
            └── ranking/trust_engine.py → evaluate_trust()
                  ├── Skill Inflation check
                  ├── Seniority Mismatch check
                  ├── Timeline Inconsistency check
                  ├── Experience Consistency check
                  ├── LangChain-only Profile check
                  ├── Keyword Stuffing check
                  └── Retrieval vs Experience Mismatch check
                │
                ▼
     final_score = fit_score × trust_score
                │
                ▼
      submission.csv  →  submission.xlsx
  [candidate_id | rank | score | reasoning]
```

---

## Scoring System

Scores are computed in `ranking/constants.py` and `ranking/reranker.py`:

| Dimension | Weight | Source |
|---|---|---|
| Semantic Similarity | 0.25 | JD-aligned token matching |
| Retrieval Expertise | 0.25 | FAISS, BM25, ANN, HNSW, Elasticsearch... |
| Ranking Expertise | 0.10 | LTR, cross-encoder, reranker... |
| Evaluation Score | 0.10 | NDCG, MRR, A/B test... |
| Production Score | 0.15 | deployed, scale, latency, QPS... |
| Startup Score | 0.05 | founding engineer, 0-to-1... |
| Behavior Score | 0.10 | recruiter_response_rate, github, completeness |
| **Total** | **1.00** | |

**Final Score** = `fit_score × trust_score`  
**Trust Score** = `1.0 - sum(penalties)`, minimum `0.15`

---

## Trust Engine

Detects low-quality or fraudulent profiles in `ranking/trust_engine.py`:

| Check | Trigger | Penalty |
|---|---|---|
| Skill Inflation | >15 skills but <2 years experience | -0.30 |
| Seniority Mismatch | Senior title (VP/Director) but <4 years exp | -0.40 |
| Timeline Inconsistency | end_date before start_date | -0.30 |
| Experience Inconsistency | Stated YoE vs duration_months >5yr gap | -0.20 |
| LangChain-only Profile | Only wrapper tools, no foundational IR skills | -0.20 |
| Keyword Stuffing | Single word repeats >5% of all words | -0.20 |
| Retrieval Mismatch | Claims IR skills but <1 year total exp | -0.10 |

**Audit results on 100K dataset:** 98.6% candidates scored clean (trust = 1.0)

---

## Running Tests

```bash
python -m pytest ranking/tests/ -v
```

Expected output:
```
test_feature_engineering_good   PASSED
test_jd_analyzer                PASSED
test_reranker                   PASSED
test_submission_processor       PASSED
test_trust_engine_honeypot      PASSED
5 passed in 0.06s
```

---

## Validation & Auditing

```bash
# Validate full dataset schema compliance
python scripts/audit_dataset.py

# Run trust engine across all 100K candidates
python scripts/full_trust_audit.py

# Debug a specific candidate
python scripts/debug_candidate.py --candidate_id CAND_0039754

# Stress test with edge cases
python scripts/stress_test.py

# Honeypot benchmark
python scripts/honeypot_benchmark.py
```

---

## Submission Format

The output file must have exactly:

| Column | Type | Example |
|---|---|---|
| `candidate_id` | string | `CAND_0039754` |
| `rank` | int (1–100) | `1` |
| `score` | float | `0.6898` |
| `reasoning` | string | `Retrieval Evidence: 'faiss...'` |

Rules:
- Exactly **100 rows**
- Ranks **1–100**, all unique
- Scores **monotonically non-increasing** (rank 1 has highest score)
- **UTF-8** encoded

---

## Key Files to Study

| Order | File | What you'll learn |
|---|---|---|
| 1 | `ranking/constants.py` | All keywords and weights |
| 2 | `ranking/feature_engineering.py` | How features are extracted |
| 3 | `ranking/trust_engine.py` | How fake profiles are detected |
| 4 | `ranking/reranker.py` | How scores are combined |
| 5 | `generate_final_submission.py` | Full pipeline entry point |
| 6 | `ranking/tests/test_ranking.py` | Concrete good vs bad examples |
