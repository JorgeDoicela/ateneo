import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct, or_
from datetime import datetime, timezone

from modules.gamification.repository import GamificationRepository
from modules.gamification.models import AchievementDefinitionModel
from modules.gamification.schemas import (
    GamificationProfileDTO,
    UserAchievementProgressDTO,
    GamificationEvaluationEventResult
)
from modules.analytics_history.models import EvaluationHistoryModel

logger = logging.getLogger(__name__)

# Escala de Niveles Formativos de Carrera Médica
CAREER_LEVELS = [
    {"level": 1, "title": "Estudiante Clínico Inicial", "min_xp": 0, "max_xp": 299},
    {"level": 2, "title": "Externo de Medicina", "min_xp": 300, "max_xp": 699},
    {"level": 3, "title": "Interno Rotativo", "min_xp": 700, "max_xp": 1299},
    {"level": 4, "title": "Médico General Novel", "min_xp": 1300, "max_xp": 2099},
    {"level": 5, "title": "Residente Clínico de Honor", "min_xp": 2100, "max_xp": 999999},
]


class GamificationService:
    """
    Servicio de Dominio de Gamificación Clínica y Progresión Formativa.
    Calcula de forma determinística los puntos de experiencia médica (XP),
    los rangos de carrera formativa y la adjudicación de hitos basados en GPC.
    """
    def __init__(self, repository: GamificationRepository, session: Optional[Session] = None):
        self.repo = repository
        self.session = session or repository.session

    @staticmethod
    def get_level_info_for_xp(xp: int) -> Dict[str, Any]:
        """Calcula el nivel actual, título y progreso porcentual dentro del nivel."""
        current_lvl = CAREER_LEVELS[0]
        for lvl in CAREER_LEVELS:
            if xp >= lvl["min_xp"]:
                current_lvl = lvl

        next_lvl = None
        current_idx = current_lvl["level"] - 1
        if current_idx + 1 < len(CAREER_LEVELS):
            next_lvl = CAREER_LEVELS[current_idx + 1]

        if next_lvl:
            xp_in_level = xp - current_lvl["min_xp"]
            needed = next_lvl["min_xp"] - current_lvl["min_xp"]
            pct = min(100.0, max(0.0, round((xp_in_level / needed) * 100, 1)))
        else:
            xp_in_level = xp - current_lvl["min_xp"]
            needed = 0
            pct = 100.0

        return {
            "level": current_lvl["level"],
            "title": current_lvl["title"],
            "xp_in_level": xp_in_level,
            "needed_for_next": needed,
            "percentage": pct,
            "next_title": next_lvl["title"] if next_lvl else None
        }

    def get_student_profile(self, user_id: str) -> GamificationProfileDTO:
        """Retorna el perfil consolidado del estudiante con métricas de carrera médica (reconcilia automáticamente contra historial real)."""
        if self.session:
            stmt_count = select(func.count(EvaluationHistoryModel.id)).where(
                or_(
                    EvaluationHistoryModel.user_id == user_id,
                    EvaluationHistoryModel.user_email == user_id
                )
            )
            history_count = self.session.execute(stmt_count).scalar_one() or 0
            profile = self.repo.get_profile(user_id)
            if history_count > 0 and (not profile or profile.casos_resueltos < history_count or profile.puntos_xp == 0):
                self.reconcile_student_progress_from_history(user_id)

        profile = self.repo.get_profile(user_id)
        unlocked_count = self.repo.count_user_achievements(user_id)
        all_defs = self.repo.get_all_active_definitions()

        if not profile:
            lvl_info = self.get_level_info_for_xp(0)
            return GamificationProfileDTO(
                user_id=user_id,
                puntos_xp=0,
                nivel_actual=lvl_info["level"],
                titulo_rango=lvl_info["title"],
                casos_resueltos=0,
                racha_dias=1,
                xp_actual_en_nivel=lvl_info["xp_in_level"],
                xp_requerido_siguiente_nivel=lvl_info["needed_for_next"],
                porcentaje_avance_nivel=lvl_info["percentage"],
                siguiente_rango=lvl_info["next_title"],
                total_logros_desbloqueados=unlocked_count,
                total_logros_disponibles=len(all_defs)
            )

        lvl_info = self.get_level_info_for_xp(profile.puntos_xp)
        return GamificationProfileDTO(
            user_id=user_id,
            puntos_xp=profile.puntos_xp,
            nivel_actual=lvl_info["level"],
            titulo_rango=lvl_info["title"],
            casos_resueltos=profile.casos_resueltos,
            racha_dias=profile.racha_dias,
            xp_actual_en_nivel=lvl_info["xp_in_level"],
            xp_requerido_siguiente_nivel=lvl_info["needed_for_next"],
            porcentaje_avance_nivel=lvl_info["percentage"],
            siguiente_rango=lvl_info["next_title"],
            total_logros_desbloqueados=unlocked_count,
            total_logros_disponibles=len(all_defs)
        )

    def get_student_achievements(self, user_id: str) -> List[UserAchievementProgressDTO]:
        """Retorna el catálogo completo de hitos clínicos con el estado de avance del usuario (reconcilia si no tiene logros pero sí historial)."""
        if self.session:
            unlocked_test = self.repo.get_user_unlocked_achievements(user_id)
            if not unlocked_test:
                stmt_count = select(func.count(EvaluationHistoryModel.id)).where(
                    or_(
                        EvaluationHistoryModel.user_id == user_id,
                        EvaluationHistoryModel.user_email == user_id
                    )
                )
                history_count = self.session.execute(stmt_count).scalar_one() or 0
                if history_count > 0:
                    self.reconcile_student_progress_from_history(user_id)

        all_defs = self.repo.get_all_active_definitions()
        unlocked = {u.achievement_id: u for u in self.repo.get_user_unlocked_achievements(user_id)}

        results: List[UserAchievementProgressDTO] = []
        for defn in all_defs:
            is_unlocked = defn.id in unlocked
            unlock_record = unlocked.get(defn.id)
            desbloqueado_en = unlock_record.desbloqueado_en if unlock_record else None
            progreso = unlock_record.progreso_actual if unlock_record else 0.0
            meta = defn.criterio_valor
            pct = 100.0 if is_unlocked else min(99.0, max(0.0, round((progreso / meta) * 100, 1)))

            results.append(UserAchievementProgressDTO(
                achievement_id=defn.id,
                codigo=defn.codigo,
                titulo=defn.titulo,
                descripcion=defn.descripcion,
                categoria=defn.categoria,
                icono=defn.icono,
                puntos_xp=defn.puntos_xp,
                desbloqueado=is_unlocked,
                desbloqueado_en=desbloqueado_en,
                progreso_actual=progreso if not is_unlocked else meta,
                meta=meta,
                porcentaje=pct
            ))

        return results

    def reconcile_student_progress_from_history(self, user_id: str) -> None:
        """
        Reconcilia de forma idempotente la progresión formativa y los hitos del estudiante
        contrastando contra su historial real en EvaluationHistoryModel.
        Garantiza que cualquier evaluación histórica sume sus puntos de experiencia (XP)
        y desbloquee los hitos correspondientes.
        """
        if not self.session:
            return

        stmt = select(EvaluationHistoryModel).where(
            or_(
                EvaluationHistoryModel.user_id == user_id,
                EvaluationHistoryModel.user_email == user_id
            )
        ).order_by(EvaluationHistoryModel.id.asc())

        evals = list(self.session.execute(stmt).scalars().all())
        if not evals:
            return

        profile = self.repo.get_or_create_profile(user_id)

        # 1. Calcular XP acumulado de evaluaciones históricas
        total_eval_xp = 0
        for e in evals:
            xp_base = 50
            xp_score = int(round((e.score or 0.0) * 10))
            xp_faithfulness = 25 if (getattr(e, "faithfulness_score", None) and e.faithfulness_score >= 0.80) else 0
            xp_fases = 30 if getattr(e, "es_fases", False) else 0
            total_eval_xp += (xp_base + xp_score + xp_faithfulness + xp_fases)

        # 2. Evaluar y desbloquear hitos según el historial real
        total_casos = len(evals)
        distinct_gpc = set(e.guia_asociada for e in evals if e.guia_asociada)
        max_score = max((e.score or 0.0) for e in evals)

        achievements_to_unlock = []

        # Hito 1: Iniciación Clínica (>= 1 caso)
        if total_casos >= 1:
            achievements_to_unlock.append(("iniciacion_clinica", 1.0, 1.0))

        # Hito 2: Apego Normativo Estricto (score >= 9.0)
        if max_score >= 9.0:
            achievements_to_unlock.append(("apego_gpc_excelente", max_score, 9.0))

        # Hito 3: Constancia Formativa (>= 5 casos)
        if total_casos >= 5:
            achievements_to_unlock.append(("constancia_formativa", float(total_casos), 5.0))

        # Hito 4: Resolución Multidisciplinar (>= 3 GPCs)
        if len(distinct_gpc) >= 3:
            achievements_to_unlock.append(("resolucion_multidisciplinar", float(len(distinct_gpc)), 3.0))

        # Hito 5: Manejo de Emergencias Críticas (score >= 8.0 en emergencias, preeclampsia, shock o rojo)
        has_emergency = any(
            (e.score or 0.0) >= 8.0 and any(
                k in (e.case_id or "").lower() or k in (e.case_title or "").lower() or k in (e.guia_asociada or "").lower()
                for k in ["emergencia", "preeclampsia", "shock", "rojo", "hemorragia", "parto"]
            )
            for e in evals
        )
        if has_emergency:
            achievements_to_unlock.append(("manejo_emergencias", 1.0, 1.0))

        # Hito 6: Eficiencia en Urgencias (tiempo <= 300s y score >= 8.5)
        has_time_efficiency = any(
            (e.score or 0.0) >= 8.5 and 0 < getattr(e, "tiempo_segundos", 0.0) <= 300.0
            for e in evals
        )
        if has_time_efficiency:
            achievements_to_unlock.append(("eficiencia_urgencias", 1.0, 1.0))

        # Hito 7: Maestría Secuencial (simulación por fases)
        has_fases = any(getattr(e, "es_fases", False) for e in evals)
        if has_fases:
            achievements_to_unlock.append(("maestria_secuencial", 1.0, 1.0))

        # Desbloquear hitos y sumar sus XP
        total_ach_xp = 0
        for ach_id, current_val, target_val in achievements_to_unlock:
            model, _ = self.repo.unlock_achievement(user_id, ach_id, current_val, target_val)
            defn = self.repo.get_definition_by_id(ach_id)
            if defn:
                total_ach_xp += defn.puntos_xp

        # 3. Consolidar perfil final
        xp_total_consolidado = total_eval_xp + total_ach_xp
        profile.casos_resueltos = max(profile.casos_resueltos, total_casos)
        profile.puntos_xp = max(profile.puntos_xp, xp_total_consolidado)

        lvl_info = self.get_level_info_for_xp(profile.puntos_xp)
        profile.nivel_actual = lvl_info["level"]
        profile.titulo_rango = lvl_info["title"]
        self.repo.update_profile(profile)
        self.session.flush()

    def process_evaluation_event(
        self,
        user_id: str,
        case_id: str,
        score: float,
        faithfulness_score: Optional[float] = None,
        tiempo_segundos: float = 0.0,
        es_fases: bool = False,
        especialidad: Optional[str] = None,
        es_emergencia: bool = False
    ) -> GamificationEvaluationEventResult:
        """
        Procesa el impacto de una evaluación diagnóstica completada:
        1. Asigna puntos XP con desglose pedagógico.
        2. Actualiza el perfil acumulado del estudiante y detecta ascensos de rango.
        3. Verifica criterios y desbloquea hitos clínicos de forma idempotente.
        """
        profile = self.repo.get_or_create_profile(user_id)
        nivel_anterior = profile.nivel_actual

        # 1. Cálculo de XP formativo
        xp_base = 50
        xp_score = int(round(score * 10))  # Ej. 8.5 -> 85 XP
        xp_faithfulness = 25 if (faithfulness_score and faithfulness_score >= 0.80) else 0
        xp_fases = 30 if es_fases else 0
        xp_total_evento = xp_base + xp_score + xp_faithfulness + xp_fases

        desglose = {
            "base": xp_base,
            "calificacion": xp_score,
            "apego_gpc": xp_faithfulness,
            "simulacion_fases": xp_fases,
            "total": xp_total_evento
        }

        # 2. Actualizar perfil
        profile.puntos_xp += xp_total_evento
        profile.casos_resueltos += 1

        lvl_info = self.get_level_info_for_xp(profile.puntos_xp)
        subio_nivel = lvl_info["level"] > nivel_anterior
        profile.nivel_actual = lvl_info["level"]
        profile.titulo_rango = lvl_info["title"]
        self.repo.update_profile(profile)

        # 3. Evaluar y desbloquear hitos clínicos
        nuevos_logros: List[UserAchievementProgressDTO] = []

        # Hito 1: Iniciación Clínica (1er caso resuelto)
        if profile.casos_resueltos >= 1:
            _, recien = self.repo.unlock_achievement(user_id, "iniciacion_clinica", 1.0, 1.0)
            if recien:
                d = self.repo.get_definition_by_id("iniciacion_clinica")
                if d:
                    nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Hito 2: Apego Normativo Estricto (score >= 9.0)
        if score >= 9.0:
            _, recien = self.repo.unlock_achievement(user_id, "apego_gpc_excelente", score, 9.0)
            if recien:
                d = self.repo.get_definition_by_id("apego_gpc_excelente")
                if d:
                    nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Hito 3: Maestría Secuencial (simulación por fases completada)
        if es_fases:
            _, recien = self.repo.unlock_achievement(user_id, "maestria_secuencial", 1.0, 1.0)
            if recien:
                d = self.repo.get_definition_by_id("maestria_secuencial")
                if d:
                    nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Hito 4: Eficiencia en Urgencias (tiempo <= 300s y score >= 8.5)
        if 0 < tiempo_segundos <= 300.0 and score >= 8.5:
            _, recien = self.repo.unlock_achievement(user_id, "eficiencia_urgencias", 1.0, 1.0)
            if recien:
                d = self.repo.get_definition_by_id("eficiencia_urgencias")
                if d:
                    nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Hito 5: Manejo de Emergencias Críticas (Código Rojo y score >= 8.0)
        if es_emergencia and score >= 8.0:
            _, recien = self.repo.unlock_achievement(user_id, "manejo_emergencias", 1.0, 1.0)
            if recien:
                d = self.repo.get_definition_by_id("manejo_emergencias")
                if d:
                    nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Hito 6: Constancia Formativa (>= 5 casos resueltos)
        if profile.casos_resueltos >= 5:
            _, recien = self.repo.unlock_achievement(user_id, "constancia_formativa", float(profile.casos_resueltos), 5.0)
            if recien:
                d = self.repo.get_definition_by_id("constancia_formativa")
                if d:
                    nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Hito 7: Resolución Multidisciplinar (>= 3 guías o especialidades evaluadas)
        if self.session:
            stmt_spec = select(func.count(distinct(EvaluationHistoryModel.guia_asociada))).where(
                EvaluationHistoryModel.user_id == user_id
            )
            count_spec = self.session.execute(stmt_spec).scalar_one() or 0
            if count_spec >= 3:
                _, recien = self.repo.unlock_achievement(user_id, "resolucion_multidisciplinar", float(count_spec), 3.0)
                if recien:
                    d = self.repo.get_definition_by_id("resolucion_multidisciplinar")
                    if d:
                        nuevos_logros.append(self._dto_from_def(d, datetime.now(timezone.utc)))

        # Si se desbloquearon hitos, sumar sus XP al perfil
        if nuevos_logros:
            extra_xp = sum(item.puntos_xp for item in nuevos_logros)
            profile.puntos_xp += extra_xp
            lvl_info_final = self.get_level_info_for_xp(profile.puntos_xp)
            if lvl_info_final["level"] > profile.nivel_actual:
                subio_nivel = True
                profile.nivel_actual = lvl_info_final["level"]
                profile.titulo_rango = lvl_info_final["title"]
            self.repo.update_profile(profile)

        return GamificationEvaluationEventResult(
            xp_ganados=xp_total_evento,
            desglose_xp=desglose,
            subio_nivel=subio_nivel,
            nuevo_nivel=profile.nivel_actual if subio_nivel else None,
            nuevo_rango=profile.titulo_rango if subio_nivel else None,
            nuevos_logros_desbloqueados=nuevos_logros
        )

    def process_socratic_session_event(self, user_id: str) -> Optional[UserAchievementProgressDTO]:
        """Registra el hito de Pensamiento Crítico Socrático al interactuar en el debriefing."""
        _, recien = self.repo.unlock_achievement(user_id, "pensamiento_socratico", 1.0, 1.0)
        if recien:
            d = self.repo.get_definition_by_id("pensamiento_socratico")
            if d:
                profile = self.repo.get_or_create_profile(user_id)
                profile.puntos_xp += d.puntos_xp
                lvl_info = self.get_level_info_for_xp(profile.puntos_xp)
                profile.nivel_actual = lvl_info["level"]
                profile.titulo_rango = lvl_info["title"]
                self.repo.update_profile(profile)
                return self._dto_from_def(d, datetime.now(timezone.utc))
        return None

    @staticmethod
    def _dto_from_def(d: AchievementDefinitionModel, dt: datetime) -> UserAchievementProgressDTO:
        return UserAchievementProgressDTO(
            achievement_id=d.id,
            codigo=d.codigo,
            titulo=d.titulo,
            descripcion=d.descripcion,
            categoria=d.categoria,
            icono=d.icono,
            puntos_xp=d.puntos_xp,
            desbloqueado=True,
            desbloqueado_en=dt,
            progreso_actual=d.criterio_valor,
            meta=d.criterio_valor,
            porcentaje=100.0
        )
