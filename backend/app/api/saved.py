from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from bson import ObjectId
from app.database.mongo import get_database
from app.api.deps import get_current_user
from app.api.jobs import serialize_job

router = APIRouter(prefix="/saved", tags=["Saved Jobs"])

@router.get("")
async def get_saved_jobs(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    cursor = db.saved_jobs.find({"user_id": user_id}).sort("created_at", -1)
    saved_records = await cursor.to_list(length=200)

    results = []
    for r in saved_records:
        job_id = r.get("job_id")
        try:
            job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        except Exception:
            job = await db.jobs.find_one({"_id": job_id})

        if job:
            match = await db.matches.find_one({"user_id": user_id, "job_id": job_id})
            results.append({
                "id": str(r["_id"]),
                "job_id": job_id,
                "saved_at": r.get("created_at"),
                "score": match.get("score") if match else None,
                "match_tier": match.get("match_tier") if match else None,
                "job": serialize_job(job)
            })

    return {"items": results, "total": len(results)}

@router.post("/{job_id}", status_code=status.HTTP_201_CREATED)
async def save_job(job_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    
    # Check job exists
    try:
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    except Exception:
        job = await db.jobs.find_one({"_id": job_id})
        
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    existing = await db.saved_jobs.find_one({"user_id": user_id, "job_id": job_id})
    if existing:
        return {"message": "Job is already in saved collection.", "id": str(existing["_id"])}

    now = datetime.now(timezone.utc)
    res = await db.saved_jobs.insert_one({
        "user_id": user_id,
        "job_id": job_id,
        "created_at": now
    })

    return {"message": "Job saved successfully.", "id": str(res.inserted_id)}

@router.delete("/{job_id}")
async def unsave_job(job_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    del_res = await db.saved_jobs.delete_one({"user_id": user_id, "job_id": job_id})
    if del_res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved job not found.")
    return {"message": "Job removed from saved list."}
