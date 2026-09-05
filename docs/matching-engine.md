# Deterministic Matching Engine & Recommendation Algorithm

## Formula & Scoring Weights

JobFusion AI uses a strictly deterministic scoring engine paired with semantic vector similarity to produce transparent, explainable compatibility scores.

The structured score is computed across 7 explicit dimensions:

$$\text{StructuredScore} = 0.30 \cdot S_{\text{skill}} + 0.20 \cdot S_{\text{role}} + 0.15 \cdot S_{\text{domain}} + 0.15 \cdot S_{\text{experience}} + 0.10 \cdot S_{\text{education}} + 0.05 \cdot S_{\text{location}} + 0.05 \cdot S_{\text{preference}}$$

### Dimensional Components:
1. **Skill Match (30%)**: Jaccard and overlap ratio between candidate skills and job required/preferred skills after alias normalization.
2. **Role Match (20%)**: Keyword and token alignment between inferred/preferred candidate roles and the job title.
3. **Domain Match (15%)**: Compatibility with primary (1.0) and secondary (0.8) domain taxonomy classifications.
4. **Experience Match (15%)**: Alignment between candidate years/level and the minimum/maximum years required.
5. **Education Match (10%)**: Degree and field compatibility (e.g. B.Tech, M.Tech, MCA, BCA).
6. **Location Match (5%)**: Remote work alignment or preferred physical locations.
7. **Preference Match (5%)**: Match with desired employment types (internship vs full-time).

### Semantic Similarity Integration:
$$\text{FinalScore} = \text{round}\Big(\big(0.70 \cdot \text{StructuredScore} + 0.30 \cdot \text{SemanticSimilarity}\big) \times 100\Big)$$

Score is normalized and bounded between **10** and **99**.

## Match Tiers:
- **90–100%**: Excellent Match
- **80–89%**: Strong Match
- **70–79%**: Good Match
- **60–69%**: Moderate Match
- **< 60%**: Low Match

## Hard Filters vs Soft Preferences:
- **Hard Filters**: Inactive/expired job statuses are filtered out.
- **Soft Preferences**: Location, preferred domain, and job types apply scoring boosts or soft penalties rather than blindly excluding relevant career adjacencies.

## Deterministic Verification Test Case:
- **Candidate Profile**:
  `Python`, `Pandas`, `Scikit-learn`, `TensorFlow`, `Machine Learning`, `MongoDB`
- **Job Posting**:
  `Python`, `TensorFlow`, `Machine Learning`, `Docker`, `AWS`
- **Output Verified**:
  - **Strong Matches**: `Python`, `TensorFlow`, `Machine Learning`
  - **Missing Skills**: `Docker`, `AWS`
  - **Match Tier**: Strong Match (> 75%)
