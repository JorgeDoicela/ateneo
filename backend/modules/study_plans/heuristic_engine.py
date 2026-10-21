import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from adaptive.knowledge_space import CLINICAL_COMPETENCIES, knowledge_space
from adaptive.curriculum_engine import CASE_COMPETENCY_MAP, detect_zone_of_proximal_development
from models.clinical_case import load_all_cases

logger = logging.getLogger(__name__)

# Palabras clave de severidad clínica y riesgo nosológico
KEYWORDS_SEVERITY_CRITICAL = [
    "sulfato de magnesio", "impregnacion", "impregnación", "codigo rojo", "código rojo",
    "shock", "reanimacion", "reanimación", "adrenalina", "intubacion", "intubación",
    "hemorragia", "oxitocina", "antibioticoterapia", "vitamina k", "falla organica",
    "falla orgánica", "hipotermia terapeutica", "hipotermia terapéutica", "inestabilidad"
]

KEYWORDS_SEVERITY_HIGH = [
    "diagnostico diferencial", "diagnóstico diferencial", "proteinuria", "criterios de severidad",
    "plaquetopenia", "trombocitopenia", "creatinina", "gasometria", "gasometría",
    "radiografia", "radiografía", "curb-65", "electrocardiograma", "cultivo", "biometria",
    "biometría", "transfusional", "criterios de ingreso"
]

# Mapeo de referencias canónicas a Guías de Práctica Clínica (GPC Ecuador)
GPC_NORMATIVE_RESOURCES = {
    "preeclampsia": {
        "guia": "GPC Trastornos Hipertensivos del Embarazo (MSP Ecuador)",
        "seccion_clave": "Sección 4.2: Manejo de Preeclampsia con Criterios de Severidad e Impregnación con Sulfato de Magnesio",
        "tiempo_lectura": 15
    },
    "hemorragia": {
        "guia": "GPC Prevención y Manejo de la Hemorragia Posparto (MSP Ecuador)",
        "seccion_clave": "Sección 5.1: Activación del Código Rojo Obstétrico y Secuencia de Uterotónicos",
        "tiempo_lectura": 15
    },
    "aborto": {
        "guia": "GPC Atención del Aborto y sus Complicaciones (MSP Ecuador)",
        "seccion_clave": "Sección 3.2: Evacuación Uterina por AMEU y Profilaxis con Inmunoglobulina Anti-D",
        "tiempo_lectura": 12
    },
    "asma": {
        "guia": "GPC Diagnóstico y Tratamiento del Asma en Pediatría (MSP Ecuador)",
        "seccion_clave": "Sección 5.3: Manejo Escalonado de Crisis Asmática Grave con SABA y Corticoide Sistémico",
        "tiempo_lectura": 15
    },
    "bronquiolitis": {
        "guia": "GPC Diagnóstico y Manejo de la Bronquiolitis Aguda (MSP Ecuador)",
        "seccion_clave": "Sección 4.1: Oxigenoterapia y Criterios de Soporte No Invasivo en Lactantes",
        "tiempo_lectura": 12
    },
    "sepsis": {
        "guia": "GPC Prevención, Diagnóstico y Tratamiento de la Sepsis Neonatal (MSP Ecuador)",
        "seccion_clave": "Sección 3.2: Esquemas Antimicrobianos de Primera Línea en Sepsis Temprana (Ampicilina + Gentamicina)",
        "tiempo_lectura": 15
    },
    "ehirn": {
        "guia": "GPC Encefalopatía Hipóxico-Isquémica en el Recién Nacido (MSP Ecuador)",
        "seccion_clave": "Sección 5: Criterios de Elegibilidad para Hipotermia Terapéutica Corporal Total y Ventana de 6 Horas",
        "tiempo_lectura": 15
    },
    "cetoacidosis": {
        "guia": "GPC Diabetes Mellitus Tipo 2 y Complicaciones Agudas (MSP Ecuador)",
        "seccion_clave": "Sección 4.2: Protocolo de Rehidratación con Cristaloides, Insulinoterapia y Reposición de Potasio",
        "tiempo_lectura": 15
    },
    "diabetes": {
        "guia": "GPC Diabetes Mellitus Tipo 2 y Complicaciones Agudas (MSP Ecuador)",
        "seccion_clave": "Sección 4.2: Protocolo de Rehidratación con Cristaloides, Insulinoterapia y Reposición de Potasio",
        "tiempo_lectura": 15
    },
    "hta": {
        "guia": "GPC Diagnóstico y Tratamiento de la Hipertensión Arterial (MSP Ecuador)",
        "seccion_clave": "Sección 6.2: Manejo de Emergencias Hipertensivas y Reducción Tensional Controlada",
        "tiempo_lectura": 12
    },
    "erc": {
        "guia": "GPC Abordaje de la Enfermedad Renal Crónica (MSP Ecuador)",
        "seccion_clave": "Sección 4.4: Manejo de Hiperpotasemia Grave con Estabilizadores de Membrana y Criterios Dialíticos",
        "tiempo_lectura": 15
    },
    "renal": {
        "guia": "GPC Abordaje de la Enfermedad Renal Crónica (MSP Ecuador)",
        "seccion_clave": "Sección 4.4: Manejo de Hiperpotasemia Grave con Estabilizadores de Membrana y Criterios Dialíticos",
        "tiempo_lectura": 15
    },
    "nac": {
        "guia": "GPC Neumonía Adquirida en la Comunidad en Pediatría y Adultos (MSP Ecuador)",
        "seccion_clave": "Sección 4.1: Estratificación de Riesgo CURB-65 y Antibioticoterapia Empírica Inicial",
        "tiempo_lectura": 15
    },
    "neumonia": {
        "guia": "GPC Neumonía Adquirida en la Comunidad en Pediatría y Adultos (MSP Ecuador)",
        "seccion_clave": "Sección 4.1: Estratificación de Riesgo CURB-65 y Antibioticoterapia Empírica Inicial",
        "tiempo_lectura": 15
    },
    "dengue": {
        "guia": "GPC Manejo del Dengue en el Primer y Segundo Nivel (MSP Ecuador)",
        "seccion_clave": "Sección 3.3: Hidratación con Cristaloides en Dengue con Signos de Alarma y Choque",
        "tiempo_lectura": 12
    },
    "tb": {
        "guia": "Guía de Práctica Clínica para la Prevención y Tratamiento de la Tuberculosis (MSP Ecuador)",
        "seccion_clave": "Sección 4.3: Esquema de Tratamiento Fase Intensiva con Dosis Fijas Combinadas (RHZE)",
        "tiempo_lectura": 15
    },
    "vih": {
        "guia": "GPC Atención Integral de Personas con VIH (MSP Ecuador)",
        "seccion_clave": "Sección 4.1: Profilaxis de Infecciones Oportunistas con Cotrimoxazol e Inicio de Esquema TLD",
        "tiempo_lectura": 15
    }
}


