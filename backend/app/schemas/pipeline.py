from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class AgentRunResponse(BaseModel):
    id: str
    run_id: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    status: str  # queued, running, completed, failed
    records_processed: int = 0
    records_failed: int = 0
    error_summary: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class PipelineRunResponse(BaseModel):
    id: str
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    status: str
    discovered_count: int = 0
    normalized_count: int = 0
    duplicate_count: int = 0
    classified_count: int = 0
    embedded_count: int = 0
    matched_count: int = 0
    error_details: Optional[str] = None
    agent_runs: List[AgentRunResponse] = []

class AgentDashboardCard(BaseModel):
    agent_id: str
    name: str
    description: str
    status: str
    metric_label: str
    metric_value: str
    last_run_time: Optional[str] = "Never"
    action_label: str
