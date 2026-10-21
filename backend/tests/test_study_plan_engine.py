import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uuid
import datetime
import pytest
from core.database import init_database
from core.unit_of_work import SqlAlchemyUnitOfWork
from modules.assessments.models import DiagnosticAssessmentModel, DiagnosticItemModel
from modules.study_plans.heuristic_engine import StudyPlanHeuristicEngine
from modules.study_plans.service import StudyPlanService


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_database()


def test_heuristic_omission_severity_classification():
    """Valida la clasificación determinística de riesgo y severidad de las omisiones."""
    weight_crit, label_crit = StudyPlanHeuristicEngine.evaluate_omission_severity("Omisión de dosis de carga de Sulfato de Magnesio")
    assert weight_crit == 3.0
    assert "Crítica" in label_crit

    weight_high, label_high = StudyPlanHeuristicEngine.evaluate_omission_severity("Falta de descarte de diagnóstico diferencial y proteinuria")
    assert weight_high == 2.0
    assert "Alta" in label_high

    weight_mod, label_mod = StudyPlanHeuristicEngine.evaluate_omission_severity("No se indican pautas de seguimiento ambulatorio y prevención")
    assert weight_mod == 1.0
    assert "Moderada" in label_mod


def test_heuristic_engine_synthesizes_plan_with_zdp_and_gpc():
    """Valida la síntesis de un plan prescriptivo con lecturas GPC y casos en ZDP."""
    items = [
        {
            "prompt_text": "Paciente con preeclampsia y criterios de severidad.",
            "case_id": "case_preeclampsia_01",
            "omisiones": ["Omisión de esquema de impregnación con Sulfato de Magnesio MSP"]
        },
        {
            "prompt_text": "Recién nacido con signos de sepsis neonatal temprana.",
            "case_id": "case_sepsis_neonatal_01",
            "omisiones": ["Falta de inicio oportuno de antibioticoterapia empírica"]
        }
    ]
    knowledge_state = {
        "semiologia_anamnesis": 0.80,
        "diagnostico_final": 0.65,
        "plan_terapeutico_msp": 0.35,  # Deficitaria
        "examenes_complementarios": 0.50
    }

    plan_data = StudyPlanHeuristicEngine.synthesize_prescriptive_plan(items, knowledge_state)

    assert "tasks" in plan_data
    assert len(plan_data["tasks"]) >= 3
    task_types = [t["task_type"] for t in plan_data["tasks"]]
    assert "gpc_reading" in task_types
    assert "case_simulation" in task_types
    assert "socratic_review" in task_types

    # Verificar que el resumen mencione las brechas detectadas
    assert "brechas clínicas" in plan_data["diagnosis_summary"]
    assert plan_data["target_duration_days"] == 7


