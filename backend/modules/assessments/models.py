import uuid
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from core.database import Base, SafeDateTime
from modules.auth.models import UserModel  # noqa: F401


class DiagnosticAssessmentModel(Base):
    """
    Entidad relacional persistida de una evaluación diagnóstica formal (Pre-Test o Post-Test).
    Soporta seguimiento longitudinal del estudiante y cálculo psicométrico de ganancia de Hake (g).
    Agnóstica de motor (compatible con SQLite WAL y PostgreSQL).
    """
    __tablename__ = "diagnostic_assessments"

    id = Column(String(100), primary_key=True, default=lambda: f"eval_{uuid.uuid4().hex[:12]}")
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_type = Column(String(50), nullable=False, index=True)  # 'pre_test' | 'post_test' | 'baseline'
    related_assessment_id = Column(String(100), ForeignKey("diagnostic_assessments.id", ondelete="SET NULL"), nullable=True, index=True)
    specialty_scope = Column(String(150), nullable=False, default="Multidisciplinar GPC")
    score_total = Column(Float, nullable=False, default=0.0)
    score_max = Column(Float, nullable=False, default=10.0)
    hake_gain_g = Column(Float, nullable=True)  # Calculado en post_test respecto a su related_assessment_id (pre_test)
    status = Column(String(50), nullable=False, default="pending", index=True)  # 'pending' | 'in_progress' | 'completed'
    started_at = Column(SafeDateTime, server_default=func.now(), nullable=False)
    completed_at = Column(SafeDateTime, nullable=True)

    # Relaciones
    items = relationship(
        "DiagnosticItemModel",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="DiagnosticItemModel.id",
        lazy="selectin"
    )
    pre_test = relationship(
        "DiagnosticAssessmentModel",
        remote_side=[id],
        foreign_keys=[related_assessment_id],
        back_populates="post_tests"
    )
    post_tests = relationship(
        "DiagnosticAssessmentModel",
        foreign_keys=[related_assessment_id],
        back_populates="pre_test"
    )

    __table_args__ = (
        Index("ix_diag_user_type", "user_id", "assessment_type"),
        Index("ix_diag_status_date", "status", "started_at"),
    )


class DiagnosticItemModel(Base):
    """
    Reactivo o caso clínico evaluado dentro de una sesión diagnóstica (Pre-Test / Post-Test).
    Almacena la respuesta argumentativa del estudiante, la calificación obtenida y el vector
    de omisiones clínicas detectadas frente a las Guías de Práctica Clínica (GPC).
    """
    __tablename__ = "diagnostic_assessment_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String(100), ForeignKey("diagnostic_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(100), nullable=True, index=True)
    prompt_text = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False, default="")
    score_obtained = Column(Float, nullable=False, default=0.0)
    omisiones_json = Column(Text, nullable=False, default="[]")
    competencias_json = Column(Text, nullable=False, default="[]")

    assessment = relationship("DiagnosticAssessmentModel", back_populates="items")

    __table_args__ = (
        Index("ix_item_assessment_case", "assessment_id", "case_id"),
    )
