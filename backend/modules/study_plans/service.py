import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable
from sqlalchemy.orm import Session

from modules.study_plans.models import PrescriptiveStudyPlanModel, StudyPlanTaskModel
from modules.study_plans.repository import StudyPlanRepository
from modules.study_plans.heuristic_engine import StudyPlanHeuristicEngine
from modules.study_plans.schemas import CompleteTaskResponseDTO

logger = logging.getLogger(__name__)


def _default_uow():
    from core.unit_of_work import SqlAlchemyUnitOfWork
    return SqlAlchemyUnitOfWork()


class StudyPlanService:
    """
    Servicio de Dominio para la Gestión de Planes de Estudio Prescriptivos.
    Orquesta la síntesis heurística, la persistencia atómica en Unit of Work
    y el avance formativo del estudiante.
    """
    def __init__(
        self,
        repository: Optional[StudyPlanRepository] = None,
        session: Optional[Session] = None,
        uow_factory: Optional[Callable[[], Any]] = None
    ):
        self.repository = repository
        self.session = session
        self.uow_factory = uow_factory or _default_uow

    def generate_plan_from_assessment(self, assessment_id: str, user_id: str) -> PrescriptiveStudyPlanModel:
        """
        Sintetiza y persiste un Plan de Estudio Prescriptivo a partir de un Pre-Test completado.
        Garantiza consistencia transaccional (ACID) y archiva planes activos previos.
        """
        uow = self.uow_factory()
        with uow:
            assessment = uow.assessments.get_assessment_by_id(assessment_id)
            if not assessment:
                raise ValueError(f"Evaluación diagnóstica '{assessment_id}' no encontrada.")

            # Obtener ítems evaluados con sus omisiones clínicas
            items = uow.assessments.get_assessment_items(assessment_id)
            items_payload = []
            for item in items:
                items_payload.append({
                    "prompt_text": item.prompt_text,
                    "case_id": item.case_id,
                    "score": item.score_obtained,
                    "omisiones": item.omisiones_json,
                    "competencias": item.competencias_json
                })

            # Consultar estado de maestría BKT actual del usuario
            mastery_state = uow.adaptive.get_mastery(user_id) or {}

            # Ejecutar síntesis determinística del plan
            plan_data = StudyPlanHeuristicEngine.synthesize_prescriptive_plan(
                assessment_items=items_payload,
                knowledge_state=mastery_state
            )

            # Archivar cualquier plan activo previo del estudiante
            existing_active = uow.study_plans.get_active_plan_by_user(user_id)
            if existing_active:
                existing_active.status = "expired"
                uow.study_plans.update_plan(existing_active)

            # Crear nueva entidad del plan prescriptivo
            new_plan = PrescriptiveStudyPlanModel(
                user_id=user_id,
                source_assessment_id=assessment_id,
                title=plan_data["title"],
                diagnosis_summary=plan_data["diagnosis_summary"],
                target_duration_days=plan_data["target_duration_days"],
                progress_percentage=0.0,
                status="active"
            )
            created_plan = uow.study_plans.create_plan(new_plan)

            # Persistir tareas formativas dosificadas
            for t_data in plan_data["tasks"]:
                task_model = StudyPlanTaskModel(
                    plan_id=created_plan.id,
                    task_type=t_data["task_type"],
                    title=t_data["title"],
                    description=t_data["description"],
                    resource_reference=t_data["resource_reference"],
                    competency_id=t_data["competency_id"],
                    estimated_minutes=t_data["estimated_minutes"],
                    is_completed=False
                )
                uow.study_plans.add_task(task_model)

            uow.commit()

            # Retornar plan persistido con sus tareas
            plan = uow.study_plans.get_plan_by_id(created_plan.id)
            if plan:
                _ = plan.tasks
            return plan

    def get_active_plan(self, user_id: str) -> Optional[PrescriptiveStudyPlanModel]:
        """Consulta el plan prescriptivo activo para el estudiante."""
        if self.repository:
            plan = self.repository.get_active_plan_by_user(user_id)
            if plan:
                _ = plan.tasks
            return plan

        uow = self.uow_factory()
        with uow:
            plan = uow.study_plans.get_active_plan_by_user(user_id)
            if plan:
                _ = plan.tasks
            return plan

    def get_plan_details(self, plan_id: str, user_id: str) -> Optional[PrescriptiveStudyPlanModel]:
        """Consulta el detalle de un plan específico verificando propiedad de usuario."""
        uow = self.uow_factory()
        with uow:
            plan = uow.study_plans.get_plan_by_id(plan_id)
            if plan and plan.user_id != user_id:
                return None
            if plan:
                _ = plan.tasks
            return plan

    def complete_task(self, task_id: int, user_id: str) -> CompleteTaskResponseDTO:
        """
        Marca una tarea como completada, recalcula el avance porcentual del plan
        y retorna la confirmación de estado.
        """
        uow = self.uow_factory()
        with uow:
            task = uow.study_plans.get_task_id(task_id) if hasattr(uow.study_plans, "get_task_id") else uow.study_plans.get_task_by_id(task_id)
            if not task:
                raise ValueError(f"Tarea de estudio #{task_id} no encontrada.")

            plan = uow.study_plans.get_plan_by_id(task.plan_id)
            if not plan or plan.user_id != user_id:
                raise PermissionError("Acceso no autorizado a la tarea de este plan de estudio.")

            updated_task = uow.study_plans.mark_task_completed(task_id)
            uow.commit()

            # Consultar estado final del plan
            plan_refreshed = uow.study_plans.get_plan_by_id(task.plan_id)
            is_plan_finished = plan_refreshed.status == "completed"

            return CompleteTaskResponseDTO(
                task_id=updated_task.id,
                plan_id=updated_task.plan_id,
                is_completed=True,
                progress_percentage=plan_refreshed.progress_percentage,
                plan_completed=is_plan_finished,
                completed_at=updated_task.completed_at or datetime.now(timezone.utc)
            )
