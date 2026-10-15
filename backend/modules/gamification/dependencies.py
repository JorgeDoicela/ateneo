from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.gamification.repository import GamificationRepository
from modules.gamification.service import GamificationService


def get_gamification_repository(db: Session = Depends(get_db)) -> GamificationRepository:
    return GamificationRepository(db)


def get_gamification_service(
    repo: GamificationRepository = Depends(get_gamification_repository),
    db: Session = Depends(get_db)
) -> GamificationService:
    return GamificationService(repository=repo, session=db)
