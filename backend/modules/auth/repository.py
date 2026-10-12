from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from modules.auth.models import UserModel, TenantModel, UserSessionModel, MagicLinkTokenModel


class TenantRepository:
    """
    Repositorio de persistencia relacional para Instituciones / Tenants.
    Permite administrar facultades, hospitales y redes de salud con particionado lógico.
    """
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        return self.db.query(func.count(TenantModel.id)).scalar() or 0

    def get_by_id(self, tenant_id: str) -> Optional[TenantModel]:
        return self.db.query(TenantModel).filter(TenantModel.id == tenant_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[TenantModel]:
        return self.db.query(TenantModel).filter(TenantModel.codigo == codigo.strip().lower()).first()

    def get_by_dominio(self, dominio: str) -> Optional[TenantModel]:
        return self.db.query(TenantModel).filter(TenantModel.dominio_email == dominio.strip().lower()).first()

    def get_all(self, solo_activos: bool = False) -> List[TenantModel]:
        query = self.db.query(TenantModel)
        if solo_activos:
            query = query.filter(TenantModel.activo == True)
        return query.all()

    def create(self, tenant: TenantModel, commit: bool = True) -> TenantModel:
        self.db.add(tenant)
        if commit:
            self.db.commit()
            self.db.refresh(tenant)
        else:
            self.db.flush()
        return tenant

    def update(self, tenant: TenantModel, commit: bool = True) -> TenantModel:
        if commit:
            self.db.commit()
            self.db.refresh(tenant)
        else:
            self.db.flush()
        return tenant



class UserRepository:
    """
    Repositorio de persistencia relacional para usuarios e identidades.
    Aísla las consultas SQL de la lógica de negocio de autenticación y soporta
    filtrado por tenant institucional.
    """
    def __init__(self, db: Session):
        self.db = db

    def count(self, tenant_id: Optional[str] = None) -> int:
        query = self.db.query(func.count(UserModel.id))
        if tenant_id:
            query = query.filter(UserModel.tenant_id == tenant_id)
        return query.scalar() or 0

    def get_by_id(self, user_id: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email.strip().lower()).first()

    def get_all(self, tenant_id: Optional[str] = None) -> List[UserModel]:
        query = self.db.query(UserModel)
        if tenant_id:
            query = query.filter(UserModel.tenant_id == tenant_id)
        return query.all()

    def get_by_tenant(self, tenant_id: str) -> List[UserModel]:
        return self.db.query(UserModel).filter(UserModel.tenant_id == tenant_id).all()

    def create(self, user: UserModel, commit: bool = True) -> UserModel:
        self.db.add(user)
        if commit:
            self.db.commit()
            self.db.refresh(user)
        else:
            self.db.flush()
        return user

    def update(self, user: UserModel, commit: bool = True) -> UserModel:
        if commit:
            self.db.commit()
            self.db.refresh(user)
        else:
            self.db.flush()
        return user


class UserSessionRepository:
    """
    Repositorio relacional para ciclo de vida de sesiones activas y lista negra de tokens JWT (JTI).
    Permite auditar accesos concurrentes, revocación inmediata en logout y control de sesiones por usuario.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, session: UserSessionModel, commit: bool = True) -> UserSessionModel:
        self.db.add(session)
        if commit:
            self.db.commit()
            self.db.refresh(session)
        else:
            self.db.flush()
        return session

    def get_by_jti(self, jti: str) -> Optional[UserSessionModel]:
        return self.db.query(UserSessionModel).filter(UserSessionModel.id == jti).first()

    def revoke(self, jti: str, commit: bool = True) -> bool:
        session = self.get_by_jti(jti)
        if not session:
            return False
        session.is_revoked = True
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        return True

    def is_jti_revoked(self, jti: str) -> bool:
        session = self.get_by_jti(jti)
        if not session:
            return False
        return bool(session.is_revoked)

    def list_active_by_user(self, user_id: str) -> List[UserSessionModel]:
        return (
            self.db.query(UserSessionModel)
            .filter(
                UserSessionModel.user_id == user_id,
                UserSessionModel.is_revoked == False
            )
            .all()
        )

    def revoke_all_for_user(self, user_id: str, commit: bool = True) -> int:
        """Invalida masivamente todas las sesiones activas de un usuario ante cambio de credenciales o bloqueo."""
        count = (
            self.db.query(UserSessionModel)
            .filter(
                UserSessionModel.user_id == user_id,
                UserSessionModel.is_revoked == False
            )
            .update({"is_revoked": True})
        )
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        return count


class MagicLinkRepository:
    """
    Repositorio relacional para la emisión, consulta y revocación de Magic Links e Invitaciones.
    Busca estrictamente por token_hash para salvaguardar la confidencialidad de los enlaces.
    """
    def __init__(self, db: Session):
        self.db = db

    def create(self, link: MagicLinkTokenModel, commit: bool = True) -> MagicLinkTokenModel:
        self.db.add(link)
        if commit:
            self.db.commit()
            self.db.refresh(link)
        else:
            self.db.flush()
        return link

    def get_by_id(self, link_id: str) -> Optional[MagicLinkTokenModel]:
        return self.db.query(MagicLinkTokenModel).filter(MagicLinkTokenModel.id == link_id).first()

    def get_by_hash(self, token_hash: str) -> Optional[MagicLinkTokenModel]:
        return self.db.query(MagicLinkTokenModel).filter(MagicLinkTokenModel.token_hash == token_hash).first()

    def list_by_tenant(
        self, 
        tenant_id: str, 
        limit: int = 100, 
        include_revoked: bool = True
    ) -> List[MagicLinkTokenModel]:
        query = self.db.query(MagicLinkTokenModel).filter(MagicLinkTokenModel.tenant_id == tenant_id)
        if not include_revoked:
            query = query.filter(MagicLinkTokenModel.is_revoked == False)
        return query.order_by(MagicLinkTokenModel.created_at.desc()).limit(limit).all()

    def revoke(self, link_id: str, commit: bool = True) -> bool:
        link = self.get_by_id(link_id)
        if not link:
            return False
        link.is_revoked = True
        if commit:
            self.db.commit()
        else:
            self.db.flush()
        return True

    def update(self, link: MagicLinkTokenModel, commit: bool = True) -> MagicLinkTokenModel:
        if commit:
            self.db.commit()
            self.db.refresh(link)
        else:
            self.db.flush()
        return link





