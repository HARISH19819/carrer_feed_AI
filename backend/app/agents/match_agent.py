from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.agents.base_agent import BaseAgent, AgentRunResult
from app.services.scoring_engine import scoring_engine
from app.database.mongo import get_database
from app.core.logging import logger

class PersonalizedMatchingAgent(BaseAgent):
    agent_name = "Match Agent"

    async def match_user_with_jobs(
        self, user_id: str, candidate_profile: Dict[str, Any], min_score: int = 40
    ) -> List[Dict[str, Any]]:
        db = get_database()
        if db is None:
            return []

        # Find active jobs
        cursor = db.jobs.find({"status": "active"}).limit(200)
        jobs = await cursor.to_list(length=200)
        
        matches = []
        now = datetime.now(timezone.utc)
        
        for job in jobs:
            match_res = scoring_engine.score_match(candidate_profile, job)
            if match_res["score"] >= min_score:
                job_id = str(job["_id"])
                match_doc = {
                    "user_id": user_id,
                    "job_id": job_id,
                    "score": match_res["score"],
                    "match_tier": match_res["match_tier"],
                    "strong_matches": match_res["strong_matches"],
                    "missing_skills": match_res["missing_skills"],
                    "why_matched": match_res["why_matched"],
                    "breakdown": match_res["breakdown"],
                    "created_at": now,
                    "updated_at": now
                }
                
                # Upsert into matches collection
                await db.matches.update_one(
                    {"user_id": user_id, "job_id": job_id},
                    {"$set": match_doc},
                    upsert=True
                )
                match_doc["job"] = job
                matches.append(match_doc)
                
        # Sort matches by score descending
        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches

    async def run(self, user_id: Optional[str] = None) -> AgentRunResult:
        result = AgentRunResult(self.agent_name)
        db = get_database()
        if db is None:
            result.error_summary = "Database not connected"
            result.finish("failed")
            return result

        try:
            matched_total = 0
            if user_id:
                profile = await db.candidate_profiles.find_one({"user_id": user_id})
                if profile:
                    res = await self.match_user_with_jobs(user_id, profile)
                    matched_total = len(res)
            else:
                # Match for all candidates
                cursor = db.candidate_profiles.find({})
                profiles = await cursor.to_list(length=100)
                for p in profiles:
                    uid = p.get("user_id")
                    if uid:
                        res = await self.match_user_with_jobs(uid, p)
                        matched_total += len(res)

            result.records_processed = matched_total
            result.details = {"matched_count": matched_total}
            result.finish("completed")
        except Exception as e:
            result.records_failed = 1
            result.error_summary = str(e)
            result.finish("failed")

        return result

match_agent = PersonalizedMatchingAgent()
