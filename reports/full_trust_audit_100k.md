# Full 100K Trust Engine Audit

- **Total records**: 100,000
- **Parse errors**: 0

## Field Reading Verification

| Field | Count | Expected |
|---|---|---|
| `top-level years_experience` (old bug) | 0 | 0 |
| `profile.years_of_experience` (correct) | 100,000 | 100,000 |
| `career.start_date` (real schema) | 300,171 | large |
| `career.start_year` (old field) | 0 | 0 |

## Trust Score Distribution

| Bucket | Count | % |
|---|---|---|
| 1.0 (clean) | 98,634 | 98.6% |
| 0.7-0.9 | 1,352 | 1.4% |
| 0.5-0.7 | 14 | 0.0% |

## Trust Flags Fired

| Flag | Count | % |
|---|---|---|
| `LangChain-only Profile without foundational IR skills.` | 917 | 0.9% |
| `Skill Inflation Detected: Many skills but <2 years exp.` | 407 | 0.4% |
| `Keyword Stuffing Detected` | 17 | 0.0% |
| `Experience Inconsistency: Stated 12.7 yrs vs career timeline` | 3 | 0.0% |
| `Experience Inconsistency: Stated 15.0 yrs vs career timeline` | 2 | 0.0% |
| `Experience Inconsistency: Stated 11.4 yrs vs career timeline` | 2 | 0.0% |
| `Experience Inconsistency: Stated 13.7 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 12.8 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 9.9 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 13.3 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 10.3 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 8.0 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 15.2 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 14.1 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 8.5 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 14.9 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 12.9 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 5.5 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 12.2 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 16.2 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 12.4 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 8.6 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 16.9 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 7.7 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 10.1 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 4.4 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 10.9 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 12.3 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 6.9 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 16.5 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 7.6 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 13.1 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 11.7 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 16.6 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 16.1 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 7.9 yrs vs career timeline ` | 1 | 0.0% |
| `Experience Inconsistency: Stated 15.6 yrs vs career timeline` | 1 | 0.0% |
| `Experience Inconsistency: Stated 14.7 yrs vs career timeline` | 1 | 0.0% |
