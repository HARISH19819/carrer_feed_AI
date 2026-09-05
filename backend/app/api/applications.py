from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from bson import ObjectId
from app.database.mongo import get_database
from app.api.deps import get_current_user
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationStats
from app.api.jobs import serialize_job

router = APIRouter(prefix="/applications", tags=["Applications"])

VALID_STATUSES = ["Saved", "Viewed", "Applied", "Interview", "Selected", "Rejected"]

@router.get("", response_model=list[ApplicationResponse])
async def list_applications(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    cursor = db.applications.find({"user_id": user_id}).sort("updated_at", -1)
    apps = await cursor.to_list(length=300)

    results = []
    for a in apps:
        job_id = a.get("job_id")
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            job = await db.jobs.find_one({"_id": job_id})

        results.append(ApplicationResponse(
            id=str(a["_id"]),
            user_id=user_id,
            job_id=job_id,
            job=serialize_job(job) if job else None,
            status=a.get("status", "Applied"),
            notes=a.get("notes"),
            applied_at=a.get("applied_at"),
            created_at=a.get("created_at", datetime.now(timezone.utc)),
            updated_at=a.get("updated_at", datetime.now(timezone.utc))
        ))

    return results

@router.post("/{job_id}", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_application(
    job_id: str,
    payload: ApplicationCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user_id = current_user["id"]

    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        job = await db.jobs.find_one({"_id": job_id})

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {VALID_STATUSES}")

    now = datetime.now(timezone.utc)
    existing = await db.applications.find_one({"user_id": user_id, "job_id": job_id})

    if existing:
        await db.applications.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "status": payload.status,
                "notes": payload.notes if payload.notes is not None else existing.get("notes"),
                "updated_at": now
            }}
        )
        app_doc = await db.applications.find_one({"_id": existing["_id"]})
    else:
        app_doc = {
            "user_id": user_id,
            "job_id": job_id,
            "status": payload.status,
            "notes": payload.notes,
            "applied_at": now if payload.status == "Applied" else None,
            "created_at": now,
            "updated_at": now
        }
        res = await db.applications.insert_one(app_doc)
        app_doc["_id"] = res.inserted_id

    return ApplicationResponse(
        id=str(app_doc["_id"]),
        user_id=user_id,
        job_id=job_id,
        job=serialize_job(job),
        status=app_doc["status"],
        notes=app_doc.get("notes"),
        applied_at=app_doc.get("applied_at"),
        created_at=app_doc["created_at"],
        updated_at=app_doc["updated_at"]
    )

@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application_status(
    application_id: str,
    payload: ApplicationUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user_id = current_user["id"]

    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {VALID_STATUSES}")

    try:
        obj_id = ObjectId(application_id)
        app_doc = await db.applications.find_one({"_id": obj_id, "user_id": user_id})
    except Exception:
        app_doc = await db.applications.find_one({"_id": application_id, "user_id": user_id})

    if not app_doc:
        raise HTTPException(status_code=404, detail="Application record not found.")

    now = datetime.now(timezone.utc)
    updates = {"status": payload.status, "updated_at": now}
    if payload.notes is not None:
        updates["notes"] = payload.notes
    if payload.status == "Applied" and not app_doc.get("applied_at"):
        updates["applied_at"] = now

    await db.applications.update_one({"_id": app_doc["_id"]}, {"$set": updates})
    updated = await db.applications.find_one({"_id": app_doc["_id"]})

    # Fetch job
    job_id = updated["job_id"]
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        job = await db.jobs.find_one({"_id": job_id})

    return ApplicationResponse(
        id=str(updated["_id"]),
        user_id=user_id,
        job_id=job_id,
        job=serialize_job(job) if job else None,
        status=updated["status"],
        notes=updated.get("notes"),
        applied_at=updated.get("applied_at"),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"]
    )

@router.get("/stats/summary", response_model=ApplicationStats)
async def get_application_stats(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]

    cursor = db.applications.find({"user_id": user_id})
    all_apps = await cursor.to_list(length=1000)

    counts = {s: 0 for s in VALID_STATUSES}
    for a in all_apps:
        st = a.get("status")
        if st in counts:
            counts[st] += 1

    total = len(all_apps)
    interviews = counts["Interview"]
    selected = counts["Selected"]
    applied = counts["Applied"]

    response_rate = round(((interviews + selected) / applied * 100), 1) if applied > 0 else 0.0

    return ApplicationStats(
        total=total,
        saved=counts["Saved"],
        viewed=counts["Viewed"],
        applied=applied,
        interview=interviews,
        selected=selected,
        rejected=counts["Rejected"],
        response_rate_percent=response_rate
    )
