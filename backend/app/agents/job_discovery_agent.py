from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.agents.base_agent import BaseAgent, AgentRunResult
from app.sources import AVAILABLE_ADAPTERS
from app.services.normalization_service import job_normalizer
from app.services.deduplication_service import deduplication_service
from app.database.mongo import get_database
from app.core.logging import logger

class JobDiscoveryAgent(BaseAgent):
    agent_name = "Scanner Agent"

    async def run(
        self,
        source_keys: Optional[List[str]] = None,
        limit_per_source: int = 25
    ) -> AgentRunResult:
        result = AgentRunResult(self.agent_name)
        db = get_database()
        
        target_keys = source_keys or list(AVAILABLE_ADAPTERS.keys())
        discovered_total = 0
        valid_total = 0
        duplicate_total = 0
        failed_total = 0
        
        # Load existing jobs for deduplication check
        existing_jobs = []
        if db is not None:
            cursor = db.jobs.find({}, {"_id": 1, "fingerprint": 1, "application_url": 1, "title": 1, "company": 1})
            existing_jobs = await cursor.to_list(length=2000)
            
        for key in target_keys:
            adapter = AVAILABLE_ADAPTERS.get(key)
            if not adapter:
                logger.warning(f"Unknown source adapter: {key}")
                continue
                
            try:
                raw_jobs = await adapter.fetch_jobs(limit=limit_per_source)
                discovered_total += len(raw_jobs)
                
                for rj in raw_jobs:
                    try:
                        normalized = job_normalizer.normalize_job_dict(rj)
                        
                        # Generate fingerprint
                        fp = deduplication_service.generate_deterministic_fingerprint(
                            normalized["company"], normalized["title"], normalized["location"]
                        )
                        normalized["fingerprint"] = fp
                        
                        # Check duplicate
                        is_dup, matched_id = deduplication_service.check_is_duplicate(
                            normalized, existing_jobs
                        )
                        
                        if is_dup:
                            duplicate_total += 1
                            # If existing job found in db, optionally append source
                            if db is not None and matched_id:
                                await db.jobs.update_one(
                                    {"_id": matched_id},
                                    {"$addToSet": {"alternate_sources": {
                                        "source": normalized["source"],
                                        "source_url": normalized["source_url"],
                                        "application_url": normalized["application_url"]
                                    }}}
                                )
                            continue
                            
                        # Add timestamps
                        now = datetime.now(timezone.utc)
                        normalized["created_at"] = now
                        normalized["updated_at"] = now
                        if not normalized.get("posted_at"):
                            normalized["posted_at"] = now
                        normalized["last_seen_at"] = now
                        
                        if db is not None:
                            insert_res = await db.jobs.insert_one(normalized)
                            normalized["_id"] = insert_res.inserted_id
                            existing_jobs.append(normalized)
                            
                        valid_total += 1
                    except Exception as item_err:
                        failed_total += 1
                        logger.warning(f"Error processing discovered job: {item_err}")
                        
            except Exception as source_err:
                failed_total += 1
                logger.error(f"Error fetching from adapter {key}: {source_err}")

        result.records_processed = valid_total
        result.records_failed = failed_total
        result.details = {
            "discovered_count": discovered_total,
            "valid_count": valid_total,
            "duplicate_count": duplicate_total,
            "failed_count": failed_total
        }
        result.finish("completed" if failed_total == 0 or valid_total > 0 else "failed")
        return result

job_discovery_agent = JobDiscoveryAgent()
