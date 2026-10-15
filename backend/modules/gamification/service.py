import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, distinct
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
        """Retorna el perfil consolidado del estudiante con métricas de carrera médica."""
        profile = self.repo.get_or_create_profile(user_id)
        lvl_info = self.get_level_info_for_xp(profile.puntos_xp)
        unlocked_count = self.repo.count_user_achievements(user_id)
        all_defs = self.repo.get_all_active_definitions()

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
        """Retorna el catálogo completo de hitos clínicos con el estado de avance del usuario."""
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
