# Database Architecture & Collections

JobFusion AI uses MongoDB Atlas (or local MongoDB 7.0/8.0+ for development) via the asynchronous `motor` Python driver.

## Collections Overview

| Collection | Description | Primary Indexes |
|---|---|---|
| `users` | User accounts, hashed passwords, roles (`student`, `admin`) | `email` (unique), `role` |
| `candidate_profiles` | Extracted profile, skills, domains, education, preferences | `user_id` (unique) |
| `jobs` | Normalized and classified job opportunities from all adapters | `fingerprint` (unique), `source`, `domain`, `experience_level`, `location_type`, `status`, text search index |
| `job_sources` | Configured source adapters, status, last run timestamps | `adapter_key` (unique) |
| `matches` | Personalized recommendation scores and breakdowns | `user_id + job_id` (unique), `user_id + score` |
| `saved_jobs` | User bookmarked opportunities | `user_id + job_id` (unique), `created_at` |
| `applications` | Kanban application lifecycle tracking records | `user_id + job_id` (unique), `user_id + status` |
| `pipeline_runs` | Full pipeline execution logs and statistics | `start_time` (descending) |
| `agent_runs` | Individual agent execution duration and telemetry | `run_id`, `agent_name` |

## Deduplication Strategy
1. **Deterministic Fingerprint**: SHA-256 hash computed over normalized company name, standardized title, and cleaned location.
2. **URL Canonicalization**: Strips tracking parameters (`utm_*`, `ref`, etc.) to detect identical source links.
3. **Multi-Source Retention**: When a duplicate job is discovered from an alternate source, the original document is preserved, and the alternate source is appended to `alternate_sources` for complete source transparency.
