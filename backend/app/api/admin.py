from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone, timedelta
from app.database.mongo import get_database
from app.api.deps import get_current_admin
from app.schemas.admin import AdminStatsResponse, JobSourceItem, DomainCount, SourceCount, UpdateJobSourcePayload
from app.sources import AVAILABLE_ADAPTERS
from app.agents.job_discovery_agent import job_discovery_agent
from app.utils.skills import DOMAIN_TAXONOMY, CANONICAL_SKILLS

router = APIRouter(prefix="/admin", tags=["Admin Operations"])

DEFAULT_SOURCES = [
    {
        "id": "src_remotive",
        "name": "Remotive Public API",
        "adapter_key": "remotive_api",
        "source_type": "api",
        "base_url": "https://remotive.com/api/remote-jobs",
        "enabled": True,
        "description": "Compliant public REST API for developer, data, and technical remote roles."
    },
    {
        "id": "src_jobicy",
        "name": "Jobicy Remote API",
        "adapter_key": "jobicy_api",
        "source_type": "api",
        "base_url": "https://jobicy.com/api/v2/remote-jobs",
        "enabled": True,
        "description": "Compliant public feed for global remote jobs."
    },
    {
        "id": "src_arbeitnow",
        "name": "Arbeitnow Tech API",
        "adapter_key": "arbeitnow_api",
        "source_type": "api",
        "base_url": "https://www.arbeitnow.com/api/job-board-api",
        "enabled": True,
        "description": "Live European & global tech job board API covering engineering and AI."
    },
    {
        "id": "src_themuse",
        "name": "The Muse Jobs API",
        "adapter_key": "themuse_api",
        "source_type": "api",
        "base_url": "https://www.themuse.com/api/public/jobs",
        "enabled": True,
        "description": "Real-time opportunities at premier technology and enterprise organizations."
    },
    {
        "id": "src_remoteok",
        "name": "RemoteOK Live API",
        "adapter_key": "remoteok_api",
        "source_type": "api",
        "base_url": "https://remoteok.com/api",
        "enabled": True,
        "description": "Real-time global remote opportunities for software developers and designers."
    },
    {
        "id": "src_wwr",
        "name": "WeWorkRemotely Live RSS",
        "adapter_key": "wwr_rss",
        "source_type": "feed",
        "base_url": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "enabled": True,
        "description": "Live RSS feed for programming, engineering, and devops positions."
    },
    {
        "id": "src_internshala",
        "name": "Internshala Live Feed",
        "adapter_key": "internshala_feed",
        "source_type": "scraper",
        "base_url": "https://internshala.com/fresher-jobs",
        "enabled": True,
        "description": "Real-time fresher tech and entry-level developer positions."
    },
    {
        "id": "src_linkedin",
        "name": "LinkedIn Jobs Feed",
        "adapter_key": "linkedin_feed",
        "source_type": "feed",
        "base_url": "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings",
        "enabled": True,
        "description": "Real-time verified professional job discovery feed from LinkedIn."
    }
]

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    
    total_users = await db.users.count_documents({})
    total_candidates = await db.candidate_profiles.count_documents({})
    total_jobs = await db.jobs.count_documents({})
    active_jobs = await db.jobs.count_documents({"status": "active"})

    # Jobs created in last 24 hours
    since_yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    jobs_today = await db.jobs.count_documents({"created_at": {"$gte": since_yesterday}})

    # Aggregation for domains
    domain_agg = await db.jobs.aggregate([
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 8}
    ]).to_list(length=10)
    jobs_by_domain = [DomainCount(domain=d.get("_id") or "Unclassified", count=d.get("count", 0)) for d in domain_agg]

    # Aggregation for sources
    source_agg = await db.jobs.aggregate([
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(length=10)
    jobs_by_source = [SourceCount(source=s.get("_id") or "Direct", count=s.get("count", 0)) for s in source_agg]

    # Pipeline runs count
    pipe_runs = await db.pipeline_runs.count_documents({})
    failed_runs = await db.pipeline_runs.count_documents({"status": "failed"})

    # Duplicate counts from pipeline runs
    dup_agg = await db.pipeline_runs.aggregate([
        {"$group": {"_id": None, "total_dup": {"$sum": "$duplicate_count"}}}
    ]).to_list(length=1)
    total_dup = dup_agg[0]["total_dup"] if dup_agg else 0
    total_found = total_jobs + total_dup
    dup_rate = round((total_dup / total_found * 100), 1) if total_found > 0 else 0.0

    # Average match score
    match_agg = await db.matches.aggregate([
        {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}}
    ]).to_list(length=1)
    avg_score = round(match_agg[0]["avg_score"], 1) if match_agg and match_agg[0].get("avg_score") else 0.0

    return AdminStatsResponse(
        total_users=total_users,
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        jobs_today=jobs_today,
        jobs_by_domain=jobs_by_domain,
        jobs_by_source=jobs_by_source,
        pipeline_runs_count=pipe_runs,
        failed_runs_count=failed_runs,
        duplicate_count_total=total_dup,
        duplicate_rate_percent=dup_rate,
        average_match_score=avg_score
    )

@router.get("/sources", response_model=list[JobSourceItem])
async def list_sources(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    sources_col = await db.job_sources.find({}).to_list(length=20)
    
    if not sources_col:
        # Seed default sources in MongoDB
        for s in DEFAULT_SOURCES:
            s_doc = s.copy()
            s_doc["last_run_at"] = None
            s_doc["last_status"] = "idle"
            s_doc["jobs_fetched_total"] = 0
            await db.job_sources.update_one({"adapter_key": s["adapter_key"]}, {"$set": s_doc}, upsert=True)
        sources_col = await db.job_sources.find({}).to_list(length=20)

    results = []
    for sc in sources_col:
        results.append(JobSourceItem(
            id=str(sc.get("_id", sc.get("id"))),
            name=sc.get("name"),
            adapter_key=sc.get("adapter_key"),
            source_type=sc.get("source_type"),
            base_url=sc.get("base_url"),
            enabled=sc.get("enabled", True),
            last_run_at=sc.get("last_run_at"),
            last_status=sc.get("last_status", "idle"),
            jobs_fetched_total=sc.get("jobs_fetched_total", 0),
            description=sc.get("description", "")
        ))
    return results

@router.patch("/sources/{adapter_key}")
async def update_source(
    adapter_key: str,
    payload: UpdateJobSourcePayload,
    current_admin: dict = Depends(get_current_admin)
):
    db = get_database()
    update_data = {}
    if payload.enabled is not None:
        update_data["enabled"] = payload.enabled

    res = await db.job_sources.update_one(
        {"adapter_key": adapter_key},
        {"$set": update_data}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"message": f"Source {adapter_key} updated."}

@router.post("/sources/{adapter_key}/run")
async def trigger_source_ingestion(
    adapter_key: str,
    current_admin: dict = Depends(get_current_admin)
):
    if adapter_key not in AVAILABLE_ADAPTERS:
        raise HTTPException(status_code=404, detail="Source adapter not registered.")

    db = get_database()
    run_res = await job_discovery_agent.run(source_keys=[adapter_key], limit_per_source=25)
    
    # Update source metrics in MongoDB
    valid_count = (run_res.details or {}).get("valid_count", 0)
    await db.job_sources.update_one(
        {"adapter_key": adapter_key},
        {
            "$set": {
                "last_run_at": datetime.now(timezone.utc),
                "last_status": run_res.status
            },
            "$inc": {"jobs_fetched_total": valid_count}
        }
    )

    return {"message": f"Ingestion triggered for {adapter_key}.", "result": run_res.to_dict()}

@router.get("/taxonomy")
async def get_taxonomy_and_skills(current_admin: dict = Depends(get_current_admin)):
    return {
        "domains": DOMAIN_TAXONOMY,
        "skill_categories": CANONICAL_SKILLS
    }
