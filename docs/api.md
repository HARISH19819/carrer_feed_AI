# API Specifications & Contracts

All backend endpoints are prefixed with `/api` and return structured JSON responses.

## Authentication (`/api/auth`)
- `POST /api/auth/register` — Register a new student user.
  - Body: `{ name, email, password }`
  - Response: `{ access_token, token_type, user }`
- `POST /api/auth/login` — Sign in and receive JWT token.
  - Body: `{ email, password }`
  - Response: `{ access_token, token_type, user }`
- `GET /api/auth/me` — Retrieve current authenticated user profile.
- `POST /api/auth/logout` — Invalidate user session.

## Candidate Profile (`/api/profile`)
- `GET /api/profile` — Fetch candidate profile and completeness score.
- `POST /api/profile/resume` — Multipart file upload (PDF/DOCX/TXT) parsed by Agent 1.
- `PUT /api/profile` — Update candidate skills, domains, or preferences.
- `POST /api/profile/reanalyze` — Re-infer domains and regenerate recommendations.

## Jobs Explorer (`/api/jobs`)
- `GET /api/jobs` — Paginated job search and filtering.
  - Query params: `q`, `domain`, `employment_type`, `experience_level`, `location_type`, `page`, `page_size`, `sort_by`
- `GET /api/jobs/{job_id}` — Full details for a single job opportunity.

## Personalized Matches (`/api/matches`)
- `GET /api/matches` — Ranked recommendation feed for logged-in user.
  - Query params: `tier` (`all`, `excellent`, `strong`, `good`), `min_score`, `sort_by`, `page`, `page_size`
- `GET /api/matches/{job_id}` — Specific 7-dimension score breakdown and explainability report.

## Saved Jobs (`/api/saved`)
- `GET /api/saved` — List all bookmarked jobs for candidate.
- `POST /api/saved/{job_id}` — Save an opportunity.
- `DELETE /api/saved/{job_id}` — Remove an opportunity from saved list.

## Applications Tracker (`/api/applications`)
- `GET /api/applications` — List user application records across Kanban stages.
- `POST /api/applications/{job_id}` — Track an application event when clicking "Apply on Source".
- `PATCH /api/applications/{application_id}` — Update workflow status (`Saved`, `Viewed`, `Applied`, `Interview`, `Selected`, `Rejected`).
- `GET /api/applications/stats/summary` — Aggregate application metrics and response rate.

## Skill Gaps (`/api/skill-gaps`)
- `GET /api/skill-gaps` — Aggregates top missing requirements across matching opportunities.

## Pipeline & Multi-Agent (`/api/pipeline`)
- `GET /api/pipeline/status` — Live status of the 4 agent cards and recent runs.
- `POST /api/pipeline/run?agent={all|scanner|classifier|matcher}` — Trigger agent execution.

## Admin Console (`/api/admin`)
- `GET /api/admin/stats` — Platform analytics, duplicate rate, active jobs, domain counts.
- `GET /api/admin/sources` — List all registered source adapters.
- `PATCH /api/admin/sources/{adapter_key}` — Enable or disable a source adapter.
- `POST /api/admin/sources/{adapter_key}/run` — Trigger manual ingestion for an adapter.
