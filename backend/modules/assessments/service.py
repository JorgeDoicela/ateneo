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


# Mapeo nosológico canónico de casos clínicos a las 4 Áreas Troncales (CACES / MSP Ecuador)
TRONCAL_GINECO_OBSTETRICIA = "Ginecología y Obstetricia"
TRONCAL_PEDIATRIA_NEONATOLOGIA = "Pediatría y Neonatología"
TRONCAL_MEDICINA_INTERNA = "Medicina Interna y Crónicos"
TRONCAL_INFECTOLOGIA_SALUD_PUBLICA = "Infectología y Salud Pública"

TRONCALES_CANONICAS = [
    TRONCAL_GINECO_OBSTETRICIA,
    TRONCAL_PEDIATRIA_NEONATOLOGIA,
    TRONCAL_MEDICINA_INTERNA,
    TRONCAL_INFECTOLOGIA_SALUD_PUBLICA,
]

CASE_TRONCAL_MAP: Dict[str, str] = {
    "case_preeclampsia_01": TRONCAL_GINECO_OBSTETRICIA,
    "case_hemorragia_01": TRONCAL_GINECO_OBSTETRICIA,
    "case_aborto_01": TRONCAL_GINECO_OBSTETRICIA,
    "case_nac_01": TRONCAL_PEDIATRIA_NEONATOLOGIA,
    "case_sepsis_neonatal_01": TRONCAL_PEDIATRIA_NEONATOLOGIA,
    "case_ehirn_01": TRONCAL_PEDIATRIA_NEONATOLOGIA,
    "case_hta_01": TRONCAL_MEDICINA_INTERNA,
    "case_erc_01": TRONCAL_MEDICINA_INTERNA,
    "case_tb_01": TRONCAL_INFECTOLOGIA_SALUD_PUBLICA,
    "case_vih_01": TRONCAL_INFECTOLOGIA_SALUD_PUBLICA,
}


