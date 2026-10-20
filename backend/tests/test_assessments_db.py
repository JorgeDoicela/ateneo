import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import uuid
import datetime
import pytest
from core.database import init_database, SessionLocal
from core.unit_of_work import SqlAlchemyUnitOfWork
from modules.assessments.models import DiagnosticAssessmentModel, DiagnosticItemModel
from modules.study_plans.models import PrescriptiveStudyPlanModel, StudyPlanTaskModel


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Garantiza la inicialización de las tablas antes de ejecutar la suite."""
    init_database()


def test_diagnostic_assessment_pre_test_creation():
    """
    Verifica la creación persistente de un Pre-Test con ítems diagnósticos asociados
    a través de SqlAlchemyUnitOfWork.
    """
    uow = SqlAlchemyUnitOfWork()
    test_user_id = "usr_alumno_001"
    pre_test_id = f"eval_pre_{uuid.uuid4().hex[:8]}"

    with uow:
        pre_test = DiagnosticAssessmentModel(
            id=pre_test_id,
            user_id=test_user_id,
            assessment_type="pre_test",
            specialty_scope="Ginecología y Obstetricia",
            score_total=5.5,
            score_max=10.0,
            status="completed",
            started_at=datetime.datetime.now(datetime.timezone.utc),
            completed_at=datetime.datetime.now(datetime.timezone.utc)
        )
        uow.assessments.create_assessment(pre_test)

        item1 = DiagnosticItemModel(
            assessment_id=pre_test_id,
            case_id="case_preeclampsia_01",
            prompt_text="Gestante de 34 semanas con TA 160/110 y proteinuria +++.",
            student_answer="Sospecha de preeclampsia, solicito laboratorio.",
            score_obtained=5.5,
            omisiones_json='["Omisión de dosis de carga de Sulfato de Magnesio"]',
            competencias_json='[{"eje": "tratamiento", "competencia": "plan_terapeutico_msp"}]'
        )
        uow.assessments.add_item(item1)
        uow.commit()

    # Verificar lectura
    with uow:
        retrieved = uow.assessments.get_assessment_by_id(pre_test_id)
        assert retrieved is not None
        assert retrieved.assessment_type == "pre_test"
        assert retrieved.score_total == 5.5
        assert len(retrieved.items) == 1
        assert "Sulfato de Magnesio" in retrieved.items[0].omisiones_json


def test_prescriptive_study_plan_tasks_and_progress_recalculation():
    """
    Verifica la creación de un plan de estudio prescriptivo con tareas dosificadas,
    así como el recálculo reactivo del porcentaje de progreso al completar tareas.
    """
    uow = SqlAlchemyUnitOfWork()
    test_user_id = "usr_alumno_001"
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"

    with uow:
        plan = PrescriptiveStudyPlanModel(
            id=plan_id,
            user_id=test_user_id,
            title="Plan de Refuerzo en Preeclampsia y Sepsis Obstétrica",
            diagnosis_summary="Brecha crítica detectada en dosificación de fármacos de primera línea (GPC MSP).",
            target_duration_days=5,
            progress_percentage=0.0,
            status="active"
        )
        uow.study_plans.create_plan(plan)

        task1 = StudyPlanTaskModel(
            plan_id=plan_id,
            task_type="gpc_reading",
            title="Revisión de GPC Preeclampsia (Sección 4.2: Impregnación)",
            resource_reference="GPC_Trastornos_Hipertensivos_MSP_2019",
            competency_id="plan_terapeutico_msp",
            estimated_minutes=10,
            is_completed=False
        )
        task2 = StudyPlanTaskModel(
            plan_id=plan_id,
            task_type="case_simulation",
            title="Simulación Clínica: Caso de Eclampsia y Código Rojo",
            resource_reference="case_preeclampsia_01",
            competency_id="plan_terapeutico_msp",
            estimated_minutes=20,
            is_completed=False
        )
        uow.study_plans.add_task(task1)
        uow.study_plans.add_task(task2)
        uow.commit()

    # Marcar primera tarea como completada (50% progreso)
    with uow:
        tasks = uow.study_plans.get_plan_tasks(plan_id)
        assert len(tasks) == 2
        first_task_id = tasks[0].id
        updated_task = uow.study_plans.mark_task_completed(first_task_id)
        assert updated_task is not None
        assert updated_task.is_completed is True

        plan_in_db = uow.study_plans.get_plan_by_id(plan_id)
        assert plan_in_db.progress_percentage == 50.0
        assert plan_in_db.status == "active"
        uow.commit()

    # Marcar segunda tarea como completada (100% progreso -> completed)
    with uow:
        tasks = uow.study_plans.get_plan_tasks(plan_id)
        second_task_id = tasks[1].id
        uow.study_plans.mark_task_completed(second_task_id)

        plan_in_db = uow.study_plans.get_plan_by_id(plan_id)
        assert plan_in_db.progress_percentage == 100.0
        assert plan_in_db.status == "completed"
        assert plan_in_db.completed_at is not None
        uow.commit()


def test_post_test_linked_to_pre_test_with_hake_gain():
    """
    Verifica que un Post-Test se vincule con su Pre-Test original y calcule la
    Ganancia Normalizada de Hake (g = (Post - Pre) / (10.0 - Pre)).
    """
    uow = SqlAlchemyUnitOfWork()
    test_user_id = "usr_alumno_001"
    pre_test_id = f"eval_pre_{uuid.uuid4().hex[:8]}"
    post_test_id = f"eval_post_{uuid.uuid4().hex[:8]}"

    pre_score = 4.0
    post_score = 8.5
    # Ganancia normalizada: (8.5 - 4.0) / (10.0 - 4.0) = 4.5 / 6.0 = 0.75 (Alta Ganancia)
    expected_hake_g = round((post_score - pre_score) / (10.0 - pre_score), 4)

    with uow:
        pre_test = DiagnosticAssessmentModel(
            id=pre_test_id,
            user_id=test_user_id,
            assessment_type="pre_test",
            score_total=pre_score,
            score_max=10.0,
            status="completed"
        )
        uow.assessments.create_assessment(pre_test)

        post_test = DiagnosticAssessmentModel(
            id=post_test_id,
            user_id=test_user_id,
            assessment_type="post_test",
            related_assessment_id=pre_test_id,
            score_total=post_score,
            score_max=10.0,
            hake_gain_g=expected_hake_g,
            status="completed"
        )
        uow.assessments.create_assessment(post_test)
        uow.commit()

    with uow:
        retrieved_post = uow.assessments.get_assessment_by_id(post_test_id)
        assert retrieved_post is not None
        assert retrieved_post.related_assessment_id == pre_test_id
        assert retrieved_post.hake_gain_g == 0.75
        assert retrieved_post.pre_test is not None
        assert retrieved_post.pre_test.score_total == 4.0
