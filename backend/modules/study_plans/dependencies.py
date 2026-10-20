from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.study_plans.repository import StudyPlanRepository


def get_study_plan_repository(session: Session = Depends(get_db)) -> StudyPlanRepository:
    """Proveedor de dependencias para el repositorio de planes de estudio prescriptivos."""
    return StudyPlanRepository(session)


def get_study_plan_service(session: Session = Depends(get_db)):
    """Proveedor de dependencias para el servicio de planes de estudio prescriptivos."""
    from modules.study_plans.service import StudyPlanService
    return StudyPlanService(repository=StudyPlanRepository(session), session=session)
