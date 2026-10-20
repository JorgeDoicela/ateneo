import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from auth.security import get_current_user
from models.schemas import UserResponse
from modules.assessments.schemas import (
    DiagnosticAssessmentDTO,
    SubmitAssessmentRequest,
    AssessmentSummaryReportDTO,
)
from modules.assessments.dependencies import get_assessment_service
from modules.assessments.service import AssessmentService

logger = logging.getLogger("ateneo.modules.assessments.router")

router = APIRouter(prefix="", tags=["Evaluaciones Diagnósticas (Pre/Post-Test)"])


class StartPreTestRequest(BaseModel):
    specialty_scope: str = Field(default="Multidisciplinar GPC", description="Ámbito o especialidad clínica de la evaluación")
    num_cases: int = Field(default=3, ge=1, le=10, description="Cantidad de reactivos clínicos basales a evaluar")


class StartPostTestRequest(BaseModel):
    pre_test_id: str = Field(..., description="ID de la evaluación diagnóstica Pre-Test previa completada")


@router.post("/pre-test/start", response_model=DiagnosticAssessmentDTO, status_code=status.HTTP_201_CREATED)
async def start_pre_test(
    payload: StartPreTestRequest = StartPreTestRequest(),
    current_user: UserResponse = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Inicia una sesión de evaluación diagnóstica de entrada (Pre-Test).
    Selecciona casos basales representativos y crea la sesión en base de datos.
    """
    try:
        assessment = service.start_pre_test(
            user_id=current_user.id,
            specialty_scope=payload.specialty_scope,
            num_cases=payload.num_cases
        )
        return assessment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error al iniciar pre-test: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo interno al iniciar el Pre-Test.")


@router.post("/post-test/start", response_model=DiagnosticAssessmentDTO, status_code=status.HTTP_201_CREATED)
async def start_post_test(
    payload: StartPostTestRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Inicia una sesión de evaluación de salida (Post-Test) isomórfica asistida por IA.
    Genera casos paralelos equivalentes sobre las mismas competencias de la GPC del MSP
    para medir la ganancia formativa pura de Hake (g).
    """
    try:
        post_test = service.start_post_test(
            pre_test_id=payload.pre_test_id,
            user_id=current_user.id
        )
        return post_test
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error al iniciar post-test: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo interno al sintetizar el Post-Test isomórfico.")


@router.post("/{assessment_id}/submit", response_model=AssessmentSummaryReportDTO)
async def submit_assessment(
    assessment_id: str,
    payload: SubmitAssessmentRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    """
    Recibe y califica las respuestas de la evaluación diagnóstica:
    - Pre-Test: Dispara la síntesis heurística automática del Plan de Estudio Prescriptivo.
    - Post-Test: Calcula en tiempo real la Ganancia Normalizada de Hake (g) contra el Pre-Test.
    """
    try:
        report = service.submit_assessment(
            assessment_id=assessment_id,
            user_id=current_user.id,
            request=payload
        )
        return report
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error al calificar evaluación diagnóstica '{assessment_id}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo al procesar y calificar la evaluación.")


@router.get("/history/me", response_model=List[DiagnosticAssessmentDTO])
async def get_my_assessment_history(
    current_user: UserResponse = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    """Consulta el historial longitudinal de evaluaciones diagnósticas del estudiante actual."""
    return service.get_user_history(current_user.id)


@router.get("/{assessment_id}", response_model=DiagnosticAssessmentDTO)
async def get_assessment(
    assessment_id: str,
    current_user: UserResponse = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service)
):
    """Consulta los detalles y reactivos de una evaluación diagnóstica."""
    assessment = service.get_assessment_details(assessment_id=assessment_id, user_id=current_user.id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación diagnóstica no encontrada o sin acceso autorizado.")
    return assessment
