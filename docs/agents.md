# Autonomous Multi-Agent System

JobFusion AI is driven by four primary specialized intelligent agents coordinated by a centralized Pipeline Orchestrator.

## Agent 1: Resume / Profile Agent (`ResumeProfileAgent`)
- **Input**: Resume files in PDF, DOCX, or TXT format.
- **Parsing**: PyMuPDF (`pymupdf`) for high-fidelity PDF text extraction; `python-docx` for Word documents; UTF-8/Latin-1 fallback for plain text.
- **Skill Extraction**: Word-boundary regex matching across thousands of canonical technical skills and aliases.
- **Normalization**: Maps raw text (e.g., `sklearn`, `scikit learn`, `js`, `ts`, `tf`) to canonical representations (`scikit-learn`, `JavaScript`, `TypeScript`, `TensorFlow`).
- **Domain & Role Inference**: Scores candidate context against the 22-domain taxonomy to deduce primary career fields and suitable titles.
- **Completeness**: Calculates deterministic profile strength percentage (0-100%).

## Agent 2: Job Discovery Agent (`JobDiscoveryAgent`)
- **Responsibility**: Ingests fresh opportunities from configured active source adapters.
- **Source Adapter Architecture**: Queries public permitted APIs (Remotive, Jobicy) and curated benchmark datasets.
- **Deduplication Integration**: Runs deterministic SHA-256 fingerprinting and URL canonicalization to eliminate cross-source duplicates.
- **Freshness & Telemetry**: Records discovered count, valid count, duplicate count, failed count, duration, and errors.

## Agent 3: Job Classification Agent (`JobClassificationAgent`)
- **Responsibility**: Analyzes jobs and assigns standardized domain and requirement metadata.
- **Domain Taxonomy**: 22 technical and business domains (AI, ML, Data Science, Frontend, Backend, DevOps, Cybersecurity, etc.).
- **Experience Level**: Normalizes requirements into `fresher`, `entry_level`, `junior`, `mid_level`, and `senior`.
- **Hybrid Mechanism**: Executes fast keyword & rule-based scoring first. If confidence is below 60%, delegates ambiguous descriptions to the pluggable LLM provider with prompt injection defense.

## Agent 4: Personalized Matching Agent (`PersonalizedMatchingAgent`)
- **Responsibility**: Evaluates candidate compatibility with active jobs.
- **Inputs**: Structured candidate profile + normalized job records.
- **Scoring Engine**: Evaluates 7 dimensions (Skills, Role, Domain, Experience, Education, Location, Preferences) + TF-IDF semantic vector similarity.
- **Transparent Explainability**: Identifies strong matching skills, flags actionable missing skills, and synthesizes a concise explanation of why the role fits.

## Pipeline Orchestrator (`PipelineOrchestrator`)
Coordinates end-to-end execution:
`Discovery -> Normalize -> Deduplicate -> Classify -> Embed -> Match -> Rank`
Generates audit logs in `pipeline_runs` and `agent_runs` for system observability.
