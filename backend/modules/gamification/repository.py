from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from datetime import datetime, timezone

from modules.gamification.models import (
    AchievementDefinitionModel,
    StudentGamificationProfileModel,
    StudentUnlockedAchievementModel
)


class GamificationRepository:
    """
    Repositorio de persistencia relacional para el subsistema de gamificación clínica y logros.
    Agnóstico de motor (SQLite WAL y PostgreSQL en producción).
    """
    def __init__(self, session: Session):
        self.session = session

    def get_all_active_definitions(self) -> List[AchievementDefinitionModel]:
        """Obtiene todas las definiciones de hitos clínicos activos."""
        stmt = select(AchievementDefinitionModel).where(AchievementDefinitionModel.activo.is_(True))
        return list(self.session.execute(stmt).scalars().all())

    def get_definition_by_id(self, achievement_id: str) -> Optional[AchievementDefinitionModel]:
        stmt = select(AchievementDefinitionModel).where(AchievementDefinitionModel.id == achievement_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_or_create_profile(self, user_id: str) -> StudentGamificationProfileModel:
        """Obtiene el perfil de progresión del estudiante o lo inicializa si es su primera actividad."""
        stmt = select(StudentGamificationProfileModel).where(StudentGamificationProfileModel.user_id == user_id)
        profile = self.session.execute(stmt).scalar_one_or_none()
        if not profile:
            profile = StudentGamificationProfileModel(
                user_id=user_id,
                puntos_xp=0,
                nivel_actual=1,
                titulo_rango="Estudiante Clínico Inicial",
                casos_resueltos=0,
                racha_dias=1,
                ultimo_acceso_fecha=datetime.now(timezone.utc)
            )
            self.session.add(profile)
            self.session.flush()
        return profile

    def update_profile(self, profile: StudentGamificationProfileModel) -> StudentGamificationProfileModel:
        profile.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return profile

    def get_user_unlocked_achievements(self, user_id: str) -> List[StudentUnlockedAchievementModel]:
        """Obtiene los hitos desbloqueados por un usuario."""
        stmt = select(StudentUnlockedAchievementModel).where(
            and_(
                StudentUnlockedAchievementModel.user_id == user_id,
                StudentUnlockedAchievementModel.completado.is_(True)
            )
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_user_achievement(self, user_id: str, achievement_id: str) -> Optional[StudentUnlockedAchievementModel]:
        stmt = select(StudentUnlockedAchievementModel).where(
            and_(
                StudentUnlockedAchievementModel.user_id == user_id,
                StudentUnlockedAchievementModel.achievement_id == achievement_id
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def unlock_achievement(
        self,
        user_id: str,
        achievement_id: str,
        progreso_actual: float = 1.0,
        meta: float = 1.0
    ) -> Tuple[StudentUnlockedAchievementModel, bool]:
        """
        Registra el desbloqueo de un hito para un usuario de forma idempotente.
        Retorna (modelo, es_nuevo_desbloqueo).
        """
        existing = self.get_user_achievement(user_id, achievement_id)
        if existing:
            if not existing.completado and progreso_actual >= meta:
                existing.completado = True
                existing.progreso_actual = meta
                existing.desbloqueado_en = datetime.now(timezone.utc)
                self.session.flush()
                return existing, True
            return existing, False

        new_unlock = StudentUnlockedAchievementModel(
            user_id=user_id,
            achievement_id=achievement_id,
            desbloqueado_en=datetime.now(timezone.utc),
            progreso_actual=progreso_actual,
            meta=meta,
            completado=True
        )
        self.session.add(new_unlock)
        self.session.flush()
        return new_unlock, True

    def count_user_achievements(self, user_id: str) -> int:
        stmt = select(func.count(StudentUnlockedAchievementModel.id)).where(
            and_(
                StudentUnlockedAchievementModel.user_id == user_id,
                StudentUnlockedAchievementModel.completado.is_(True)
            )
        )
        return self.session.execute(stmt).scalar_one() or 0
