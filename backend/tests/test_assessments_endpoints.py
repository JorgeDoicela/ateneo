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

    # Validar que el Post-Test autogeneró el nuevo Plan de Consolidación y Maestría Clínica
    post_plan_resp = client.get("/api/study-plans/me")
    assert post_plan_resp.status_code == 200, post_plan_resp.text
    post_plan = post_plan_resp.json()
    assert post_plan is not None
    assert post_plan["source_assessment_id"] == post_test_id
    assert "Consolidación" in post_plan["title"] or "Maestría" in post_plan["title"]
    assert post_plan["status"] == "active"
    assert len(post_plan["tasks"]) >= 3

    # 7. Consultar Historial Longitudinal
    history_resp = client.get("/api/assessments/history/me")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 2
    assessment_ids = [a["id"] for a in history]
    assert pre_test_id in assessment_ids
    assert post_test_id in assessment_ids


def test_stratified_caces_pre_test_selection():
    """
    Valida psicométricamente que el inicio de Pre-Test por defecto:
    1. Seleccione 4 reactivos clínicos basales.
    2. Cada reactivo corresponda de forma no redundante a una de las 4 troncales CACES / MSP:
       - Ginecología y Obstetricia
       - Pediatría y Neonatología
       - Medicina Interna y Crónicos
       - Infectología y Salud Pública
    3. Garantice 25% de paridad por área troncal (balance 1:1:1:1) sin sesgo de representatividad.
    """
    from modules.assessments.service import CASE_TRONCAL_MAP, TRONCALES_CANONICAS

    client = TestClient(app)
    resp = client.post("/api/assessments/pre-test/start", json={})
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["assessment_type"] == "pre_test"
    assert data["specialty_scope"] == "Batería Troncal CACES (Multidisciplinar)"
    items = data["items"]
    assert len(items) == 4, f"Se esperaban 4 reactivos troncales, se obtuvieron {len(items)}"

    evaluated_troncales = set()
    for item in items:
        case_id = item["case_id"]
        troncal = CASE_TRONCAL_MAP.get(case_id)
        assert troncal is not None, f"El caso {case_id} no está catalogado en CASE_TRONCAL_MAP"
        assert troncal in TRONCALES_CANONICAS, f"Troncal {troncal} no es una de las 4 canónicas CACES"
        assert troncal not in evaluated_troncales, f"Troncal {troncal} repetida en el Pre-Test estratificado"
        evaluated_troncales.add(troncal)

    assert evaluated_troncales == set(TRONCALES_CANONICAS), "El Pre-Test no cubrió la totalidad de las 4 troncales CACES"


def test_full_caces_stratified_cycle_with_isomorphic_battery_and_hake_gain():
    """
    Valida el ciclo de investigación cerrado bajo el estándar CACES / MSP:
    1. Pre-Test multidisciplinar estratificado (4 reactivos, 1 por troncal).
    2. Calificación basal con omisiones formativas.
    3. Síntesis y verificación del Plan de Estudio Prescriptivo.
    4. Post-Test isomórfico paralelo de 4 reactivos (isomorfismo 1:1 por troncal).
    5. Calificación mejorada del Post-Test y cálculo de Ganancia de Hake (g).
    """
    client = TestClient(app)

    # 1. Iniciar Pre-Test CACES por defecto
    start_resp = client.post("/api/assessments/pre-test/start", json={})
    assert start_resp.status_code == 201, start_resp.text
    pre_test = start_resp.json()
    pre_test_id = pre_test["id"]
    pre_items = pre_test["items"]
    assert len(pre_items) == 4

    # 2. Enviar respuestas basales con omisiones parciales
    pre_answers = []
    for it in pre_items:
        pre_answers.append({
            "item_id": it["id"],
            "student_answer": "Sospecho cuadro agudo, solicito biometría y observación en sala."
        })
    submit_pre_resp = client.post(f"/api/assessments/{pre_test_id}/submit", json={
        "assessment_id": pre_test_id,
        "answers": pre_answers
    })
    assert submit_pre_resp.status_code == 200, submit_pre_resp.text
    pre_report = submit_pre_resp.json()
    assert pre_report["assessment_type"] == "pre_test"
    pre_score = pre_report["score_total"]
    assert pre_score < 7.0, f"Calificación basal esperada < 7.0, se obtuvo {pre_score}"

    # 3. Verificar Plan Prescriptivo generado
    plan_resp = client.get("/api/study-plans/me")
    assert plan_resp.status_code == 200
    plan = plan_resp.json()
    assert plan is not None
    assert plan["source_assessment_id"] == pre_test_id
    assert len(plan["tasks"]) > 0

    # 4. Iniciar Post-Test Isomórfico paralelo
    start_post_resp = client.post("/api/assessments/post-test/start", json={"pre_test_id": pre_test_id})
    assert start_post_resp.status_code == 201, start_post_resp.text
    post_test = start_post_resp.json()
    post_test_id = post_test["id"]
    post_items = post_test["items"]
    assert len(post_items) == 4, f"Se esperaban 4 reactivos isomórficos paralelos, se obtuvieron {len(post_items)}"

    # Verificar que los reactivos del Post-Test tengan formato Markdown médico enriquecido
    for p_item in post_items:
        assert "###" in p_item["prompt_text"]
        assert "Área Troncal" in p_item["prompt_text"]

    # 5. Enviar respuestas optimizadas con evidencia de la GPC al Post-Test
    post_answers = []
    for p_it in post_items:
        prompt_low = p_it["prompt_text"].lower()
        if "preeclampsia" in prompt_low or "hipertens" in prompt_low:
            ans = "Preeclampsia severa. Neuroprotección con Sulfato de Magnesio esquema Zuspan e Hidralazina según GPC MSP."
        elif "asma" in prompt_low or "respirat" in prompt_low or "salbutamol" in prompt_low:
            ans = "Crisis asmática. Salbutamol inhalado más Corticoide sistémico y oxigenoterapia normada."
        elif "diabet" in prompt_low or "cetoacidosis" in prompt_low:
            ans = "Cetoacidosis diabética. Rehidratación con cristaloides e infusión continua de Insulina rápida."
        else:
            ans = "Manejo según GPC del MSP con Ceftriaxona o esquema antimicrobiano normado de primera línea."

        post_answers.append({
            "item_id": p_it["id"],
            "student_answer": ans
        })

    submit_post_resp = client.post(f"/api/assessments/{post_test_id}/submit", json={
        "assessment_id": post_test_id,
        "answers": post_answers
    })
    assert submit_post_resp.status_code == 200, submit_post_resp.text
    post_report = submit_post_resp.json()
    post_score = post_report["score_total"]
    assert post_score > pre_score, f"Post-Score {post_score} debe superar Pre-Score {pre_score}"

    # 6. Validar Ganancia de Hake (g)
    hake_g = post_report["hake_gain_g"]
    assert hake_g is not None
    assert hake_g > 0.0
    assert "Ganancia" in (post_report["hake_category"] or "")


