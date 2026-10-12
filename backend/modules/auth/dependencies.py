from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.repository import UserRepository, TenantRepository, UserSessionRepository, MagicLinkRepository
from modules.auth.service import AuthService


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_tenant_repository(db: Session = Depends(get_db)) -> TenantRepository:
    return TenantRepository(db)


def get_user_session_repository(db: Session = Depends(get_db)) -> UserSessionRepository:
    return UserSessionRepository(db)


def get_magic_link_repository(db: Session = Depends(get_db)) -> MagicLinkRepository:
    return MagicLinkRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
    session_repo: UserSessionRepository = Depends(get_user_session_repository),
    magic_link_repo: MagicLinkRepository = Depends(get_magic_link_repository)
) -> AuthService:
    return AuthService(
        repository=user_repo,
        tenant_repository=tenant_repo,
        session_repository=session_repo,
        magic_link_repository=magic_link_repo
    )