def select_stratified_pre_test_cases(
    all_cases: List[Any],
    specialty_scope: str,
    user_id: str,
    num_cases: int = 4
) -> List[Any]:
    """
    Selecciona los reactivos del Pre-Test mediante muestreo estratificado balanceado:
    1. Si el scope es Multidisciplinar / CACES: selecciona exactamente 1 caso representativo
       por cada una de las 4 áreas troncales de la carrera de medicina en Ecuador.
       Garantiza validez de contenido psicométrica, paridad diagnóstica (25% por troncal)
       y erradica el sesgo de sobredimensionar una sola especialidad.
    2. Si el scope es monotemático (ej. solo Pediatría): filtra rigurosamente los casos
       pertenecientes a dicha especialidad troncal.
    """
    scope_lower = (specialty_scope or "").strip().lower()
    is_multidisciplinar = (
        not specialty_scope or
        "multidisciplinar" in scope_lower or
        "caces" in scope_lower or
        "general" in scope_lower or
        "troncal" in scope_lower
    )

    if is_multidisciplinar:
        # Agrupar casos por troncal
        cases_by_troncal: Dict[str, List[Any]] = {t: [] for t in TRONCALES_CANONICAS}
        for c in all_cases:
            t = CASE_TRONCAL_MAP.get(c.id)
            if t and t in cases_by_troncal:
                cases_by_troncal[t].append(c)

        selected: List[Any] = []
        hash_seed = sum(ord(ch) for ch in user_id) if user_id else 0

        # Seleccionar 1 caso representativo de cada una de las 4 troncales
        for troncal in TRONCALES_CANONICAS:
            bucket = cases_by_troncal.get(troncal, [])
            if bucket:
                idx = (hash_seed + len(selected)) % len(bucket)
                selected.append(bucket[idx])

        if num_cases and num_cases > 0 and num_cases < len(selected):
            return selected[:num_cases]
        return selected

    # Ámbito monotemático específico
    matched_cases = [
        c for c in all_cases
        if CASE_TRONCAL_MAP.get(c.id, "").lower() == scope_lower or
           scope_lower in CASE_TRONCAL_MAP.get(c.id, "").lower()
    ]
    if matched_cases:
        return matched_cases[:num_cases]

    return all_cases[:num_cases]


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
        specialty_scope: str = "Batería Troncal CACES (Multidisciplinar)",
        num_cases: int = 4
    ) -> DiagnosticAssessmentModel:
        """
        Inicia una sesión de Pre-Test seleccionando casos basales mediante muestreo estratificado balanceado.
        Garantiza que una prueba general evalúe las 4 troncales (Gineco-Obstetricia, Pediatría, Medicina Interna, Infectología).
        """
        uow = self.uow_factory()
        with uow:
            case_service = get_case_service()
            all_cases = case_service.list_cases()
            if not all_cases:
                raise ValueError("No existen casos clínicos disponibles para iniciar el Pre-Test.")

            selected_cases = select_stratified_pre_test_cases(
                all_cases=all_cases,
                specialty_scope=specialty_scope,
                user_id=user_id,
                num_cases=num_cases
            )

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
                troncal = CASE_TRONCAL_MAP.get(case.id, "Troncal Clínica")
                prompt_text = (
                    f"### {case.titulo}\n\n"
                    f"> **Área Troncal:** {troncal} • **Guía Oficial:** {case.guia_asociada}\n\n"
                    f"{case.enunciado}\n\n"
                    f"**Pregunta Formativa:**\n\n{case.pregunta}"
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
                troncal = CASE_TRONCAL_MAP.get(iso_case.base_case_id, "Troncal Clínica")
                guia = iso_case.guia_asociada or "Guía de Práctica Clínica MSP Ecuador"
                prompt_text = (
                    f"### {iso_case.titulo} (Variante Isomórfica Post-Test)\n\n"
                    f"> **Área Troncal:** {troncal} • **Guía Oficial:** {guia}\n\n"
                    f"{iso_case.enunciado}\n\n"
                    f"**Pregunta Formativa:**\n\n{iso_case.pregunta}"
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

        # Análisis de fidelidad normativa con base en palabras clave diagnósticas/terapéuticas (10 patologías canónicas)
        norm_keywords = [
            # Ginecología y Obstetricia
            ("sulfato de magnesio", 2.0, "Manejo farmacológico con Sulfato de Magnesio"),
            ("zuspan", 1.5, "Esquema normado Zuspan"),
            ("codigo rojo", 2.0, "Activación de Código Rojo Obstétrico"),
            ("oxitocina", 1.5, "Uso de uterotónicos normados de primera línea"),
            ("ameu", 2.0, "Evacuación uterina por AMEU según edad gestacional"),
            ("anti-d", 1.5, "Profilaxis con Inmunoglobulina Anti-D en madre Rh-"),
            # Pediatría y Neonatología
            ("salbutamol", 2.0, "Broncodilatador de acción rápida (SABA)"),
            ("corticoide", 1.5, "Corticoide sistémico en crisis asmática"),
            ("curb-65", 2.0, "Estratificación objetiva de CURB-65"),
            ("ceftriaxona", 1.5, "Antibioticoterapia parenteral normada"),
            ("hipotermia", 2.5, "Hipotermia terapéutica neonatal a 33.5°C"),
            ("ampicilina", 1.5, "Ampicilina parenteral en sepsis neonatal"),
            ("gentamicina", 1.5, "Gentamicina parenteral en sepsis neonatal"),
            # Medicina Interna y Crónicos
            ("insulina", 2.0, "Insulinoterapia en cetoacidosis diabética"),
            ("cristaloides", 1.5, "Hidratación parenteral con solución salina / cristaloides"),
            ("gluconato de calcio", 2.5, "Estabilizador de membrana miocárdica en hiperpotasemia"),
            ("emergencia hipertensiva", 1.5, "Identificación de emergencia hipertensiva"),
            # Infectología y Salud Pública
            ("ringer lactato", 2.0, "Rehidratación vigorosa en Dengue con signos de alarma"),
            ("rhze", 2.5, "Esquema antituberculoso de fase intensiva en DFC"),
            ("tld", 2.0, "Esquema TARGA de primera línea Tenofovir/Lamivudina/Dolutegravir"),
            ("cotrimoxazol", 1.5, "Profilaxis de infecciones oportunistas ante CD4 < 200")
        ]

        for kw, pts, label in norm_keywords:
            if kw in ans:
                score += pts

        # Penalizaciones por omisiones diagnósticas o terapéuticas críticas
        p_lower = item.prompt_text.lower()

        if "sulfato" not in ans and ("preeclampsia" in p_lower or "criterios de severidad" in p_lower):
            omisiones.append("Omisión de neuroprotección con Sulfato de Magnesio bajo esquema Zuspan según GPC MSP")
            competencias.append("plan_terapeutico_msp")

        if "codigo rojo" not in ans and "hemorragia" in p_lower:
            omisiones.append("Demora en activación inmediata del protocolo de Código Rojo Obstétrico")
            competencias.append("plan_terapeutico_msp")

        if "anti-d" not in ans and "inmunoglobulina" not in ans and "aborto" in p_lower and "negativo" in p_lower:
            omisiones.append("Omisión de profilaxis con Inmunoglobulina Anti-D en paciente Rh negativo")
            competencias.append("plan_terapeutico_msp")

        if "salbutamol" not in ans and "inhalad" not in ans and "asma" in p_lower:
            omisiones.append("Omisión de broncodilatador de acción rápida (Salbutamol) en crisis asmática")
            competencias.append("plan_terapeutico_msp")

        if "ampicilina" not in ans and "gentamicina" not in ans and "sepsis" in p_lower:
            omisiones.append("Omisión del esquema antimicrobiano sinérgico empírico (Ampicilina + Gentamicina)")
            competencias.append("plan_terapeutico_msp")

        if "hipotermia" not in ans and ("ehirn" in p_lower or "asfixia" in p_lower or "sarnat" in p_lower):
            omisiones.append("Omisión de indicación oportuna de Hipotermia Terapéutica dentro de la ventana de 6 horas")
            competencias.append("plan_terapeutico_msp")

        if "curb" not in ans and "neumonia" in p_lower:
            omisiones.append("Omisión de estratificación objetiva de severidad mediante escala CURB-65")
            competencias.append("diagnostico_final")

        if "insulina" not in ans and "cetoacidosis" in p_lower:
            omisiones.append("Omisión de infusión de insulina cristalina continua en cetoacidosis diabética")
            competencias.append("plan_terapeutico_msp")

        if "gluconato" not in ans and ("hiperpotasemia" in p_lower or "potasio" in p_lower):
            omisiones.append("Omisión de estabilizador de membrana cardiaca (Gluconato de Calcio) ante hiperpotasemia severa")
            competencias.append("plan_terapeutico_msp")

        if "ringer" not in ans and "salina" not in ans and "dengue" in p_lower:
            omisiones.append("Omisión de reposición hídrica parenteral inmediata con cristaloides en Dengue con signos de alarma")
            competencias.append("plan_terapeutico_msp")

        if "rhze" not in ans and "tuberculosis" in p_lower:
            omisiones.append("Omisión de prescripción normada de Fase Inicial en Dosis Fija Combinada (RHZE)")
            competencias.append("plan_terapeutico_msp")

        if "cotrimoxazol" not in ans and "tld" not in ans and "vih" in p_lower:
            omisiones.append("Omisión de profilaxis con Cotrimoxazol ante CD4 < 200 e inicio normado de TLD")
            competencias.append("plan_terapeutico_msp")

        final_score = min(10.0, max(0.0, round(score, 1)))
        return {
            "score": final_score,
            "omisiones": omisiones,
            "competencias": competencias or ["plan_terapeutico_msp"]
        }
