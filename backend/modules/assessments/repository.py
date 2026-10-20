import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from modules.assessments.models import DiagnosticAssessmentModel, DiagnosticItemModel

logger = logging.getLogger(__name__)


class AssessmentRepository:
    """
    Repositorio de persistencia relacional para el subsistema de evaluaciones diagnósticas (Pre/Post-Test).
    """
    def __init__(self, session: Session):
        self.session = session

    def create_assessment(self, assessment: DiagnosticAssessmentModel) -> DiagnosticAssessmentModel:
        self.session.add(assessment)
        self.session.flush()
        return assessment

    def get_assessment_by_id(self, assessment_id: str) -> Optional[DiagnosticAssessmentModel]:
        stmt = select(DiagnosticAssessmentModel).where(DiagnosticAssessmentModel.id == assessment_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_user_assessments(
        self,
        user_id: str,
        assessment_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[DiagnosticAssessmentModel]:
        conditions = [DiagnosticAssessmentModel.user_id == user_id]
        if assessment_type:
            conditions.append(DiagnosticAssessmentModel.assessment_type == assessment_type)
        if status:
            conditions.append(DiagnosticAssessmentModel.status == status)

        stmt = (
            select(DiagnosticAssessmentModel)
            .where(and_(*conditions))
            .order_by(desc(DiagnosticAssessmentModel.started_at))
        )
        return list(self.session.execute(stmt).scalars().all())

    def update_assessment(self, assessment: DiagnosticAssessmentModel) -> DiagnosticAssessmentModel:
        self.session.merge(assessment)
        self.session.flush()
        return assessment

    def add_item(self, item: DiagnosticItemModel) -> DiagnosticItemModel:
        self.session.add(item)
        self.session.flush()
        return item

    def get_assessment_items(self, assessment_id: str) -> List[DiagnosticItemModel]:
        stmt = (
            select(DiagnosticItemModel)
            .where(DiagnosticItemModel.assessment_id == assessment_id)
            .order_by(DiagnosticItemModel.id.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_latest_pre_test(self, user_id: str) -> Optional[DiagnosticAssessmentModel]:
        stmt = (
            select(DiagnosticAssessmentModel)
            .where(
                and_(
                    DiagnosticAssessmentModel.user_id == user_id,
                    DiagnosticAssessmentModel.assessment_type == "pre_test",
                    DiagnosticAssessmentModel.status == "completed"
                )
            )
            .order_by(desc(DiagnosticAssessmentModel.completed_at))
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()
