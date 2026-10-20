import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status

from auth.security import get_current_user
from models.schemas import UserResponse
from modules.study_plans.schemas import (
    PrescriptiveStudyPlanDTO,
    CompleteTaskResponseDTO,
)
from modules.study_plans.dependencies import get_study_plan_service
from modules.study_plans.service import StudyPlanService

logger = logging.getLogger("ateneo.modules.study_plans.router")

router = APIRouter(prefix="", tags=["Planes de Estudio Prescriptivos"])


@router.get("/me", response_model=Optional[PrescriptiveStudyPlanDTO])
async def get_my_active_study_plan(
    current_user: UserResponse = Depends(get_current_user),
    service: StudyPlanService = Depends(get_study_plan_service)
):
    """
    Consulta el Plan de Estudio Prescriptivo activo para el estudiante autenticado.
    Retorna el plan con sus tareas dosificadas (GPC, simulación ZDP, debriefing socrático).
    """
    plan = service.get_active_plan(current_user.id)
    if not plan:
        return None
    return plan


@router.get("/{plan_id}", response_model=PrescriptiveStudyPlanDTO)
async def get_study_plan_by_id(
    plan_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: StudyPlanService = Depends(get_study_plan_service)
):
    """Consulta el detalle de un plan específico verificando propiedad de usuario."""
    plan = service.get_plan_details(plan_id=plan_id, user_id=current_user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan de estudio no encontrado o no pertenece al usuario autenticado."
        )
    return plan


@router.post("/tasks/{task_id}/complete", response_model=CompleteTaskResponseDTO)
async def complete_study_plan_task(
    task_id: int,
    current_user: UserResponse = Depends(get_current_user),
    service: StudyPlanService = Depends(get_study_plan_service)
):
    """
    Marca una tarea formativa como completada y recalcula en tiempo real el porcentaje de avance del plan.
    """
    try:
        response = service.complete_task(task_id=task_id, user_id=current_user.id)
        return response
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error al completar tarea formativa #{task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo al actualizar la tarea de estudio.")
