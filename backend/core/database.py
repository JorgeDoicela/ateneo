import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from core.config import settings

# Configuración del motor según el dialecto de base de datos
engine_kwargs = {}

if settings.is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 60.0}
else:
    # Optimización para PostgreSQL u otros motores en producción
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(settings.database_url, **engine_kwargs)

# Si es SQLite, configurar journal_mode compatible con bind mounts y busy_timeout defensivo
if settings.is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        journal_mode = os.getenv("SQLITE_JOURNAL_MODE", "MEMORY").upper()
        try:
            cursor.execute(f"PRAGMA journal_mode={journal_mode}")
        except Exception:
            cursor.execute("PRAGMA journal_mode=MEMORY")
        cursor.execute("PRAGMA busy_timeout=60000")
        cursor.execute("PRAGMA synchronous=OFF")
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
    from modules.gamification.models import (
        AchievementDefinitionModel,
        StudentGamificationProfileModel,
        StudentUnlockedAchievementModel
    )

    Base.metadata.create_all(bind=engine)

    # Migración defensiva e idempotente de columnas para SQLite
    if settings.is_sqlite:
        from sqlalchemy import text
        with engine.connect() as conn:
            try:
                res = conn.execute(text("PRAGMA table_info(users)"))
                existing_cols = {row[1] for row in res.fetchall()}
                if "terminos_aceptados" not in existing_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN terminos_aceptados BOOLEAN DEFAULT 0 NOT NULL"))
                if "fecha_terminos_aceptados" not in existing_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN fecha_terminos_aceptados DATETIME"))
                if "version_terminos" not in existing_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN version_terminos VARCHAR(50) DEFAULT 'v1.0-investigacion-2026'"))
                conn.commit()
            except Exception:
                pass

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
                "nombre_institucional": "Ateneo+ Sede Central",
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
            existing_t = tenant_repo.get_by_id(t_data["id"])
            if not existing_t:
                tenant_repo.create(TenantModel(
                    id=t_data["id"],
                    codigo=t_data["codigo"],
                    nombre_institucional=t_data["nombre_institucional"],
                    dominio_email=t_data["dominio_email"],
                    gpc_activas_json=json.dumps(t_data["gpc"], ensure_ascii=False),
                    activo=True
                ))
            elif "(MSP Ecuador)" in existing_t.nombre_institucional:
                existing_t.nombre_institucional = existing_t.nombre_institucional.replace(" (MSP Ecuador)", "").strip()
                db.commit()

        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo, tenant_repo)
        auth_service.seed_demo_users_if_needed()

        # Siembra defensiva e idempotente de hitos clínicos canónicos
        default_achievements = [
            {
                "id": "iniciacion_clinica",
                "codigo": "ACH_INIT_01",
                "titulo": "Iniciación Clínica",
                "descripcion": "Completar la primera simulación diagnóstica con base en las Guías de Práctica Clínica del Ecuador.",
                "categoria": "diagnostico",
                "icono": "Stethoscope",
                "puntos_xp": 50,
                "criterio_tipo": "cases_completed",
                "criterio_valor": 1.0
            },
            {
                "id": "apego_gpc_excelente",
                "codigo": "ACH_GPC_02",
                "titulo": "Apego Normativo Estricto",
                "descripcion": "Obtener una calificación diagnóstica igual o superior a 9.0/10 con alta concordancia clínica formativa.",
                "categoria": "excelencia",
                "icono": "Award",
                "puntos_xp": 100,
                "criterio_tipo": "score_threshold",
                "criterio_valor": 9.0
            },
            {
                "id": "maestria_secuencial",
                "codigo": "ACH_PHASE_03",
                "titulo": "Maestría Secuencial",
                "descripcion": "Superar con éxito las tres fases secuenciales (Anamnesis, Paraclínicos y Manejo) en simulación dinámica.",
                "categoria": "fases",
                "icono": "Layers",
                "puntos_xp": 75,
                "criterio_tipo": "phases_completed",
                "criterio_valor": 1.0
            },
            {
                "id": "resolucion_multidisciplinar",
                "codigo": "ACH_SPEC_04",
                "titulo": "Resolución Multidisciplinar",
                "descripcion": "Resolver casos clínicos de al menos 3 especialidades o Guías de Práctica Clínica distintas.",
                "categoria": "especialidad",
                "icono": "Compass",
                "puntos_xp": 120,
                "criterio_tipo": "specialties_count",
                "criterio_valor": 3.0
            },
            {
                "id": "pensamiento_socratico",
                "codigo": "ACH_SOCRATIC_05",
                "titulo": "Pensamiento Crítico Socrático",
                "descripcion": "Participar activamente en un diálogo de debriefing socrático para aclarar y justificar omisiones clínicas.",
                "categoria": "dialogo",
                "icono": "MessageSquare",
                "puntos_xp": 60,
                "criterio_tipo": "socratic_debrief",
                "criterio_valor": 1.0
            },
            {
                "id": "eficiencia_urgencias",
                "codigo": "ACH_TIME_06",
                "titulo": "Eficiencia en Urgencias",
                "descripcion": "Emitir un juicio clínico acertado con calificación >= 8.5 en un tiempo menor o igual a 5 minutos.",
                "categoria": "agilidad",
                "icono": "Zap",
                "puntos_xp": 90,
                "criterio_tipo": "time_efficiency",
                "criterio_valor": 1.0
            },
            {
                "id": "constancia_formativa",
                "codigo": "ACH_COUNT_07",
                "titulo": "Constancia Formativa",
                "descripcion": "Resolver un acumulado de 5 casos clínicos completos dentro del simulador.",
                "categoria": "constancia",
                "icono": "ShieldCheck",
                "puntos_xp": 150,
                "criterio_tipo": "cases_completed",
                "criterio_valor": 5.0
            },
            {
                "id": "manejo_emergencias",
                "codigo": "ACH_EMERG_08",
                "titulo": "Manejo de Emergencias Críticas",
                "descripcion": "Resolver con éxito (nota >= 8.0) un caso clasificado como Código Rojo o urgencia obstétrica/cardiovascular.",
                "categoria": "emergencias",
                "icono": "AlertCircle",
                "puntos_xp": 110,
                "criterio_tipo": "emergency_case",
                "criterio_valor": 1.0
            }
        ]
        from modules.gamification.models import AchievementDefinitionModel, StudentGamificationProfileModel
        for ach in default_achievements:
            existing_ach = db.get(AchievementDefinitionModel, ach["id"])
            if not existing_ach:
                db.add(AchievementDefinitionModel(**ach))

        demo_profiles = [
            ("usr_alumno_001", "Estudiante Clínico Inicial"),
            ("usr_estudiante_002", "Estudiante Clínico Inicial"),
            ("usr_estudiante_003", "Estudiante Clínico Inicial"),
            ("usr_estudiante_004", "Estudiante Clínico Inicial"),
            ("usr_docente_001", "Docente de Medicina"),
            ("usr_admin_001", "Administrador Institucional")
        ]
        for uid, title in demo_profiles:
            existing_prof = db.get(StudentGamificationProfileModel, uid)
            if not existing_prof:
                db.add(StudentGamificationProfileModel(
                    user_id=uid,
                    puntos_xp=0,
                    nivel_actual=1,
                    titulo_rango=title,
                    casos_resueltos=0,
                    racha_dias=1,
                    ultimo_acceso_fecha=datetime.datetime.now(datetime.timezone.utc)
                ))
        db.commit()

