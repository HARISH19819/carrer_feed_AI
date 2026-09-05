from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from datetime import datetime, timezone
from typing import Dict, Any
from app.database.mongo import get_database
from app.api.deps import get_current_user
from app.schemas.profile import CandidateProfileResponse, CandidateProfileUpdate
from app.agents.resume_agent import resume_profile_agent
from app.agents.match_agent import match_agent
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/profile", tags=["Candidate Profile"])

@router.get("", response_model=CandidateProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found. Please upload a resume first."
        )
    profile["id"] = str(profile["_id"])
    return profile

@router.post("/resume", response_model=CandidateProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Validate extension
    filename = file.filename or "resume.pdf"
    ext = "." + filename.lower().split(".")[-1]
    if ext not in settings.ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed extensions: {', '.join(settings.ALLOWED_RESUME_EXTENSIONS)}"
        )

    # Read content and validate file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10MB limit."
        )
    if len(content) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File appears to be empty."
        )

    db = get_database()
    user_id = current_user["id"]

    try:
        # Run Resume / Profile Agent
        profile_data = await resume_profile_agent.parse_resume_to_profile(filename, content)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        logger.error(f"Resume parsing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="We couldn't parse this resume. Please ensure it is a valid, uncorrupted PDF or DOCX file."
        )

    now = datetime.now(timezone.utc)
    profile_data["user_id"] = user_id
    profile_data["updated_at"] = now

    # Check if existing profile
    existing = await db.candidate_profiles.find_one({"user_id": user_id})
    if existing:
        await db.candidate_profiles.update_one(
            {"user_id": user_id},
            {"$set": profile_data}
        )
        profile_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    else:
        profile_data["created_at"] = now
        ins = await db.candidate_profiles.insert_one(profile_data)
        profile_doc = profile_data
        profile_doc["_id"] = ins.inserted_id

    profile_doc["id"] = str(profile_doc["_id"])

    # Auto-trigger personalized matching for the freshly uploaded candidate profile
    try:
        await match_agent.match_user_with_jobs(user_id, profile_doc)
    except Exception as match_err:
        logger.warning(f"Immediate matching after resume upload failed: {match_err}")

    return profile_doc

@router.put("", response_model=CandidateProfileResponse)
async def update_profile(
    payload: CandidateProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    user_id = current_user["id"]
    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    update_dict = {k: v for k, v in payload.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc)

    # Recalculate completeness score
    merged = {**profile, **update_dict}
    update_dict["completeness_score"] = resume_profile_agent.calculate_profile_strength(merged)

    await db.candidate_profiles.update_one(
        {"user_id": user_id},
        {"$set": update_dict}
    )

    updated_profile = await db.candidate_profiles.find_one({"user_id": user_id})
    updated_profile["id"] = str(updated_profile["_id"])

    # Re-trigger matching with new preferences/skills
    try:
        await match_agent.match_user_with_jobs(user_id, updated_profile)
    except Exception as err:
        logger.warning(f"Re-matching after profile update failed: {err}")

    return updated_profile

@router.post("/reanalyze")
async def reanalyze_profile(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile found to re-analyze.")

    # Re-infer domains and recommended roles
    domains = resume_profile_agent.infer_domains(profile.get("skills", []), "")
    roles = resume_profile_agent.infer_recommended_roles(domains, profile.get("skills", []))
    
    updates = {
        "domains": domains,
        "recommended_roles": roles,
        "updated_at": datetime.now(timezone.utc)
    }
    await db.candidate_profiles.update_one({"user_id": user_id}, {"$set": updates})
    
    # Re-run matching
    merged = {**profile, **updates}
    matches = await match_agent.match_user_with_jobs(user_id, merged)
    
    return {
        "message": "Profile successfully re-analyzed and matches refreshed.",
        "matches_generated": len(matches)
    }
