import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from core.config import settings

# Configuración del motor según el dialecto de base de datos
engine_kwargs = {}

if settings.is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Optimización para PostgreSQL u otros motores en producción
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(settings.database_url, **engine_kwargs)

# Si es SQLite, activar modo WAL (Write-Ahead Logging) para máxima concurrencia
if settings.is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
        except Exception:
            cursor.execute("PRAGMA journal_mode=DELETE")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

import datetime
from sqlalchemy import TypeDecorator, DateTime

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SafeDateTime(TypeDecorator):
    """
    Tipo DateTime robusto y agnóstico de motor (SQLite WAL / PostgreSQL).
    Garantiza compatibilidad estricta con DateTime(timezone=True) de SQLAlchemy
    mientras acepta objetos datetime nativos o cadenas ISO-8601 defensivamente.
    """
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.datetime.fromisoformat(value)
            except Exception:
                return datetime.datetime.now(datetime.timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        return value


def get_db() -> Generator[Session, None, None]:
    """
    Generador de sesión transaccional para inyección de dependencias con FastAPI.
    Garantiza el cierre seguro y rollback automático ante excepciones no controladas.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


from contextlib import contextmanager


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager seguro para scripts, tareas asíncronas en background o servicios.
    Garantiza rollback automático ante fallos y cierre seguro de la conexión.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_database() -> None:
    """Crea todas las tablas declaradas en los modelos si aún no existen y siembra datos iniciales."""
    import json
    # Importar entidades para registrar sus esquemas en Base.metadata
    from modules.auth.models import UserModel, TenantModel, UserSessionModel, MagicLinkTokenModel
    from modules.analytics_history.models import EvaluationHistoryModel
    from modules.collaboration.models import AteneoRoomModel
    from modules.adaptive.models import StudentMasteryModel, StudentSnapshotModel
    from modules.cases.models import ClinicalCaseModel

    Base.metadata.create_all(bind=engine)

    # Siembra defensiva e idempotente de tenant por defecto y usuarios institucionales
    with SessionLocal() as db:
        from modules.auth.repository import UserRepository, TenantRepository
        from modules.auth.service import AuthService
        tenant_repo = TenantRepository(db)
        # Siembra defensiva e idempotente de tenants institucionales
        default_tenants = [
            {
                "id": "tenant_default",
                "codigo": "ateneo_central",
                "nombre_institucional": "Ateneo+ Sede Central (MSP Ecuador)",
                "dominio_email": "ateneo.edu.ec",
                "gpc": ["GPC_Hipertension_Arterial_MSP_2019", "GPC_Diabetes_Mellitus_Tipo_2_MSP_2017", "GPC_Neumonia_Adquirida_Comunidad_Pediatria_MSP_2019"]
            },
            {
                "id": "tenant_uce",
                "codigo": "uce",
                "nombre_institucional": "Universidad Central del Ecuador (Facultad de Ciencias Médicas)",
                "dominio_email": "uce.edu.ec",
                "gpc": ["GPC_Hipertension_Arterial_MSP_2019", "GPC_Diabetes_Mellitus_Tipo_2_MSP_2017"]
            },
            {
                "id": "tenant_usfq",
                "codigo": "usfq",
                "nombre_institucional": "Universidad San Francisco de Quito (Colegio de Ciencias de la Salud)",
                "dominio_email": "usfq.edu.ec",
                "gpc": ["GPC_Hipertension_Arterial_MSP_2019", "GPC_Diabetes_Mellitus_Tipo_2_MSP_2017"]
            }
        ]
        for t_data in default_tenants:
            if not tenant_repo.get_by_id(t_data["id"]):
                tenant_repo.create(TenantModel(
                    id=t_data["id"],
                    codigo=t_data["codigo"],
                    nombre_institucional=t_data["nombre_institucional"],
                    dominio_email=t_data["dominio_email"],
                    gpc_activas_json=json.dumps(t_data["gpc"], ensure_ascii=False),
                    activo=True
                ))

        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo, tenant_repo)
        auth_service.seed_demo_users_if_needed()