def test_study_plan_service_lifecycle_in_database():
    """Valida el ciclo de vida completo del servicio de planes en la base de datos relacional."""
    uow = SqlAlchemyUnitOfWork()
    user_id = "usr_alumno_001"
    pre_test_id = f"eval_pre_{uuid.uuid4().hex[:8]}"

    # 1. Crear Pre-Test en base de datos
    with uow:
        pre_test = DiagnosticAssessmentModel(
            id=pre_test_id,
            user_id=user_id,
            assessment_type="pre_test",
            specialty_scope="Ginecología y Obstetricia",
            score_total=5.0,
            score_max=10.0,
            status="completed",
            started_at=datetime.datetime.now(datetime.timezone.utc),
            completed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        uow.assessments.create_assessment(pre_test)

        item = DiagnosticItemModel(
            assessment_id=pre_test_id,
            case_id="case_preeclampsia_01",
            prompt_text="Gestante con hipertensión severa en labor de parto.",
            student_answer="Indico reposo y monitoreo fetal.",
            score_obtained=5.0,
            omisiones_json='["Omisión de impregnación con Sulfato de Magnesio según GPC MSP"]',
            competencias_json='[{"eje": "tratamiento", "competencia": "plan_terapeutico_msp"}]'
        )
        uow.assessments.add_item(item)
        uow.commit()

    # 2. Generar plan prescriptivo mediante el servicio
    service = StudyPlanService()
    created_plan = service.generate_plan_from_assessment(pre_test_id, user_id)

    assert created_plan is not None
    assert created_plan.user_id == user_id
    assert created_plan.source_assessment_id == pre_test_id
    assert created_plan.status == "active"
    assert created_plan.progress_percentage == 0.0
    assert len(created_plan.tasks) >= 3

    # 3. Consultar plan activo
    active_plan = service.get_active_plan(user_id)
    assert active_plan is not None
    assert active_plan.id == created_plan.id

    # 4. Completar tareas una por una y verificar progreso
    tasks = created_plan.tasks
    first_task = tasks[0]
    res_step1 = service.complete_task(first_task.id, user_id)
    assert res_step1.is_completed is True
    assert res_step1.progress_percentage > 0.0
    assert res_step1.plan_completed is False

    # Completar el resto de tareas
    for t in tasks[1:]:
        service.complete_task(t.id, user_id)

    # Verificar que el plan haya alcanzado 100% y estatus 'completed'
    plan_final = service.get_plan_details(created_plan.id, user_id)
    assert plan_final.progress_percentage == 100.0
    assert plan_final.status == "completed"
    assert plan_final.completed_at is not None


def test_heuristic_engine_synthesizes_post_test_mastery_plan():
    """Valida la síntesis de un plan de consolidación y maestría tras completar el Post-Test."""
    items = [
        {
            "prompt_text": "Paciente con preeclampsia y criterios de severidad.",
            "case_id": "case_preeclampsia_01",
            "omisiones": []  # Sin omisiones críticas en el post-test
        }
    ]
    knowledge_state = {
        "semiologia_anamnesis": 0.90,
        "diagnostico_final": 0.85,
        "plan_terapeutico_msp": 0.80,
        "examenes_complementarios": 0.85
    }

    plan_data = StudyPlanHeuristicEngine.synthesize_prescriptive_plan(
        assessment_items=items,
        knowledge_state=knowledge_state,
        assessment_type="post_test",
        hake_gain_g=0.75
    )

    assert "tasks" in plan_data
    assert len(plan_data["tasks"]) >= 3
    assert "Consolidación" in plan_data["title"] or "Maestría" in plan_data["title"]
    assert "0.75" in plan_data["title"]
    assert "Alto Rendimiento" in plan_data["diagnosis_summary"] or "sobresaliente" in plan_data["diagnosis_summary"].lower()

    task_types = [t["task_type"] for t in plan_data["tasks"]]
    assert "gpc_reading" in task_types
    assert "case_simulation" in task_types
    assert "socratic_review" in task_types


def test_post_test_study_plan_lifecycle_in_database():
    """Valida que un Post-Test completado persista un plan de maestría y archive el anterior."""
    uow = SqlAlchemyUnitOfWork()
    user_id = "usr_alumno_001"
    post_test_id = f"eval_post_{uuid.uuid4().hex[:8]}"

    with uow:
        post_test = DiagnosticAssessmentModel(
            id=post_test_id,
            user_id=user_id,
            assessment_type="post_test",
            specialty_scope="Troncal General CACES",
            score_total=9.5,
            score_max=10.0,
            hake_gain_g=0.82,
            status="completed",
            started_at=datetime.datetime.now(datetime.timezone.utc),
            completed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        uow.assessments.create_assessment(post_test)

        item = DiagnosticItemModel(
            assessment_id=post_test_id,
            case_id="case_preeclampsia_01",
            prompt_text="Gestante con hipertensión severa en labor de parto.",
            student_answer="Indico impregnación con Sulfato de Magnesio e Hidralazina según GPC MSP.",
            score_obtained=9.5,
            omisiones_json='[]',
            competencias_json='[{"eje": "tratamiento", "competencia": "plan_terapeutico_msp"}]'
        )
        uow.assessments.add_item(item)
        uow.commit()

    service = StudyPlanService()
    mastery_plan = service.generate_plan_from_assessment(post_test_id, user_id)

    assert mastery_plan is not None
    assert mastery_plan.user_id == user_id
    assert mastery_plan.source_assessment_id == post_test_id
    assert mastery_plan.status == "active"
    assert "Consolidación" in mastery_plan.title or "Maestría" in mastery_plan.title
    assert len(mastery_plan.tasks) >= 3

    active = service.get_active_plan(user_id)
    assert active is not None
    assert active.id == mastery_plan.id

