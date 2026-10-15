import logging
from typing import List, Optional
from fastapi import APIRouter, Depends

from auth.security import get_optional_current_user, UserResponse
from modules.gamification.dependencies import get_gamification_service
from modules.gamification.service import GamificationService, CAREER_LEVELS
from modules.gamification.schemas import (
    GamificationProfileDTO,
    UserAchievementProgressDTO
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gamification", tags=["Gamificación y Carrera Médica"])


@router.get("/profile", response_model=GamificationProfileDTO)
async def get_gamification_profile(
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    service: GamificationService = Depends(get_gamification_service)
):
    """
    Retorna el perfil de carrera médica y progresión de XP del estudiante en sesión.
    Si no hay sesión autenticada, usa el usuario institucional demo.
    """
    target_user_id = current_user.id if current_user else "usr_alumno_001"
    return service.get_student_profile(target_user_id)


@router.get("/achievements", response_model=List[UserAchievementProgressDTO])
async def get_student_achievements(
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    service: GamificationService = Depends(get_gamification_service)
):
    """
    Retorna el catálogo completo de hitos clínicos con el estado de avance
    (bloqueado, en progreso o completado con fecha de obtención) para el estudiante.
    """
    target_user_id = current_user.id if current_user else "usr_alumno_001"
    return service.get_student_achievements(target_user_id)


@router.get("/levels")
async def get_career_levels():
    """
    Retorna la escala formativa de niveles de carrera médica en Ateneo+.
    """
    return {"levels": CAREER_LEVELS}
