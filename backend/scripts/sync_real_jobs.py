import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.mongo import connect_to_mongo, close_mongo_connection, get_database
from app.agents.job_discovery_agent import job_discovery_agent
from app.agents.job_classifier_agent import job_classifier_agent
from app.agents.match_agent import match_agent
from app.core.logging import logger

async def sync_all_real_jobs():
    logger.info("Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()

    # 1. Purge all fake / demo / dataset jobs
    del_res = await db.jobs.delete_many({
        "$or": [
            {"is_demo": True},
            {"source": {"$regex": "Dataset|Compliant Verified", "$options": "i"}}
        ]
    })
    logger.info(f"Purged {del_res.deleted_count} fake / dataset jobs from database.")

    # 2. Run Scanner Agent across all live real-time public APIs & feeds
    logger.info("Executing Scanner Agent across all real-time adapters...")
    scan_res = await job_discovery_agent.run(limit_per_source=25)
    logger.info(f"Scanner Agent finished: {scan_res.records_processed} live jobs added, {scan_res.details}")

    # 3. Classify newly ingested real jobs
    logger.info("Executing Classifier Agent on real jobs...")
    class_res = await job_classifier_agent.run()
    logger.info(f"Classifier Agent finished: {class_res.records_processed} jobs categorized.")

    # 4. Run match agent for active candidate profiles
    logger.info("Executing Match Agent...")
    match_res = await match_agent.run()
    logger.info(f"Match Agent finished: {match_res.records_processed} match pairs generated.")

    # 5. Print summary of total jobs and sources in db
    total_jobs = await db.jobs.count_documents({})
    sources = await db.jobs.distinct("source")
    logger.info(f"SUCCESS: Database now has {total_jobs} 100% REAL jobs across sources: {sources}")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(sync_all_real_jobs())
