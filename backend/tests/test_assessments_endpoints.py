import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import init_database
from auth.security import get_current_user
from models.schemas import UserResponse, UserRole


# Usuario de prueba autenticado existente en base de datos
MOCK_USER = UserResponse(
    id="usr_alumno_001",
    email="alumno.general@hospital.edu.ec",
    nombre="Dr. Alumno General",
    rol=UserRole.ALUMNO,
    tenant_id="tenant_default",
    terminos_aceptados=True
)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    init_database()
    # Override de la dependencia get_current_user en FastAPI
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield
    app.dependency_overrides.clear()


def test_full_formative_cycle_pre_test_plan_post_test_and_hake_gain():
    """
    Valida el ciclo formativo cerrado completo mediante la API REST de FastAPI:
    1. Iniciar Pre-Test diagnóstico.
    2. Enviar respuestas del Pre-Test con omisiones clínicas deliberadas.
    3. Verificar la generación automática del Plan de Estudio Prescriptivo.
    4. Consultar el plan y completar una de sus tareas formativas dosificadas.
    5. Iniciar Post-Test isomórfico paralelo asistido por IA.
    6. Enviar respuestas mejoradas al Post-Test y verificar el cálculo de Ganancia de Hake (g).
    7. Consultar el historial longitudinal del estudiante.
    """
    client = TestClient(app)

    # 1. Iniciar Pre-Test
    start_resp = client.post("/api/assessments/pre-test/start", json={"specialty_scope": "Ginecología y Obstetricia", "num_cases": 2})
    assert start_resp.status_code == 201, start_resp.text
    pre_test_data = start_resp.json()
    pre_test_id = pre_test_data["id"]
    assert pre_test_data["assessment_type"] == "pre_test"
    assert pre_test_data["status"] == "in_progress"
    assert len(pre_test_data["items"]) >= 2

    # 2. Enviar respuestas del Pre-Test con omisión clínica
    items = pre_test_data["items"]
    submit_payload = {
        "assessment_id": pre_test_id,
        "answers": [
            {
                "item_id": items[0]["id"],
                "student_answer": "Indico reposo absoluto y analgésicos comunes para el dolor de cabeza."
            },
            {
                "item_id": items[1]["id"],
                "student_answer": "Monitoreo fetal continuo y control de diuresis horaria."
            }
        ]
    }
    submit_pre_resp = client.post(f"/api/assessments/{pre_test_id}/submit", json=submit_payload)
    assert submit_pre_resp.status_code == 200, submit_pre_resp.text
    pre_report = submit_pre_resp.json()
    assert pre_report["assessment_type"] == "pre_test"
    pre_score = pre_report["score_total"]
    assert pre_score < 7.0, "El pre-test con omisiones debe tener calificación formativa inicial moderada o baja"

    # 3. Consultar Plan de Estudio Prescriptivo autogenerado
    plan_resp = client.get("/api/study-plans/me")
    assert plan_resp.status_code == 200, plan_resp.text
    active_plan = plan_resp.json()
    assert active_plan is not None
    assert active_plan["user_id"] == MOCK_USER.id
    assert active_plan["source_assessment_id"] == pre_test_id
    assert active_plan["status"] == "active"
    assert len(active_plan["tasks"]) >= 3

    # 4. Completar primera tarea formativa del plan
    first_task = active_plan["tasks"][0]
    task_id = first_task["id"]
    complete_task_resp = client.post(f"/api/study-plans/tasks/{task_id}/complete")
    assert complete_task_resp.status_code == 200, complete_task_resp.text
    task_res = complete_task_resp.json()
    assert task_res["is_completed"] is True
    assert task_res["progress_percentage"] > 0.0

    # 5. Iniciar Post-Test Isomórfico vinculado al Pre-Test
    post_start_resp = client.post("/api/assessments/post-test/start", json={"pre_test_id": pre_test_id})
    assert post_start_resp.status_code == 201, post_start_resp.text
    post_test_data = post_start_resp.json()
    post_test_id = post_test_data["id"]
    assert post_test_data["assessment_type"] == "post_test"
    assert post_test_data["related_assessment_id"] == pre_test_id
    assert len(post_test_data["items"]) >= 2

    # 6. Enviar respuestas óptimas al Post-Test aplicando las guías normadas del MSP
    post_items = post_test_data["items"]
    post_submit_payload = {
        "assessment_id": post_test_id,
        "answers": [
            {
                "item_id": post_items[0]["id"],
                "student_answer": (
                    "Diagnóstico: Preeclampsia con Criterios de Severidad. "
                    "Inicio inmediato de neuroprotección con Sulfato de Magnesio bajo esquema Zuspan "
                    "(impregnación 4g IV en 20 minutos y mantenimiento 1g/h en infusión continua). "
                    "Manejo de crisis hipertensiva con Hidralazina o Nifedipino según GPC MSP."
                )
            },
            {
                "item_id": post_items[1]["id"],
                "student_answer": (
                    "Activación del Código Rojo Obstétrico. Maniobra bimanual uterina y administración "
                    "inmediata de Oxitocina normada de primera línea según GPC de Hemorragia Posparto."
                )
            }
        ]
    }
    submit_post_resp = client.post(f"/api/assessments/{post_test_id}/submit", json=post_submit_payload)
    assert submit_post_resp.status_code == 200, submit_post_resp.text
    post_report = submit_post_resp.json()
    assert post_report["assessment_type"] == "post_test"
    post_score = post_report["score_total"]
    assert post_score > pre_score, "El puntaje del Post-Test debe superar al Pre-Test tras el estudio"

    # Validar Ganancia de Hake (g)
    hake_g = post_report["hake_gain_g"]
    assert hake_g is not None
    assert hake_g > 0.0
    assert "Ganancia" in (post_report["hake_category"] or "")

    # 7. Consultar Historial Longitudinal
    history_resp = client.get("/api/assessments/history/me")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 2
    assessment_ids = [a["id"] for a in history]
    assert pre_test_id in assessment_ids
    assert post_test_id in assessment_ids
