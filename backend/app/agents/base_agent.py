from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class AgentRunResult:
    def __init__(
        self,
        agent_name: str,
        status: str = "completed",
        records_processed: int = 0,
        records_failed: int = 0,
        error_summary: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.agent_name = agent_name
        self.status = status
        self.records_processed = records_processed
        self.records_failed = records_failed
        self.error_summary = error_summary
        self.details = details or {}
        self.start_time = datetime.now(timezone.utc)
        self.end_time: Optional[datetime] = None

    def finish(self, status: Optional[str] = None):
        self.end_time = datetime.now(timezone.utc)
        if status:
            self.status = status

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return round((self.end_time - self.start_time).total_seconds(), 2)
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "error_summary": self.error_summary,
            "details": self.details
        }

class BaseAgent(ABC):
    agent_name: str

    @abstractmethod
    async def run(self, *args, **kwargs) -> AgentRunResult:
        pass
