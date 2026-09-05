from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from app.database.mongo import get_database
from app.api.deps import get_current_user
from app.agents.pipeline_orchestrator import pipeline_orchestrator
from app.agents.job_discovery_agent import job_discovery_agent
from app.agents.job_classifier_agent import job_classifier_agent
from app.agents.match_agent import match_agent

router = APIRouter(prefix="/pipeline", tags=["Pipeline & Agents"])

@router.get("/status")
async def get_pipeline_status(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]

    # Calculate real-time counts for the 4 agent cards
    total_jobs = await db.jobs.count_documents({})
    pending_classify = await db.jobs.count_documents(
        {"$or": [{"classification_method": "deterministic"}, {"confidence": {"$exists": False}}]}
    )
    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    user_matches_count = await db.matches.count_documents({"user_id": user_id})

    # Recent runs
    cursor = db.pipeline_runs.find({}).sort("start_time", -1).limit(5)
    recent_runs = await cursor.to_list(length=5)
    for r in recent_runs:
        r["id"] = str(r["_id"])
        del r["_id"]

    agent_cards = [
        {
            "agent_id": "scanner",
            "name": "Scanner Agent",
            "description": "Discovers fresh opportunities from configured sources.",
            "status": "ready",
            "metric_label": "Jobs indexed",
            "metric_value": str(total_jobs),
            "action_label": "Scan Now"
        },
        {
            "agent_id": "classifier",
            "name": "Classifier Agent",
            "description": "Structures opportunities by domain, skills, and experience.",
            "status": "ready",
            "metric_label": "Pending classification",
            "metric_value": str(pending_classify),
            "action_label": "Classify Pending"
        },
        {
            "agent_id": "profile",
            "name": "Profile Agent",
            "description": "Builds and maintains your candidate profile.",
            "status": "ready" if profile else "action_required",
            "metric_label": "Profile strength",
            "metric_value": f"{profile.get('completeness_score', 0)}%" if profile else "No Resume",
            "action_label": "View Profile"
        },
        {
            "agent_id": "matcher",
            "name": "Match Agent",
            "description": "Ranks opportunities according to your profile.",
            "status": "ready",
            "metric_label": "Matches ranked",
            "metric_value": f"{user_matches_count} matches",
            "action_label": "Rank For Me"
        }
    ]

    return {
        "pipeline_state": "idle",
        "agent_cards": agent_cards,
        "recent_runs": recent_runs
    }

@router.post("/run")
async def trigger_pipeline_run(
    agent: str = "all",  # "all", "scanner", "classifier", "matcher"
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    if agent == "all":
        summary = await pipeline_orchestrator.run_full_pipeline(user_id=user_id)
        return {"message": "Full multi-agent pipeline completed.", "summary": summary}
    elif agent == "scanner":
        res = await job_discovery_agent.run()
        return {"message": "Scanner agent run completed.", "result": res.to_dict()}
    elif agent == "classifier":
        res = await job_classifier_agent.run()
        return {"message": "Classifier agent run completed.", "result": res.to_dict()}
    elif agent == "matcher":
        res = await match_agent.run(user_id=user_id)
        return {"message": "Match agent run completed.", "result": res.to_dict()}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown agent '{agent}'.")
