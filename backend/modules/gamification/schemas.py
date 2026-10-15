from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AchievementDefinitionDTO(BaseModel):
    id: str
    codigo: str
    titulo: str
    descripcion: str
    categoria: str
    icono: str
    puntos_xp: int
    criterio_tipo: str
    criterio_valor: float
    activo: bool

    class Config:
        from_attributes = True


class UserAchievementProgressDTO(BaseModel):
    achievement_id: str
    codigo: str
    titulo: str
    descripcion: str
    categoria: str
    icono: str
    puntos_xp: int
    desbloqueado: bool
    desbloqueado_en: Optional[datetime] = None
    progreso_actual: float = 0.0
    meta: float = 1.0
    porcentaje: float = 0.0


class GamificationProfileDTO(BaseModel):
    user_id: str
    puntos_xp: int
    nivel_actual: int
    titulo_rango: str
    casos_resueltos: int
    racha_dias: int
    xp_actual_en_nivel: int
    xp_requerido_siguiente_nivel: int
    porcentaje_avance_nivel: float
    siguiente_rango: Optional[str] = None
    total_logros_desbloqueados: int
    total_logros_disponibles: int


class GamificationEvaluationEventResult(BaseModel):
    xp_ganados: int
    desglose_xp: dict
    subio_nivel: bool
    nuevo_nivel: Optional[int] = None
    nuevo_rango: Optional[str] = None
    nuevos_logros_desbloqueados: List[UserAchievementProgressDTO] = Field(default_factory=list)
