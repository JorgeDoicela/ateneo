from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, func
from core.database import Base, SafeDateTime


class TenantModel(Base):
    """
    Entidad relacional persistida de Institución / Tenant (Universidad, Hospital o Red de Salud).
    Agnóstica de motor (SQLite en desarrollo con modo WAL / PostgreSQL en producción).
    Permite particionado lógico y gobernanza multi-institucional.
    """
    __tablename__ = "tenants"

    id = Column(String(50), primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre_institucional = Column(String(200), nullable=False)
    dominio_email = Column(String(100), nullable=False, index=True)
    gpc_activas_json = Column(Text, nullable=False, default="[]")
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(SafeDateTime, server_default=func.now(), nullable=False)
    updated_at = Column(SafeDateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class UserModel(Base):
    """
    Entidad relacional persistida de usuarios e identidades del sistema Ateneo+.
    Agnóstica de motor (SQLite en desarrollo con modo WAL / PostgreSQL en producción).
    """
    __tablename__ = "users"

    id = Column(String(100), primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    rol = Column(String(50), nullable=False, default="alumno")
    hashed_password = Column(String(255), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    tenant_id = Column(
        String(50),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        default="tenant_default",
        server_default="tenant_default",
        index=True
    )
    last_login_at = Column(SafeDateTime, nullable=True)
    login_count = Column(Integer, nullable=False, default=0, server_default="0")
    failed_login_attempts = Column(Integer, nullable=False, default=0, server_default="0")
    locked_until = Column(SafeDateTime, nullable=True)
    email_verified = Column(Boolean, nullable=False, default=False, server_default="0")
    created_at = Column(SafeDateTime, server_default=func.now(), nullable=False)


class UserSessionModel(Base):
    """
    Entidad persistida para el control y revocación de sesiones activas (Token Blacklist / JTI).
    Garantiza el cierre de sesión real y rastreo de accesos concurrentes por IP y User-Agent.
    """
    __tablename__ = "user_sessions"

    id = Column(String(64), primary_key=True, index=True)  # Claim criptográfico JTI (UUID v4)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(50), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    is_revoked = Column(Boolean, nullable=False, default=False, server_default="0", index=True)
    expires_at = Column(SafeDateTime, nullable=False)
    created_at = Column(SafeDateTime, server_default=func.now(), nullable=False)

