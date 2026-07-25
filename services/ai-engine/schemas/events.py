from typing import Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def current_utc_time():
    return datetime.now(timezone.utc).isoformat()

class BaseJobEvent(BaseModel):
    jobId: str
    type: Literal["progress", "warning", "completed", "failed", "log"]
    timestamp: str = Field(default_factory=current_utc_time)

class ProgressEvent(BaseJobEvent):
    type: Literal["progress"] = "progress"
    stage: str
    message: str
    progress: int
    estimatedRemaining: Optional[int] = None
    currentScene: Optional[int] = None
    totalScenes: Optional[int] = None

class CompletedEvent(BaseJobEvent):
    type: Literal["completed"] = "completed"
    videoUrl: Optional[str] = None
    result: Optional[Any] = None

class FailedEvent(BaseJobEvent):
    type: Literal["failed"] = "failed"
    error: str

class WarningEvent(BaseJobEvent):
    type: Literal["warning"] = "warning"
    message: str

class LogEvent(BaseJobEvent):
    type: Literal["log"] = "log"
    message: str
