import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Callable
from sqlalchemy.orm import Session

from core.unit_of_work import SqlAlchemyUnitOfWork
from modules.assessments.models import DiagnosticAssessmentModel, DiagnosticItemModel
from modules.assessments.repository import AssessmentRepository
from modules.assessments.schemas import (
    DiagnosticAssessmentDTO,
    DiagnosticItemDTO,
    SubmitAssessmentRequest,
    AssessmentSummaryReportDTO,
)
from modules.cases.dependencies import get_case_service
from rag.isomorphic_generator import IsomorphicCaseGenerator, CURATED_ISOMORPHIC_CASES
from modules.study_plans.service import StudyPlanService
from config import GEMINI_API_KEY

logger = logging.getLogger("ateneo.modules.assessments.service")


def _default_uow():
    return SqlAlchemyUnitOfWork()


class AssessmentService:
    """
    Servicio de Dominio para la Gestión de Evaluaciones Diagnósticas (Pre-Test / Post-Test).
    Orquesta el inicio de baterías, la calificación asistida por RAG/Heurística,
    el cálculo psicométrico de Ganancia de Hake (g) y el enganche transaccional con
    los Planes de Estudio Prescriptivos.
    """
    def __init__(
        self,
        repository: Optional[AssessmentRepository] = None,
        session: Optional[Session] = None,
        uow_factory: Optional[Callable[[], Any]] = None
    ):
        self.repository = repository
        self.session = session
        self.uow_factory = uow_factory or _default_uow

    @classmethod
    def calculate_hake_gain(cls, pre_score: float, post_score: float, max_score: float = 10.0) -> Dict[str, Any]:
        """
        Calcula la Ganancia Normalizada de Hake (g):
        g = (Post - Pre) / (Max - Pre)
        
        Manejo de Casos de Borde:
        - Si Pre >= Max: g = 1.0 si Post >= Pre, sino (Post - Pre) / Pre
        - Si Post < Pre (regresión): g = (Post - Pre) / Pre acotado en [-1.0, 0.0]
        - Caso estándar: g acotado en [0.0, 1.0]
        """
        pre = float(pre_score)
        post = float(post_score)
        max_s = float(max_score)

        if max_s <= 0:
            max_s = 10.0

        if pre >= max_s:
            if post >= pre:
                g = 1.0
            else:
                g = max(-1.0, round((post - pre) / (pre or 1.0), 3))
        elif post < pre:
            g = max(-1.0, round((post - pre) / (pre or 1.0), 3))
        else:
            denom = max_s - pre
            g = round((post - pre) / denom, 3) if denom > 0 else 1.0
            g = min(1.0, max(0.0, g))

        if g >= 0.70:
            category = "Ganancia Alta (g >= 0.70)"
        elif g >= 0.30:
            category = "Ganancia Media (0.30 <= g < 0.70)"
        elif g >= 0.0:
            category = "Ganancia Baja (g < 0.30)"
        else:
            category = "Regresión Diagnóstica (g < 0.0)"

        return {
            "hake_gain_g": g,
            "category": category,
            "pre_score": pre,
            "post_score": post,
            "max_score": max_s
        }

    def start_pre_test(
        self,
        user_id: str,
        specialty_scope: str = "Multidisciplinar GPC",
        num_cases: int = 3
    ) -> DiagnosticAssessmentModel:
        """
        Inicia una sesión de Pre-Test seleccionando casos basales representativos.
        Persiste los reactivos en estado 'in_progress'.
        """
        uow = self.uow_factory()
        with uow:
            case_service = get_case_service()
            all_cases = case_service.list_cases()
            if not all_cases:
                raise ValueError("No existen casos clínicos disponibles para iniciar el Pre-Test.")

            selected_cases = all_cases[:num_cases]

            assessment = DiagnosticAssessmentModel(
                user_id=user_id,
                assessment_type="pre_test",
                specialty_scope=specialty_scope,
                score_total=0.0,
                score_max=10.0,
                status="in_progress",
                started_at=datetime.now(timezone.utc)
            )
            created_assessment = uow.assessments.create_assessment(assessment)

            for case in selected_cases:
                prompt_text = (
                    f"**{case.titulo}**\n\n"
                    f"{case.enunciado}\n\n"
                    f"**Pregunta Formativa:**\n{case.pregunta}"
                )
                item = DiagnosticItemModel(
                    assessment_id=created_assessment.id,
                    case_id=case.id,
                    prompt_text=prompt_text,
                    student_answer="",
                    score_obtained=0.0,
                    omisiones_json="[]",
                    competencias_json=json.dumps(case.competencias_activadas or ["diagnostico_final", "plan_terapeutico_msp"])
                )
                uow.assessments.add_item(item)

            uow.commit()

            res = uow.assessments.get_assessment_by_id(created_assessment.id)
            if res:
                _ = res.items
            return res

    def start_post_test(self, pre_test_id: str, user_id: str) -> DiagnosticAssessmentModel:
        """
        Inicia una sesión de Post-Test isomórfica a partir de un Pre-Test completado.
        Sintetiza variantes paralelas equivalentes para medir ganancia formativa pura.
        """
        uow = self.uow_factory()
        with uow:
            pre_test = uow.assessments.get_assessment_by_id(pre_test_id)
            if not pre_test:
                raise ValueError(f"Evaluación Pre-Test '{pre_test_id}' no encontrada.")
            if pre_test.user_id != user_id:
                raise PermissionError("Acceso no autorizado a la evaluación Pre-Test especificada.")
            if pre_test.status != "completed":
                raise ValueError("El Pre-Test debe estar completado antes de iniciar el Post-Test.")

            items = uow.assessments.get_assessment_items(pre_test_id)
            if not items:
                raise ValueError("El Pre-Test no cuenta con reactivos evaluados.")

            # Generar batería de casos isomórficos paralelos
            isomorphic_battery = IsomorphicCaseGenerator.generate_post_test_battery(
                assessment_items=items
            )

            post_test = DiagnosticAssessmentModel(
                user_id=user_id,
                assessment_type="post_test",
                related_assessment_id=pre_test_id,
                specialty_scope=pre_test.specialty_scope,
                score_total=0.0,
                score_max=10.0,
                status="in_progress",
                started_at=datetime.now(timezone.utc)
            )
            created_post_test = uow.assessments.create_assessment(post_test)

            for iso_case in isomorphic_battery:
                prompt_text = (
                    f"**{iso_case.titulo}**\n\n"
                    f"{iso_case.enunciado}\n\n"
                    f"**Pregunta Formativa:**\n{iso_case.pregunta}"
                )
                item = DiagnosticItemModel(
                    assessment_id=created_post_test.id,
                    case_id=iso_case.id,
                    prompt_text=prompt_text,
                    student_answer="",
                    score_obtained=0.0,
                    omisiones_json="[]",
                    competencias_json=json.dumps(iso_case.competencias_evaluadas)
                )
                uow.assessments.add_item(item)

            uow.commit()

            res = uow.assessments.get_assessment_by_id(created_post_test.id)
            if res:
                _ = res.items
            return res

    def submit_assessment(
        self,
        assessment_id: str,
        user_id: str,
        request: SubmitAssessmentRequest
    ) -> AssessmentSummaryReportDTO:
        """
        Califica y finaliza una evaluación diagnóstica (Pre-Test o Post-Test).
        - Si es Pre-Test: Sintetiza automáticamente el Plan de Estudio Prescriptivo.
        - Si es Post-Test: Calcula la Ganancia de Hake (g) contrastando con el Pre-Test.
        """
        uow = self.uow_factory()
        with uow:
            assessment = uow.assessments.get_assessment_by_id(assessment_id)
            if not assessment:
                raise ValueError(f"Evaluación diagnóstica '{assessment_id}' no encontrada.")
            if assessment.user_id != user_id:
                raise PermissionError("Acceso no autorizado a la evaluación diagnóstica.")
            if assessment.status == "completed":
                raise ValueError("Esta evaluación diagnóstica ya ha sido completada previamente.")

            items = uow.assessments.get_assessment_items(assessment_id)
            items_by_id = {it.id: it for it in items}

            total_score = 0.0
            total_omisiones_count = 0
            affected_competencies = set()

            for ans in request.answers:
                item = items_by_id.get(ans.item_id)
                if not item:
                    continue

                item.student_answer = ans.student_answer.strip()

                # Calificación diagnóstica (RAG o Heurística Defensiva)
                eval_res = self._evaluate_item_answer(item)
                item.score_obtained = eval_res["score"]
                item.omisiones_json = json.dumps(eval_res["omisiones"], ensure_ascii=False)
                item.competencias_json = json.dumps(eval_res["competencias"], ensure_ascii=False)

                total_score += eval_res["score"]
                total_omisiones_count += len(eval_res["omisiones"])
                for c in eval_res["competencias"]:
                    affected_competencies.add(c if isinstance(c, str) else c.get("competencia", str(c)))

            # Normalizar calificación promedio sobre 10
            n_items = len(request.answers) or 1
            avg_score = round(total_score / n_items, 2)
            assessment.score_total = avg_score
            assessment.status = "completed"
            assessment.completed_at = datetime.now(timezone.utc)

            hake_data = None
            # Si es Post-Test vinculado con Pre-Test, calcular Hake Gain
            if assessment.assessment_type == "post_test" and assessment.related_assessment_id:
                pre_test = uow.assessments.get_assessment_by_id(assessment.related_assessment_id)
                if pre_test and pre_test.score_total is not None:
                    hake_data = self.calculate_hake_gain(
                        pre_score=pre_test.score_total,
                        post_score=avg_score,
                        max_score=assessment.score_max or 10.0
                    )
                    assessment.hake_gain_g = hake_data["hake_gain_g"]

            uow.commit()

            # Si es Pre-Test, generar automáticamente el Plan de Estudio Prescriptivo
            if assessment.assessment_type == "pre_test":
                try:
                    study_service = StudyPlanService(uow_factory=self.uow_factory)
                    study_service.generate_plan_from_assessment(assessment_id, user_id)
                except Exception as ex:
                    logger.warning(f"No se pudo autogenerar plan de estudio para evaluación '{assessment_id}': {ex}")

            return AssessmentSummaryReportDTO(
                assessment_id=assessment.id,
                user_id=assessment.user_id,
                assessment_type=assessment.assessment_type,
                score_total=assessment.score_total,
                score_max=assessment.score_max or 10.0,
                hake_gain_g=assessment.hake_gain_g,
                hake_category=hake_data.get("category") if hake_data else None,
                total_omisiones_detectadas=total_omisiones_count,
                competencias_afectadas=list(affected_competencies),
                completed_at=assessment.completed_at or datetime.now(timezone.utc)
            )

    def get_assessment_details(self, assessment_id: str, user_id: str) -> Optional[DiagnosticAssessmentModel]:
        """Consulta una evaluación diagnóstica con sus ítems."""
        uow = self.uow_factory()
        with uow:
            assessment = uow.assessments.get_assessment_by_id(assessment_id)
            if not assessment:
                return None
            if assessment.user_id != user_id:
                return None
            _ = assessment.items
            return assessment

    def get_user_history(self, user_id: str) -> List[DiagnosticAssessmentModel]:
        """Consulta el historial de evaluaciones diagnósticas del estudiante."""
        uow = self.uow_factory()
        with uow:
            assessments = uow.assessments.get_user_assessments(user_id)
            for a in assessments:
                _ = a.items
            return assessments

    def _evaluate_item_answer(self, item: DiagnosticItemModel) -> Dict[str, Any]:
        """
        Califica de forma defensiva y reproducible la respuesta del estudiante.
        Si la respuesta está vacía o es muy deficiente, asigna omisiones normativas.
        Si incluye criterios de la GPC, otorga puntaje formativo.
        """
        ans = (item.student_answer or "").strip().lower()
        if not ans:
            return {
                "score": 0.0,
                "omisiones": ["Omisión total de respuesta clínica y conducta terapéutica normada"],
                "competencias": ["plan_terapeutico_msp", "diagnostico_final"]
            }

        score = 5.0
        omisiones: List[str] = []
        competencias: List[str] = []

        # Análisis de fidelidad normativa con base en palabras clave diagnósticas/terapéuticas
        norm_keywords = [
            ("sulfato de magnesio", 2.0, "Manejo farmacológico con Sulfato de Magnesio"),
            ("zuspan", 1.5, "Esquema normado Zuspan"),
            ("codigo rojo", 2.0, "Activación de Código Rojo"),
            ("oxitocina", 1.5, "Uso de uterotónicos normados"),
            ("curb-65", 2.0, "Estratificación de CURB-65"),
            ("ceftriaxona", 1.5, "Antibioticoterapia de primera línea"),
            ("hipotermia", 2.5, "Hipotermia terapéutica neonatal a 33.5°C"),
            ("ameu", 2.0, "Evacuación uterina por AMEU según edad gestacional")
        ]

        for kw, pts, label in norm_keywords:
            if kw in ans:
                score += pts

        # Penalizaciones por omisiones detectadas
        if "sulfato" not in ans and ("preeclampsia" in item.prompt_text.lower() or "hipertens" in item.prompt_text.lower()):
            omisiones.append("Omisión de neuroprotección con Sulfato de Magnesio según GPC MSP")
            competencias.append("plan_terapeutico_msp")

        if "codigo rojo" not in ans and "hemorragia" in item.prompt_text.lower():
            omisiones.append("Demora en activación inmediata del protocolo de Código Rojo Obstétrico")
            competencias.append("plan_terapeutico_msp")

        if "curb" not in ans and "neumonia" in item.prompt_text.lower():
            omisiones.append("Omisión de estratificación objetiva de severidad mediante escala CURB-65")
            competencias.append("diagnostico_final")

        final_score = min(10.0, max(0.0, round(score, 1)))
        return {
            "score": final_score,
            "omisiones": omisiones,
            "competencias": competencias or ["plan_terapeutico_msp"]
        }
