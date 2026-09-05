from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EducationItem(BaseModel):
    degree: str = "B.Tech"
    field: Optional[str] = "Computer Science"
    institution: Optional[str] = "University"
    graduation_year: Optional[int] = 2026

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = []

class WorkExperienceItem(BaseModel):
    title: str
    company: str
    duration: Optional[str] = None
    description: Optional[str] = None

class CandidateProfileBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[EducationItem] = []
    experience_level: str = "fresher"  # fresher, entry_level, junior, mid_level, senior
    years_of_experience: float = 0.0
    skills: List[str] = []
    domains: List[str] = []
    recommended_roles: List[str] = []
    preferred_locations: List[str] = []
    preferred_job_types: List[str] = ["internship", "full_time"]
    remote_preference: str = "any"  # remote, hybrid, onsite, any
    minimum_match_score: int = 60
    projects: List[ProjectItem] = []
    certifications: List[str] = []
    work_experiences: List[WorkExperienceItem] = []

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    recommended_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_job_types: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    minimum_match_score: Optional[int] = None
    experience_level: Optional[str] = None
    years_of_experience: Optional[float] = None
    education: Optional[List[EducationItem]] = None

class CandidateProfileResponse(CandidateProfileBase):
    id: str
    user_id: str
    completeness_score: int = 0
    created_at: datetime
    updated_at: datetime
