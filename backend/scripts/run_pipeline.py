import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.mongo import connect_to_mongo, close_mongo_connection
from app.database.indexes import create_indexes
from app.agents.pipeline_orchestrator import pipeline_orchestrator
from app.core.logging import logger

async def main():
    logger.info("Starting background scheduled pipeline runner...")
    await connect_to_mongo()
    await create_indexes()

    summary = await pipeline_orchestrator.run_full_pipeline()
    logger.info(f"Pipeline finished with status: {summary.get('status')}")
    logger.info(f"Discovered: {summary.get('discovered_count')}, Valid: {summary.get('normalized_count')}, Duplicates: {summary.get('duplicate_count')}, Classified: {summary.get('classified_count')}, Matches: {summary.get('matched_count')}")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
