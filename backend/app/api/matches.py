from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, List
from bson import ObjectId
from app.database.mongo import get_database
from app.api.deps import get_current_user
from app.schemas.match import MatchResponse, MatchListResponse, ScoreBreakdown
from app.api.jobs import serialize_job
from app.agents.match_agent import match_agent

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.get("", response_model=MatchListResponse)
async def get_my_matches(
    tier: Optional[str] = Query(None, description="all, excellent, strong, good"),
    min_score: int = Query(40, ge=0, le=100),
    sort_by: str = Query("score_desc", description="score_desc, newest"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user_id = current_user["id"]

    # Check if candidate has matches; if none exist, run match agent on the fly
    existing_count = await db.matches.count_documents({"user_id": user_id})
    if existing_count == 0:
        profile = await db.candidate_profiles.find_one({"user_id": user_id})
        if profile:
            await match_agent.match_user_with_jobs(user_id, profile, min_score=30)

    # Build query
    query: dict = {"user_id": user_id, "score": {"$gte": min_score}}
    
    if tier and tier.lower() != "all":
        tier_map = {
            "excellent": "Excellent Match",
            "strong": "Strong Match",
            "good": "Good Match",
            "moderate": "Moderate Match"
        }
        target_tier = tier_map.get(tier.lower(), tier)
        query["match_tier"] = target_tier

    total = await db.matches.count_documents(query)
    skip = (page - 1) * page_size

    sort_criteria = [("score", -1)]
    if sort_by == "newest":
        sort_criteria = [("created_at", -1)]

    cursor = db.matches.find(query).sort(sort_criteria).skip(skip).limit(page_size)
    raw_matches = await cursor.to_list(length=page_size)

    # Fetch saved jobs and applications to annotate status
    saved_cursor = db.saved_jobs.find({"user_id": user_id})
    saved_list = await saved_cursor.to_list(length=500)
    saved_job_ids = {str(s.get("job_id")) for s in saved_list}

    app_cursor = db.applications.find({"user_id": user_id})
    app_list = await app_cursor.to_list(length=500)
    app_status_map = {str(a.get("job_id")): a.get("status", "Applied") for a in app_list}

    items = []
    for m in raw_matches:
        job_id = m.get("job_id")
        # Fetch job document
        try:
            job_doc = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            job_doc = await db.jobs.find_one({"_id": job_id})

        if not job_doc:
            continue

        bd = m.get("breakdown", {})
        breakdown_obj = ScoreBreakdown(
            skill_score=bd.get("skill_score", 0.0),
            role_score=bd.get("role_score", 0.0),
            domain_score=bd.get("domain_score", 0.0),
            experience_score=bd.get("experience_score", 0.0),
            education_score=bd.get("education_score", 0.0),
            location_score=bd.get("location_score", 0.0),
            preference_score=bd.get("preference_score", 0.0),
            semantic_similarity=bd.get("semantic_similarity", 0.0)
        )

        items.append(MatchResponse(
            id=str(m["_id"]),
            user_id=user_id,
            job_id=job_id,
            job=serialize_job(job_doc),
            score=m.get("score", 50),
            match_tier=m.get("match_tier", "Good Match"),
            strong_matches=m.get("strong_matches", []),
            missing_skills=m.get("missing_skills", []),
            why_matched=m.get("why_matched", "Matches your profile"),
            breakdown=breakdown_obj,
            is_saved=job_id in saved_job_ids,
            application_status=app_status_map.get(job_id),
            created_at=m.get("created_at"),
            updated_at=m.get("updated_at")
        ))

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return MatchListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{job_id}", response_model=MatchResponse)
async def get_single_match(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user_id = current_user["id"]

    match_doc = await db.matches.find_one({"user_id": user_id, "job_id": job_id})
    
    # If not computed yet, compute now
    if not match_doc:
        profile = await db.candidate_profiles.find_one({"user_id": user_id})
        try:
            job_doc = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            job_doc = await db.jobs.find_one({"_id": job_id})
            
        if not job_doc or not profile:
            raise HTTPException(status_code=404, detail="Job or profile not found.")
            
        from app.services.scoring_engine import scoring_engine
        match_res = scoring_engine.score_match(profile, job_doc)
        now = datetime.now(timezone.utc)
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
        res = await db.matches.insert_one(match_doc)
        match_doc["_id"] = res.inserted_id
    else:
        try:
            job_doc = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            job_doc = await db.jobs.find_one({"_id": job_id})

    saved = await db.saved_jobs.find_one({"user_id": user_id, "job_id": job_id})
    app = await db.applications.find_one({"user_id": user_id, "job_id": job_id})

    bd = match_doc.get("breakdown", {})
    breakdown_obj = ScoreBreakdown(
        skill_score=bd.get("skill_score", 0.0),
        role_score=bd.get("role_score", 0.0),
        domain_score=bd.get("domain_score", 0.0),
        experience_score=bd.get("experience_score", 0.0),
        education_score=bd.get("education_score", 0.0),
        location_score=bd.get("location_score", 0.0),
        preference_score=bd.get("preference_score", 0.0),
        semantic_similarity=bd.get("semantic_similarity", 0.0)
    )

    return MatchResponse(
        id=str(match_doc["_id"]),
        user_id=user_id,
        job_id=job_id,
        job=serialize_job(job_doc),
        score=match_doc.get("score", 50),
        match_tier=match_doc.get("match_tier", "Good Match"),
        strong_matches=match_doc.get("strong_matches", []),
        missing_skills=match_doc.get("missing_skills", []),
        why_matched=match_doc.get("why_matched", ""),
        breakdown=breakdown_obj,
        is_saved=saved is not None,
        application_status=app.get("status") if app else None,
        created_at=match_doc.get("created_at"),
        updated_at=match_doc.get("updated_at")
    )
