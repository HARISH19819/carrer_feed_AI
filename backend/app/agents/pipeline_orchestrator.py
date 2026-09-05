import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.agents.job_discovery_agent import job_discovery_agent
from app.agents.job_classifier_agent import job_classifier_agent
from app.agents.match_agent import match_agent
from app.database.mongo import get_database
from app.core.logging import logger

class PipelineOrchestrator:
    async def run_full_pipeline(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        db = get_database()

        pipeline_doc = {
            "run_id": run_id,
            "start_time": start_time,
            "status": "running",
            "discovered_count": 0,
            "duplicate_count": 0,
            "classified_count": 0,
            "matched_count": 0,
            "error_details": None,
            "agent_runs": []
        }

        if db is not None:
            await db.pipeline_runs.insert_one(pipeline_doc)

        logger.info(f"Starting Pipeline Run {run_id}...")

        try:
            # Step 1: Discover jobs
            discovery_res = await job_discovery_agent.run()
            disc_details = discovery_res.details or {}
            
            # Step 2: Classify pending jobs
            classifier_res = await job_classifier_agent.run()
            class_details = classifier_res.details or {}
            
            # Step 3: Personalized matching
            matcher_res = await match_agent.run(user_id=user_id)
            match_details = matcher_res.details or {}

            end_time = datetime.now(timezone.utc)
            duration = round((end_time - start_time).total_seconds(), 2)

            agent_runs_summary = [
                discovery_res.to_dict(),
                classifier_res.to_dict(),
                matcher_res.to_dict()
            ]

            summary = {
                "run_id": run_id,
                "status": "completed",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "discovered_count": disc_details.get("discovered_count", 0),
                "normalized_count": disc_details.get("valid_count", 0),
                "duplicate_count": disc_details.get("duplicate_count", 0),
                "classified_count": class_details.get("classified_count", 0),
                "matched_count": match_details.get("matched_count", 0),
                "error_details": None,
                "agent_runs": agent_runs_summary
            }

            if db is not None:
                await db.pipeline_runs.update_one(
                    {"run_id": run_id},
                    {"$set": summary}
                )
                for ar in agent_runs_summary:
                    ar_copy = ar.copy()
                    ar_copy["run_id"] = run_id
                    await db.agent_runs.insert_one(ar_copy)

            logger.info(f"Pipeline Run {run_id} completed successfully in {duration}s.")
            return summary

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = round((end_time - start_time).total_seconds(), 2)
            err_msg = str(e)
            logger.error(f"Pipeline Run {run_id} failed: {err_msg}")

            fail_summary = {
                "run_id": run_id,
                "status": "failed",
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration,
                "error_details": err_msg
            }
            if db is not None:
                await db.pipeline_runs.update_one(
                    {"run_id": run_id},
                    {"$set": fail_summary}
                )
            return fail_summary

pipeline_orchestrator = PipelineOrchestrator()
