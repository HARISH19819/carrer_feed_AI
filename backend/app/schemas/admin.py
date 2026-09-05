from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class DomainCount(BaseModel):
    domain: str
    count: int

class SourceCount(BaseModel):
    source: str
    count: int

class AdminStatsResponse(BaseModel):
    total_users: int = 0
    total_candidates: int = 0
    total_jobs: int = 0
    active_jobs: int = 0
    jobs_today: int = 0
    jobs_by_domain: List[DomainCount] = []
    jobs_by_source: List[SourceCount] = []
    pipeline_runs_count: int = 0
    failed_runs_count: int = 0
    duplicate_count_total: int = 0
    duplicate_rate_percent: float = 0.0
    average_match_score: float = 0.0

class JobSourceItem(BaseModel):
    id: str
    name: str
    adapter_key: str
    source_type: str  # api, rss, dataset
    base_url: str
    enabled: bool
    last_run_at: Optional[datetime] = None
    last_status: str = "idle"
    jobs_fetched_total: int = 0
    description: str

class UpdateJobSourcePayload(BaseModel):
    enabled: Optional[bool] = None
