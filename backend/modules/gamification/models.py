from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, Index, UniqueConstraint, func
from core.database import Base, SafeDateTime
from modules.auth.models import UserModel  # noqa: F401


class AchievementDefinitionModel(Base):
    """
    Catálogo canónico de hitos clínicos y reconocimientos formativos.
    Inmutable en tiempo de ejecución de la simulación.
    """
    __tablename__ = "achievement_definitions"

    id = Column(String(80), primary_key=True)
    codigo = Column(String(80), unique=True, nullable=False, index=True)
    titulo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False, default="diagnostico", index=True)
    icono = Column(String(50), nullable=False, default="Award")
    puntos_xp = Column(Integer, nullable=False, default=100)
    criterio_tipo = Column(String(50), nullable=False)
    criterio_valor = Column(Float, nullable=False, default=1.0)
    activo = Column(Boolean, nullable=False, default=True)


class StudentGamificationProfileModel(Base):
    """
    Perfil consolidado de progresión clínica, puntos de experiencia (XP)
    y rango formativo del estudiante en la plataforma Ateneo+.
    """
    __tablename__ = "student_gamification_profiles"

    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    puntos_xp = Column(Integer, nullable=False, default=0)
    nivel_actual = Column(Integer, nullable=False, default=1)
    titulo_rango = Column(String(100), nullable=False, default="Estudiante Clínico Inicial")
    casos_resueltos = Column(Integer, nullable=False, default=0)
    racha_dias = Column(Integer, nullable=False, default=1)
    ultimo_acceso_fecha = Column(SafeDateTime, server_default=func.now(), nullable=False)
    updated_at = Column(SafeDateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class StudentUnlockedAchievementModel(Base):
    """
    Registro histórico de hitos clínicos alcanzados por cada estudiante.
    Garantiza unicidad por usuario y logro.
    """
    __tablename__ = "student_unlocked_achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id = Column(String(80), ForeignKey("achievement_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    desbloqueado_en = Column(SafeDateTime, server_default=func.now(), nullable=False)
    progreso_actual = Column(Float, nullable=False, default=1.0)
    meta = Column(Float, nullable=False, default=1.0)
    completado = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
        Index("ix_unlocked_user_achievement", "user_id", "achievement_id"),
    )
