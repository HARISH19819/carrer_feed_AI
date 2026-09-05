from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    location_type: str = "remote"  # remote, hybrid, onsite, unknown
    employment_type: str = "full_time"  # full_time, internship, part_time, contract, freelance
    experience_level: str = "fresher"  # fresher, entry_level, junior, mid_level, senior, unknown
    experience_required: Optional[str] = "0-1 years"
    min_experience_years: float = 0.0
    max_experience_years: float = 1.0
    salary: Optional[str] = "Not specified"
    description: str
    skills: List[str] = []
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    domain: Optional[str] = "Software Development"
    secondary_domains: List[str] = []
    classification_method: str = "deterministic"
    source: str
    source_url: str
    application_url: str
    posted_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    status: str = "active"  # active, expired, duplicate, archived
    fingerprint: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    relative_posted_time: Optional[str] = "Recently"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
