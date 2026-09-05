from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.job import JobResponse

class ScoreBreakdown(BaseModel):
    skill_score: float
    role_score: float
    domain_score: float
    experience_score: float
    education_score: float
    location_score: float
    preference_score: float
    semantic_similarity: float

class MatchResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    job: JobResponse
    score: int  # 0 - 100
    match_tier: str  # Excellent Match, Strong Match, Good Match, Moderate Match, Low Match
    strong_matches: List[str]
    missing_skills: List[str]
    why_matched: str
    breakdown: ScoreBreakdown
    is_saved: bool = False
    application_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class MatchListResponse(BaseModel):
    items: List[MatchResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
