from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.assessments.repository import AssessmentRepository


def get_assessment_repository(session: Session = Depends(get_db)) -> AssessmentRepository:
    """Proveedor de dependencias para el repositorio de evaluaciones diagnósticas."""
    return AssessmentRepository(session)


def get_assessment_service(session: Session = Depends(get_db)):
    """Proveedor de dependencias para el servicio de evaluaciones diagnósticas."""
    from modules.assessments.service import AssessmentService
    return AssessmentService(repository=AssessmentRepository(session), session=session)
