from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, List
from bson import ObjectId
from app.database.mongo import get_database
from app.schemas.job import JobResponse, JobListResponse
from app.utils.dates import get_relative_time
from app.api.deps import security_scheme, decode_access_token

router = APIRouter(prefix="/jobs", tags=["Jobs"])

def serialize_job(job: dict) -> JobResponse:
    job_id = str(job["_id"])
    return JobResponse(
        id=job_id,
        title=job.get("title", ""),
        company=job.get("company", ""),
        location=job.get("location", "Remote"),
        location_type=job.get("location_type", "remote"),
        employment_type=job.get("employment_type", "full_time"),
        experience_level=job.get("experience_level", "fresher"),
        experience_required=job.get("experience_required", "0-1 years"),
        min_experience_years=float(job.get("min_experience_years", 0.0)),
        max_experience_years=float(job.get("max_experience_years", 1.0)),
        salary=job.get("salary", "Not specified"),
        description=job.get("description", ""),
        skills=job.get("skills", []),
        required_skills=job.get("required_skills", []),
        preferred_skills=job.get("preferred_skills", []),
        domain=job.get("domain", "Software Development"),
        secondary_domains=job.get("secondary_domains", []),
        classification_method=job.get("classification_method", "deterministic"),
        source=job.get("source", "Direct"),
        source_url=job.get("source_url", ""),
        application_url=job.get("application_url", ""),
        posted_at=job.get("posted_at"),
        last_seen_at=job.get("last_seen_at"),
        status=job.get("status", "active"),
        fingerprint=job.get("fingerprint"),
        relative_posted_time=get_relative_time(job.get("posted_at")),
        created_at=job.get("created_at"),
        updated_at=job.get("updated_at")
    )

@router.get("", response_model=JobListResponse)
async def list_jobs(
    q: Optional[str] = Query(None, description="Search query across title, company, skills"),
    domain: Optional[str] = Query(None, description="Domain filter"),
    employment_type: Optional[str] = Query(None, description="full_time, internship, part_time, contract"),
    experience_level: Optional[str] = Query(None, description="fresher, entry_level, junior, mid_level, senior"),
    location_type: Optional[str] = Query(None, description="remote, hybrid, onsite"),
    sort_by: str = Query("newest", description="newest, title"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50)
):
    db = get_database()
    filter_query: dict = {"status": "active"}

    if domain and domain.lower() != "all":
        filter_query["domain"] = domain
    if employment_type and employment_type.lower() != "all":
        filter_query["employment_type"] = employment_type
    if experience_level and experience_level.lower() != "all":
        filter_query["experience_level"] = experience_level
    if location_type and location_type.lower() != "all":
        filter_query["location_type"] = location_type

    if q and q.strip():
        search_terms = q.strip()
        filter_query["$or"] = [
            {"title": {"$regex": search_terms, "$options": "i"}},
            {"company": {"$regex": search_terms, "$options": "i"}},
            {"skills": {"$regex": search_terms, "$options": "i"}},
            {"domain": {"$regex": search_terms, "$options": "i"}}
        ]

    items = []
    total = 0
    total_pages = 1
    
    try:
        if db is not None:
            total = await db.jobs.count_documents(filter_query)
            skip = (page - 1) * page_size

            sort_order = [("posted_at", -1)]
            if sort_by == "title":
                sort_order = [("title", 1)]

            cursor = db.jobs.find(filter_query).sort(sort_order).skip(skip).limit(page_size)
            raw_jobs = await cursor.to_list(length=page_size)
            items = [serialize_job(j) for j in raw_jobs]
            total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    except Exception as e:
        from app.core.logging import logger
        logger.warning(f"Database query error in list_jobs: {e}")
        # Graceful fallback: return empty list or freshly fetched jobs without crashing
        items = []
        total = 0
        total_pages = 1

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_by_id(job_id: str):
    db = get_database()
    try:
        obj_id = ObjectId(job_id)
        job = await db.jobs.find_one({"_id": obj_id})
    except Exception:
        job = await db.jobs.find_one({"_id": job_id})

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return serialize_job(job)
