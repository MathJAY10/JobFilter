# Ranking Engine

This module is responsible for candidate ranking, trust evaluation, explainability, and validation for the AI Hiring Challenge.

## Core Components

### Feature Engineering

File:

```text
feature_engineering.py
```

Extracts:

* Retrieval Expertise
* Ranking Expertise
* Evaluation Expertise
* Production Experience
* Startup Signals
* Behavioral Signals

---

### Trust Engine

File:

```text
trust_engine.py
```

Detects:

* Skill Inflation
* Title Inflation
* Seniority Mismatch
* Timeline Inconsistency
* Keyword Stuffing
* LangChain-only Profiles

Outputs:

```text
trust_score
trust_flags
```

---

### Re-Ranker

File:

```text
reranker.py
```

Computes:

```text
fit_score
final_score
```

Combines:

* Semantic Similarity
* Retrieval Signals
* Ranking Signals
* Evaluation Signals
* Production Signals
* Startup Signals
* Behavioral Signals
* Trust Score

---

### Explanation Engine

File:

```text
explanation.py
```

Generates deterministic explanations using evidence collected during feature extraction.

---

## Validation & Observability

### Audit Candidate

```bash
python ranking/audit.py --candidate_id <candidate_id>
```

Displays:

* Feature Scores
* Trust Flags
* Trust Score
* Final Score
* Evidence
* Explanation

---

### Calibration

```bash
python ranking/calibration.py
```

Runs ranking calibration and scoring validation.

---

### Stress Testing

```bash
python ranking/stress_test.py
```

Validates ranking behavior against synthetic edge cases.

---

### Honeypot Benchmark

```bash
python ranking/honeypot_benchmark.py
```

Tests trust engine against synthetic honeypot profiles.

---

### Weight Sensitivity

```bash
python ranking/weight_sensitivity.py
```

Evaluates ranking stability when scoring weights are perturbed.

---

### Distribution Analysis

```bash
python ranking/distribution_analysis.py
```

Generates score distributions and percentile analysis.

---

### Integration Check

```bash
python ranking/integration_check.py
```

Validates retrieval output before ranking.

Checks:

* Required fields
* Null values
* Duplicate IDs
* Score distributions

---

### Top 100 Audit

```bash
python ranking/top100_audit.py
```

Audits the final Top 100 candidates before submission.

---

## Expected Retrieval Input

Required fields:

```text
candidate_id
candidate_document
semantic_similarity
retrieval_score
```

Recommended fields:

```text
skills
career_history
profile
education
redrob_signals
years_experience
```

---

## Output

Final submission format:

```text
candidate_id
rank
score
reasoning
```
