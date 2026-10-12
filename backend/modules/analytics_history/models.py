from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Index, func
from core.database import Base, SafeDateTime
from modules.auth.models import UserModel, TenantModel  # noqa: F401


class EvaluationHistoryModel(Base):
    """
    Entidad relacional persistida de cada simulación diagnóstica evaluada por el sistema RAG.
    Agnóstica de motor (compatible con SQLite y clústeres PostgreSQL en producción).
    """
    __tablename__ = "evaluation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_email = Column(String(150), nullable=False, index=True)
    case_id = Column(String(100), nullable=False, index=True)
    guia_asociada = Column(String(150), nullable=False)
    case_title = Column(String(255), nullable=False)
    score = Column(Float, nullable=False)
    score_max = Column(Integer, nullable=False, default=10)
    faithfulness_score = Column(Float, nullable=True, default=0.0)
    cohorte_id = Column(String(50), nullable=True, default="general", index=True)
    tiempo_segundos = Column(Float, nullable=True, default=0.0)
    llm_latency_ms = Column(Float, nullable=True, default=0.0, server_default="0.0")
    llm_model_used = Column(String(50), nullable=True, default="gemini-3.8-flash", server_default="gemini-3.8-flash")
    rag_tokens_used = Column(Integer, nullable=True, default=0, server_default="0")
    paraclinical_studies_count = Column(Integer, nullable=False, default=0, server_default="0")
    tenant_id = Column(
        String(50),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        default="tenant_default",
        server_default="tenant_default",
        index=True
    )
    aciertos_json = Column(Text, nullable=False, default="[]")
    omisiones_json = Column(Text, nullable=False, default="[]")
    competencias_json = Column(Text, nullable=False, default="[]")
    cita_normativa_json = Column(Text, nullable=False, default="{}")
    retroalimentacion_general = Column(Text, nullable=False, default="")
    timestamp = Column(SafeDateTime, server_default=func.now(), nullable=False, index=True)


    __table_args__ = (
        Index("ix_eval_user_created", "user_id", "timestamp"),
        Index("ix_eval_cohort_guide", "cohorte_id", "guia_asociada"),
        Index("ix_eval_tenant_cohort", "tenant_id", "cohorte_id"),
    )


class LearningActivityEventModel(Base):
    """
    Eventos granulares de interacción y navegación formativa del estudiante.
    Permite auditar tiempos de permanencia, interacción con estudios diagnósticos y diálogos socráticos.
    """
    __tablename__ = "learning_activity_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(100), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True) # case_opened, paraclinical_inspected, socratic_debrief_opened
    metadata_json = Column(Text, nullable=False, default="{}", server_default="{}")
    timestamp = Column(SafeDateTime, server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("ix_event_user_case_time", "user_id", "case_id", "timestamp"),
        Index("ix_event_tenant_type", "tenant_id", "event_type"),
    )

