from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from rag.isomorphic_generator import IsomorphicCaseResult as IsomorphicCaseDTO


class DiagnosticItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    assessment_id: str
    case_id: Optional[str] = None
    prompt_text: str
    student_answer: str = ""
    score_obtained: float = 0.0
    omisiones_json: str = "[]"
    competencias_json: str = "[]"


class DiagnosticAssessmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    assessment_type: str  # 'pre_test' | 'post_test' | 'baseline'
    related_assessment_id: Optional[str] = None
    specialty_scope: str = "Multidisciplinar GPC"
    score_total: float = 0.0
    score_max: float = 10.0
    hake_gain_g: Optional[float] = None
    status: str = "pending"  # 'pending' | 'in_progress' | 'completed'
    started_at: datetime
    completed_at: Optional[datetime] = None
    items: List[DiagnosticItemDTO] = Field(default_factory=list)


class SubmitItemAnswerRequest(BaseModel):
    item_id: int
    student_answer: str


class SubmitAssessmentRequest(BaseModel):
    assessment_id: str
    answers: List[SubmitItemAnswerRequest]


class AssessmentSummaryReportDTO(BaseModel):
    assessment_id: str
    user_id: str
    assessment_type: str
    score_total: float
    score_max: float
    hake_gain_g: Optional[float] = None
    hake_category: Optional[str] = None
    total_omisiones_detectadas: int = 0
    competencias_afectadas: List[str] = Field(default_factory=list)
    completed_at: datetime
