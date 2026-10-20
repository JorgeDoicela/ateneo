from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class StudyPlanTaskDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    plan_id: str
    task_type: str  # 'gpc_reading' | 'case_simulation' | 'socratic_review'
    title: str
    description: str = ""
    resource_reference: str = ""
    competency_id: str = "semiologia_anamnesis"
    estimated_minutes: int = 15
    is_completed: bool = False
    completed_at: Optional[datetime] = None


class PrescriptiveStudyPlanDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    source_assessment_id: Optional[str] = None
    title: str
    diagnosis_summary: str = ""
    target_duration_days: int = 7
    progress_percentage: float = 0.0
    status: str = "active"  # 'active' | 'completed' | 'expired'
    created_at: datetime
    completed_at: Optional[datetime] = None
    tasks: List[StudyPlanTaskDTO] = Field(default_factory=list)


class CompleteTaskResponseDTO(BaseModel):
    task_id: int
    plan_id: str
    is_completed: bool
    progress_percentage: float
    plan_completed: bool
    completed_at: datetime
