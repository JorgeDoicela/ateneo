import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc, func
from modules.study_plans.models import PrescriptiveStudyPlanModel, StudyPlanTaskModel

logger = logging.getLogger(__name__)


class StudyPlanRepository:
    """
    Repositorio de persistencia relacional para Planes de Estudio Prescriptivos y sus Tareas formativas.
    """
    def __init__(self, session: Session):
        self.session = session

    def create_plan(self, plan: PrescriptiveStudyPlanModel) -> PrescriptiveStudyPlanModel:
        self.session.add(plan)
        self.session.flush()
        return plan

    def get_plan_by_id(self, plan_id: str) -> Optional[PrescriptiveStudyPlanModel]:
        stmt = select(PrescriptiveStudyPlanModel).where(PrescriptiveStudyPlanModel.id == plan_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_plan_by_user(self, user_id: str) -> Optional[PrescriptiveStudyPlanModel]:
        stmt = (
            select(PrescriptiveStudyPlanModel)
            .where(
                and_(
                    PrescriptiveStudyPlanModel.user_id == user_id,
                    PrescriptiveStudyPlanModel.status == "active"
                )
            )
            .order_by(desc(PrescriptiveStudyPlanModel.created_at))
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_user_plans(self, user_id: str) -> List[PrescriptiveStudyPlanModel]:
        stmt = (
            select(PrescriptiveStudyPlanModel)
            .where(PrescriptiveStudyPlanModel.user_id == user_id)
            .order_by(desc(PrescriptiveStudyPlanModel.created_at))
        )
        return list(self.session.execute(stmt).scalars().all())

    def update_plan(self, plan: PrescriptiveStudyPlanModel) -> PrescriptiveStudyPlanModel:
        self.session.merge(plan)
        self.session.flush()
        return plan

    def add_task(self, task: StudyPlanTaskModel) -> StudyPlanTaskModel:
        self.session.add(task)
        self.session.flush()
        return task

    def get_plan_tasks(self, plan_id: str) -> List[StudyPlanTaskModel]:
        stmt = (
            select(StudyPlanTaskModel)
            .where(StudyPlanTaskModel.plan_id == plan_id)
            .order_by(StudyPlanTaskModel.id.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_task_by_id(self, task_id: int) -> Optional[StudyPlanTaskModel]:
        stmt = select(StudyPlanTaskModel).where(StudyPlanTaskModel.id == task_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def mark_task_completed(self, task_id: int) -> Optional[StudyPlanTaskModel]:
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        from datetime import datetime, timezone
        task.is_completed = True
        task.completed_at = datetime.now(timezone.utc)
        self.session.flush()

        # Recalcular porcentaje de progreso del plan asociado
        self.recalculate_plan_progress(task.plan_id)
        return task

    def recalculate_plan_progress(self, plan_id: str) -> float:
        plan = self.get_plan_by_id(plan_id)
        if not plan:
            return 0.0

        tasks = self.get_plan_tasks(plan_id)
        if not tasks:
            plan.progress_percentage = 0.0
            self.session.flush()
            return 0.0

        completed_count = sum(1 for t in tasks if t.is_completed)
        pct = round((completed_count / len(tasks)) * 100, 1)
        plan.progress_percentage = pct

        if pct >= 100.0 and plan.status == "active":
            from datetime import datetime, timezone
            plan.status = "completed"
            plan.completed_at = datetime.now(timezone.utc)

        self.session.flush()
        return pct