class StudyPlanHeuristicEngine:
    """
    Motor Heurístico de Prescripción Pedagógica basada en Evidencia Clínica.
    Calcula determinísticamente las brechas formativas de un estudiante, pondera
    el riesgo clínico ($W_i$), extrae la evidencia de las GPCs de Ecuador y prescribe
    una ruta de aprendizaje dosificada en la Zona de Desarrollo Próximo (ZDP).
    """

    @classmethod
    def evaluate_omission_severity(cls, omission_text: str) -> Tuple[float, str]:
        """
        Clasifica una omisión clínica según el riesgo de morbimortalidad y Código Rojo:
        - Severidad 3.0: Crítica (fármacos vitales, reanimación, código rojo).
        - Severidad 2.0: Alta (diagnóstico diferencial, gravedad, paraclínicos urgentes).
        - Severidad 1.0: Moderada (seguimiento, prevención, monitoreo ambulatorio).
        """
        text_lower = omission_text.lower()
        for kw in KEYWORDS_SEVERITY_CRITICAL:
            if kw in text_lower:
                return 3.0, "Crítica (Riesgo Vital / Fármaco Normado)"
        for kw in KEYWORDS_SEVERITY_HIGH:
            if kw in text_lower:
                return 2.0, "Alta (Diagnóstico y Severidad)"
        return 1.0, "Moderada (Monitoreo y Seguimiento)"

    @classmethod
    def find_associated_gpc_resource(cls, text_context: str) -> Dict[str, Any]:
        """Identifica la Guía de Práctica Clínica oficial correspondiente al contexto clínico."""
        text_lower = text_context.lower()
        for key, res in GPC_NORMATIVE_RESOURCES.items():
            if key in text_lower:
                return res
        # Fallback normativo general
        return {
            "guia": "Guías de Práctica Clínica Oficiales (MSP Ecuador)",
            "seccion_clave": "Criterios Diagnósticos y Esquemas Terapéuticos Estandarizados",
            "tiempo_lectura": 15
        }

    @classmethod
    def synthesize_prescriptive_plan(
        cls,
        assessment_items: List[Dict[str, Any]],
        knowledge_state: Dict[str, float],
        assessment_type: str = "pre_test",
        hake_gain_g: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sintetiza un plan prescriptivo personalizado:
        1. Identifica y pondera las brechas clínicas ($W_i = \text{severidad} \times (1.05 - P(L_k))$).
        2. Selecciona la evidencia GPC específica para lectura guiada.
        3. Identifica casos recomendados en la Zona de Desarrollo Próximo (ZDP).
        4. Genera tareas secuenciales y dosificadas (nivelación para Pre-Test o maestría/consolidación para Post-Test).
        """
        scored_gaps: List[Dict[str, Any]] = []

        for item in assessment_items:
            raw_omisiones = item.get("omisiones", [])
            if isinstance(raw_omisiones, str):
                try:
                    raw_omisiones = json.loads(raw_omisiones)
                except Exception:
                    raw_omisiones = [raw_omisiones]

            prompt_text = item.get("prompt_text", "")
            case_id = item.get("case_id", "")

            # Identificar competencias asociadas al ítem
            item_comps = CASE_COMPETENCY_MAP.get(case_id, ["semiologia_anamnesis", "plan_terapeutico_msp"])

            for omision in raw_omisiones:
                if not isinstance(omision, str) or not omision.strip():
                    continue

                severity_weight, severity_label = cls.evaluate_omission_severity(omision)

                # Priorizar con base en la competencia con menor maestría BKT
                min_p_comp = min(item_comps, key=lambda c: knowledge_state.get(c, 0.5))
                p_mastery = knowledge_state.get(min_p_comp, 0.5)

                # Fórmula psicométrica ponderada: W_i = Severidad * (1.05 - P(L_k))
                w_score = round(severity_weight * (1.05 - p_mastery), 3)

                gpc_res = cls.find_associated_gpc_resource(f"{omision} {prompt_text} {case_id}")

                scored_gaps.append({
                    "omision": omision.strip(),
                    "severidad_peso": severity_weight,
                    "severidad_label": severity_label,
                    "competency_id": min_p_comp,
                    "competency_name": CLINICAL_COMPETENCIES.get(min_p_comp, {}).get("nombre", min_p_comp),
                    "p_mastery": p_mastery,
                    "w_score": w_score,
                    "case_id": case_id,
                    "gpc_resource": gpc_res
                })

        # Ordenar brechas por peso heurístico descendente
        scored_gaps.sort(key=lambda g: g["w_score"], reverse=True)

        # Detectar casos en ZDP
        zdp_competencies = detect_zone_of_proximal_development(knowledge_state)
        all_cases = load_all_cases()

        tasks_payload: List[Dict[str, Any]] = []
        used_cases = set()

        if assessment_type == "post_test":
            # Ruta de Consolidación y Maestría Clínica (Post-Test)
            top_gaps = scored_gaps[:2] if scored_gaps else []
            if top_gaps:
                for gap in top_gaps:
                    tasks_payload.append({
                        "task_type": "gpc_reading",
                        "title": f"Lectura de Maestría GPC: {gap['gpc_resource']['guia']}",
                        "description": f"Estudio avanzado en {gap['gpc_resource']['seccion_clave']} para perfeccionar la brecha residual: '{gap['omision']}'.",
                        "resource_reference": gap["gpc_resource"]["guia"],
                        "competency_id": gap["competency_id"],
                        "estimated_minutes": gap["gpc_resource"]["tiempo_lectura"],
                        "is_completed": False
                    })
            else:
                tasks_payload.append({
                    "task_type": "gpc_reading",
                    "title": "Lectura Normativa Avanzada: Protocolos Críticos MSP Ecuador",
                    "description": "Estudio de directrices avanzadas y algoritmo de manejo en situaciones de emergencia médica y quirúrgica.",
                    "resource_reference": "GPC Trastornos Hipertensivos del Embarazo (MSP Ecuador)",
                    "competency_id": "plan_terapeutico_msp",
                    "estimated_minutes": 15,
                    "is_completed": False
                })

            target_comps = set(g["competency_id"] for g in top_gaps) or set(zdp_competencies) or {"plan_terapeutico_msp"}
            for case in all_cases:
                case_comps = CASE_COMPETENCY_MAP.get(case.id, [])
                if any(tc in case_comps for tc in target_comps) and case.id not in used_cases:
                    tasks_payload.append({
                        "task_type": "case_simulation",
                        "title": f"Simulación de Maestría: {case.titulo}",
                        "description": f"Resolución autónoma de caso clínico ({case.guia_asociada}) para afianzar toma de decisiones en internado rotativo.",
                        "resource_reference": case.id,
                        "competency_id": list(target_comps)[0] if target_comps else "plan_terapeutico_msp",
                        "estimated_minutes": 20,
                        "is_completed": False
                    })
                    used_cases.add(case.id)
                    if len(tasks_payload) >= 3:
                        break

            # Asegurar al menos 2 simulaciones clínicas en el plan de maestría
            if len([t for t in tasks_payload if t["task_type"] == "case_simulation"]) < 2:
                for case in all_cases:
                    if case.id not in used_cases:
                        tasks_payload.append({
                            "task_type": "case_simulation",
                            "title": f"Simulación de Maestría: {case.titulo}",
                            "description": f"Resolución autónoma de caso clínico ({case.guia_asociada}) para consolidar autonomía clínica.",
                            "resource_reference": case.id,
                            "competency_id": "diagnostico_final",
                            "estimated_minutes": 20,
                            "is_completed": False
                        })
                        used_cases.add(case.id)
                        if len(tasks_payload) >= 3:
                            break

            # Debriefing socrático de auditoría y maestría
            if scored_gaps:
                primary_gap = scored_gaps[0]
                tasks_payload.append({
                    "task_type": "socratic_review",
                    "title": "Auditoría Clínica de Maestría: Justificación de Decisión Normada",
                    "description": f"Debriefing socrático interactivo sobre: '{primary_gap['omision']}' para asegurar criterio normativo independiente.",
                    "resource_reference": primary_gap.get("case_id") or "case_preeclampsia_01",
                    "competency_id": primary_gap["competency_id"],
                    "estimated_minutes": 10,
                    "is_completed": False
                })
            else:
                tasks_payload.append({
                    "task_type": "socratic_review",
                    "title": "Auditoría y Liderazgo Clínico: Análisis Socrático de Casos Críticos",
                    "description": "Evaluación reflexiva sobre toma de decisiones de emergencia, manejo de recursos y priorización clínica según normativa MSP.",
                    "resource_reference": "case_preeclampsia_01",
                    "competency_id": "diagnostico_final",
                    "estimated_minutes": 10,
                    "is_completed": False
                })

            if hake_gain_g is not None:
                plan_title = f"Plan de Consolidación y Maestría Clínica (Post-Test - Ganancia de Hake: {hake_gain_g:.2f})"
            else:
                plan_title = "Plan de Consolidación y Maestría Clínica (Post-Test GPC MSP)"

            if scored_gaps:
                hake_txt = f" con Ganancia de Hake g={hake_gain_g:.2f}" if hake_gain_g is not None else ""
                diagnosis_summary = (
                    f"Evaluación final completada{hake_txt}. Se identificaron {len(scored_gaps)} brechas clínicas residuales. "
                    f"Prioridad formativa de consolidación en: {', '.join(set(g['competency_name'] for g in scored_gaps[:2]))}. "
                    f"Ruta prescriptiva dosificada para afianzar la autonomía y el juicio diagnóstico previo al internado rotativo."
                )
            else:
                hake_txt = f" (Ganancia de Hake g={hake_gain_g:.2f} - Alto Rendimiento)" if hake_gain_g is not None else ""
                diagnosis_summary = (
                    f"Evaluación final completada con dominio clínico sobresaliente{hake_txt}. "
                    "No se identificaron omisiones normativas críticas. Plan de maestría clínica orientado a casos de alta complejidad y liderazgo asistencial."
                )

            return {
                "title": plan_title,
                "diagnosis_summary": diagnosis_summary,
                "target_duration_days": 7,
                "scored_gaps": scored_gaps,
                "tasks": tasks_payload
            }

        # Ruta estándar de Nivelación Basal (Pre-Test)
        top_gaps = scored_gaps[:2] if scored_gaps else []
        for gap in top_gaps:
            tasks_payload.append({
                "task_type": "gpc_reading",
                "title": f"Lectura Normativa GPC: {gap['gpc_resource']['guia']}",
                "description": f"Estudio focalizado en {gap['gpc_resource']['seccion_clave']} para superar la brecha: '{gap['omision']}'.",
                "resource_reference": gap["gpc_resource"]["guia"],
                "competency_id": gap["competency_id"],
                "estimated_minutes": gap["gpc_resource"]["tiempo_lectura"],
                "is_completed": False
            })

        if not top_gaps:
            tasks_payload.append({
                "task_type": "gpc_reading",
                "title": "Lectura Normativa GPC: Marco Troncal MSP Ecuador",
                "description": "Estudio general de guías normativas para consolidación de competencias clínicas.",
                "resource_reference": "Guías de Práctica Clínica Oficiales (MSP Ecuador)",
                "competency_id": "plan_terapeutico_msp",
                "estimated_minutes": 15,
                "is_completed": False
            })

        target_comps = set(g["competency_id"] for g in top_gaps) or set(zdp_competencies) or {"plan_terapeutico_msp"}

        for case in all_cases:
            case_comps = CASE_COMPETENCY_MAP.get(case.id, [])
            if any(tc in case_comps for tc in target_comps) and case.id not in used_cases:
                tasks_payload.append({
                    "task_type": "case_simulation",
                    "title": f"Simulación Práctica: {case.titulo}",
                    "description": f"Resolución de caso clínico en Zona de Desarrollo Próximo ({case.guia_asociada}) enfocado en adherencia a la GPC.",
                    "resource_reference": case.id,
                    "competency_id": list(target_comps)[0] if target_comps else "plan_terapeutico_msp",
                    "estimated_minutes": 20,
                    "is_completed": False
                })
                used_cases.add(case.id)
                if len(tasks_payload) >= 4:
                    break

        if len([t for t in tasks_payload if t["task_type"] == "case_simulation"]) < 2:
            for case in all_cases:
                if case.id not in used_cases:
                    tasks_payload.append({
                        "task_type": "case_simulation",
                        "title": f"Simulación Práctica: {case.titulo}",
                        "description": f"Resolución de caso clínico ({case.guia_asociada}) enfocado en adherencia a la GPC.",
                        "resource_reference": case.id,
                        "competency_id": "diagnostico_final",
                        "estimated_minutes": 20,
                        "is_completed": False
                    })
                    used_cases.add(case.id)
                    if len(tasks_payload) >= 4:
                        break

        if scored_gaps:
            primary_gap = scored_gaps[0]
            tasks_payload.append({
                "task_type": "socratic_review",
                "title": "Debriefing Socrático: Razonamiento y Justificación de Decisión",
                "description": f"Interrogación socrática interactiva sobre: '{primary_gap['omision']}' para afianzar el criterio normativo.",
                "resource_reference": primary_gap.get("case_id") or "case_preeclampsia_01",
                "competency_id": primary_gap["competency_id"],
                "estimated_minutes": 10,
                "is_completed": False
            })
        else:
            tasks_payload.append({
                "task_type": "socratic_review",
                "title": "Debriefing Socrático: Razonamiento y Justificación de Decisión",
                "description": "Interrogación socrática interactiva para afianzar el criterio normativo y la autonomía diagnóstica.",
                "resource_reference": "case_preeclampsia_01",
                "competency_id": "diagnostico_final",
                "estimated_minutes": 10,
                "is_completed": False
            })

        critical_count = sum(1 for g in scored_gaps if g["severidad_peso"] >= 3.0)
        plan_title = (
            f"Plan de Refuerzo Clínico Prioritario ({len(tasks_payload)} tareas dosificadas)"
            if critical_count > 0 else
            f"Plan de Perfeccionamiento y Consolidación de Competencias GPC"
        )

        diagnosis_summary = (
            f"Se detectaron {len(scored_gaps)} brechas clínicas durante la evaluación diagnóstica. "
            f"Prioridad formativa en: {', '.join(set(g['competency_name'] for g in top_gaps[:2]))}. "
            f"El plan prescribe lecturas normativas específicas de las GPC del MSP y casos en ZDP para nivelación integral."
            if scored_gaps else
            "Diagnóstico de entrada satisfactorio sin omisiones críticas detectadas. Plan orientado a consolidación de maestría clínica avanzada."
        )

        return {
            "title": plan_title,
            "diagnosis_summary": diagnosis_summary,
            "target_duration_days": 7,
            "scored_gaps": scored_gaps,
            "tasks": tasks_payload
        }
