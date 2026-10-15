import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.auth.models import UserModel, TenantModel
from modules.gamification.models import (
    AchievementDefinitionModel,
    StudentGamificationProfileModel,
    StudentUnlockedAchievementModel
)
from modules.gamification.repository import GamificationRepository
from modules.gamification.service import GamificationService, CAREER_LEVELS


@pytest.fixture
def db_session():
    """Sesión SQLite en memoria aislada para pruebas de persistencia."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    # Tenant de prueba
    test_tenant = TenantModel(
        id="tenant_default",
        codigo="ateneo_central",
        nombre_institucional="Ateneo+ Sede Central",
        dominio_email="ateneo.edu.ec"
    )
    session.add(test_tenant)
    session.commit()

    # Usuario de prueba
    test_user = UserModel(
        id="usr_test_student",
        email="test_student@ateneo.edu.ec",
        nombre="Estudiante de Prueba",
        hashed_password="fakehashedpassword",
        rol="alumno",
        tenant_id="tenant_default"
    )
    session.add(test_user)

    # Catálogo canónico de prueba
    defs = [
        AchievementDefinitionModel(id="iniciacion_clinica", codigo="ACH_INIT_01", titulo="Iniciación Clínica", descripcion="Completar la primera simulación.", categoria="diagnostico", icono="Stethoscope", puntos_xp=50, criterio_tipo="cases_completed", criterio_valor=1.0, activo=True),
        AchievementDefinitionModel(id="apego_gpc_excelente", codigo="ACH_GPC_02", titulo="Apego Normativo Estricto", descripcion="Obtener nota >= 9.0.", categoria="excelencia", icono="Award", puntos_xp=100, criterio_tipo="score_threshold", criterio_valor=9.0, activo=True),
        AchievementDefinitionModel(id="maestria_secuencial", codigo="ACH_PHASE_03", titulo="Maestría Secuencial", descripcion="Fases completadas.", categoria="fases", icono="Layers", puntos_xp=75, criterio_tipo="phases_completed", criterio_valor=1.0, activo=True),
        AchievementDefinitionModel(id="eficiencia_urgencias", codigo="ACH_TIME_06", titulo="Eficiencia en Urgencias", descripcion="Tiempo rápido.", categoria="agilidad", icono="Zap", puntos_xp=90, criterio_tipo="time_efficiency", criterio_valor=1.0, activo=True),
    ]
    session.add_all(defs)
    session.commit()

    yield session
    session.close()


def test_level_calculation_ranges():
    """Valida la escala de progresión de niveles de carrera médica."""
    # Nivel 1: 0 - 299 XP
    lvl1 = GamificationService.get_level_info_for_xp(150)
    assert lvl1["level"] == 1
    assert lvl1["title"] == "Estudiante Clínico Inicial"
    assert lvl1["needed_for_next"] == 300
    assert lvl1["percentage"] == 50.0

    # Nivel 2: 300 - 699 XP
    lvl2 = GamificationService.get_level_info_for_xp(300)
    assert lvl2["level"] == 2
    assert lvl2["title"] == "Externo de Medicina"

    # Nivel 5: 2100+ XP
    lvl5 = GamificationService.get_level_info_for_xp(3500)
    assert lvl5["level"] == 5
    assert lvl5["title"] == "Residente Clínico de Honor"
    assert lvl5["percentage"] == 100.0


def test_gamification_profile_initialization(db_session):
    """Valida que un estudiante sin actividad inicie en Nivel 1 con 0 XP."""
    repo = GamificationRepository(db_session)
    service = GamificationService(repo, db_session)

    profile = service.get_student_profile("usr_test_student")
    assert profile.user_id == "usr_test_student"
    assert profile.puntos_xp == 0
    assert profile.nivel_actual == 1
    assert profile.titulo_rango == "Estudiante Clínico Inicial"
    assert profile.total_logros_desbloqueados == 0
    assert profile.total_logros_disponibles == 4


def test_process_evaluation_event_unlocks_achievements(db_session):
    """Valida el cálculo de XP y el desbloqueo de hitos clínicos tras un caso exitoso."""
    repo = GamificationRepository(db_session)
    service = GamificationService(repo, db_session)

    # Simular evaluación con score 9.5
    result = service.process_evaluation_event(
        user_id="usr_test_student",
        case_id="case_hta_01",
        score=9.5,
        faithfulness_score=0.90,
        tiempo_segundos=180.0,
        es_fases=True,
        especialidad="Medicina Interna",
        es_emergencia=False
    )

    # Total evento = 200 XP
    # Hitos desbloqueados (4): Iniciación (+50), Apego (+100), Fases (+75), Urgencias (+90) = +315 XP
    # Total perfil = 515 XP -> Sube a Nivel 2 (Externo de Medicina)
    assert result.xp_ganados == 200
    assert len(result.nuevos_logros_desbloqueados) == 4
    assert result.subio_nivel is True
    assert result.nuevo_nivel == 2
    assert result.nuevo_rango == "Externo de Medicina"

    # Verificar perfil actualizado
    updated_profile = service.get_student_profile("usr_test_student")
    assert updated_profile.puntos_xp == 515
    assert updated_profile.nivel_actual == 2
    assert updated_profile.casos_resueltos == 1
    assert updated_profile.total_logros_desbloqueados == 4


def test_idempotent_achievement_unlock(db_session):
    """Valida que un hito clínico ya desbloqueado no duplique registros ni sume XP doble."""
    repo = GamificationRepository(db_session)
    service = GamificationService(repo, db_session)

    # Primera evaluación
    res1 = service.process_evaluation_event(
        user_id="usr_test_student",
        case_id="case_01",
        score=9.2
    )
    assert len(res1.nuevos_logros_desbloqueados) == 2

    # Segunda evaluación idéntica
    res2 = service.process_evaluation_event(
        user_id="usr_test_student",
        case_id="case_02",
        score=9.5
    )
    # No deben duplicarse los hitos ya ganados
    assert len(res2.nuevos_logros_desbloqueados) == 0
