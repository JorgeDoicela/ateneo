import uuid
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from core.database import Base, SafeDateTime
from modules.auth.models import UserModel  # noqa: F401
from modules.assessments.models import DiagnosticAssessmentModel  # noqa: F401


class PrescriptiveStudyPlanModel(Base):
    """
    Entidad relacional persistida de un Plan de Estudio Prescriptivo personalizado.
    Generado determinísticamente a partir del diagnóstico inicial de brechas (Pre-Test)
    o de la analítica longitudinal acumulada del estudiante.
    """
    __tablename__ = "prescriptive_study_plans"

    id = Column(String(100), primary_key=True, default=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_assessment_id = Column(String(100), ForeignKey("diagnostic_assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    diagnosis_summary = Column(Text, nullable=False, default="")
    target_duration_days = Column(Integer, nullable=False, default=7)
    progress_percentage = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False, default="active", index=True)  # 'active' | 'completed' | 'expired'
    created_at = Column(SafeDateTime, server_default=func.now(), nullable=False)
    completed_at = Column(SafeDateTime, nullable=True)

    # Relaciones
    tasks = relationship(
        "StudyPlanTaskModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="StudyPlanTaskModel.id",
        lazy="selectin"
    )
    source_assessment = relationship("DiagnosticAssessmentModel")

    __table_args__ = (
        Index("ix_plan_user_status", "user_id", "status"),
    )


class StudyPlanTaskModel(Base):
    """
    Tarea pedagógica atómica dosificada dentro de un Plan de Estudio Prescriptivo.
    Puede ser lectura guiada de una GPC, simulación de un caso clínico en ZDP
    o revisión socrática de conceptos clave.
    """
    __tablename__ = "study_plan_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String(100), ForeignKey("prescriptive_study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(50), nullable=False, index=True)  # 'gpc_reading' | 'case_simulation' | 'socratic_review'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    resource_reference = Column(String(255), nullable=False, default="")  # ID de caso (ej: case_preeclampsia_01) o título de GPC
    competency_id = Column(String(100), nullable=False, default="semiologia_anamnesis")  # Nodo KST
    estimated_minutes = Column(Integer, nullable=False, default=15)
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(SafeDateTime, nullable=True)

    plan = relationship("PrescriptiveStudyPlanModel", back_populates="tasks")

    __table_args__ = (
        Index("ix_task_plan_status", "plan_id", "is_completed"),
        Index("ix_task_type_comp", "task_type", "competency_id"),
    )
