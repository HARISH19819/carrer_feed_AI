import pymongo
from app.database.mongo import get_database
from app.core.logging import logger

async def create_indexes():
    db = get_database()
    if db is None:
        logger.warning("Database not connected; skipping index creation.")
        return

    try:
        # Users
        await db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        await db.users.create_index([("role", pymongo.ASCENDING)])

        # Candidate Profiles
        await db.candidate_profiles.create_index([("user_id", pymongo.ASCENDING)], unique=True)

        # Jobs
        await db.jobs.create_index([("fingerprint", pymongo.ASCENDING)], unique=True, sparse=True)
        await db.jobs.create_index([("source", pymongo.ASCENDING)])
        await db.jobs.create_index([("source_url", pymongo.ASCENDING)])
        await db.jobs.create_index([("posted_at", pymongo.DESCENDING)])
        await db.jobs.create_index([("domain", pymongo.ASCENDING)])
        await db.jobs.create_index([("experience_level", pymongo.ASCENDING)])
        await db.jobs.create_index([("location_type", pymongo.ASCENDING)])
        await db.jobs.create_index([("employment_type", pymongo.ASCENDING)])
        await db.jobs.create_index([("status", pymongo.ASCENDING)])
        # Text search index for title, company, description, skills
        await db.jobs.create_index([
            ("title", pymongo.TEXT),
            ("company", pymongo.TEXT),
            ("description", pymongo.TEXT),
            ("skills", pymongo.TEXT)
        ], name="jobs_text_search_idx")

        # Matches
        await db.matches.create_index([("user_id", pymongo.ASCENDING), ("job_id", pymongo.ASCENDING)], unique=True)
        await db.matches.create_index([("user_id", pymongo.ASCENDING), ("score", pymongo.DESCENDING)])

        # Saved Jobs
        await db.saved_jobs.create_index([("user_id", pymongo.ASCENDING), ("job_id", pymongo.ASCENDING)], unique=True)
        await db.saved_jobs.create_index([("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])

        # Applications
        await db.applications.create_index([("user_id", pymongo.ASCENDING), ("job_id", pymongo.ASCENDING)], unique=True)
        await db.applications.create_index([("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)])

        # Pipeline runs & Agent runs
        await db.pipeline_runs.create_index([("start_time", pymongo.DESCENDING)])
        await db.agent_runs.create_index([("run_id", pymongo.ASCENDING)])
        await db.agent_runs.create_index([("agent_name", pymongo.ASCENDING)])

        logger.info("Database indexes successfully ensured.")
    except Exception as e:
        logger.error(f"Error ensuring database indexes: {e}")
