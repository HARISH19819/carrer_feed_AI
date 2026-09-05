from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.job import JobResponse

class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "Applied"  # Saved, Viewed, Applied, Interview, Selected, Rejected
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    job: Optional[JobResponse] = None
    status: str
    notes: Optional[str] = None
    applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ApplicationStats(BaseModel):
    total: int = 0
    saved: int = 0
    viewed: int = 0
    applied: int = 0
    interview: int = 0
    selected: int = 0
    rejected: int = 0
    response_rate_percent: float = 0.0
