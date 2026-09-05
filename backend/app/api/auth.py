from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.database.mongo import get_database
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    db = get_database()
    email_clean = payload.email.lower().strip()
    
    # Check duplicate email
    existing = await db.users.find_one({"email": email_clean})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
        
    now = datetime.now(timezone.utc)
    user_doc = {
        "name": payload.name.strip(),
        "email": email_clean,
        "hashed_password": hash_password(payload.password),
        "role": "student",
        "created_at": now,
        "updated_at": now
    }
    
    res = await db.users.insert_one(user_doc)
    user_id = str(res.inserted_id)
    
    token = create_access_token({"sub": user_id, "role": "student"})
    
    user_resp = UserResponse(
        id=user_id,
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
        has_profile=False,
        profile_strength=0
    )
    
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    db = get_database()
    email_clean = payload.email.lower().strip()
    
    user = await db.users.find_one({"email": email_clean})
    if not user or not verify_password(payload.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password combination."
        )
        
    user_id = str(user["_id"])
    role = user.get("role", "student")
    token = create_access_token({"sub": user_id, "role": role})
    
    # Check if profile exists
    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    has_profile = profile is not None
    strength = profile.get("completeness_score", 0) if profile else 0
    
    user_resp = UserResponse(
        id=user_id,
        name=user.get("name", "User"),
        email=user.get("email"),
        role=role,
        created_at=user.get("created_at") or datetime.now(timezone.utc),
        has_profile=has_profile,
        profile_strength=strength
    )
    
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    profile = await db.candidate_profiles.find_one({"user_id": user_id})
    
    return UserResponse(
        id=user_id,
        name=current_user.get("name", "User"),
        email=current_user.get("email"),
        role=current_user.get("role", "student"),
        created_at=current_user.get("created_at", datetime.now(timezone.utc)),
        has_profile=profile is not None,
        profile_strength=profile.get("completeness_score", 0) if profile else 0
    )

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully."}
