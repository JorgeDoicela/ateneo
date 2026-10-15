export interface GamificationProfile {
  user_id: string;
  puntos_xp: number;
  nivel_actual: number;
  titulo_rango: string;
  casos_resueltos: number;
  racha_dias: number;
  xp_actual_en_nivel: number;
  xp_requerido_siguiente_nivel: number;
  porcentaje_avance_nivel: number;
  siguiente_rango: string | null;
  total_logros_desbloqueados: number;
  total_logros_disponibles: number;
}

export interface UserAchievementProgress {
  achievement_id: string;
  codigo: string;
  titulo: string;
  descripcion: string;
  categoria: 'diagnostico' | 'excelencia' | 'fases' | 'especialidad' | 'dialogo' | 'agilidad' | 'constancia' | 'emergencias' | string;
  icono: string;
  puntos_xp: number;
  desbloqueado: boolean;
  desbloqueado_en: string | null;
  progreso_actual: number;
  meta: number;
  porcentaje: number;
}

export interface CareerLevelInfo {
  level: number;
  title: string;
  min_xp: number;
  max_xp: number;
}
