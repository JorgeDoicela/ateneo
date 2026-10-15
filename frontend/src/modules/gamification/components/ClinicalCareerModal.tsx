import React, { useEffect, useState, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { 
  X, 
  Award, 
  Stethoscope, 
  Layers, 
  Compass, 
  MessageSquare, 
  Zap, 
  ShieldCheck, 
  AlertCircle, 
  CheckCircle2, 
  Lock, 
  GraduationCap,
  Sparkles
} from 'lucide-react';
import { gamificationApi } from '../api/gamificationApi';
import type { GamificationProfile, UserAchievementProgress } from '../types';

export interface ClinicalCareerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Stethoscope,
  Award,
  Layers,
  Compass,
  MessageSquare,
  Zap,
  ShieldCheck,
  AlertCircle,
  GraduationCap
};

const CAREER_LEVELS_STEPS = [
  { level: 1, title: 'Inicial', minXp: 0 },
  { level: 2, title: 'Externo', minXp: 300 },
  { level: 3, title: 'Interno', minXp: 700 },
  { level: 4, title: 'Médico', minXp: 1300 },
  { level: 5, title: 'Residente', minXp: 2100 }
];

export default function ClinicalCareerModal({ isOpen, onClose }: ClinicalCareerModalProps) {
  const [profile, setProfile] = useState<GamificationProfile | null>(null);
  const [achievements, setAchievements] = useState<UserAchievementProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('todos');

  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setLoading(true);

    Promise.all([
      gamificationApi.getProfile(),
      gamificationApi.getAchievements()
    ])
      .then(([profData, achData]) => {
        if (isMounted) {
          setProfile(profData);
          setAchievements(achData);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Error al cargar datos de carrera formativa:', err);
        if (isMounted) setLoading(false);
      });

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';

    return () => {
      isMounted = false;
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  const categories = useMemo(() => {
    return [
      { id: 'todos', label: 'Todos los Hitos' },
      { id: 'diagnostico', label: 'Diagnóstico' },
      { id: 'excelencia', label: 'Excelencia GPC' },
      { id: 'fases', label: 'Simulación por Fases' },
      { id: 'especialidad', label: 'Especialidades' },
      { id: 'constancia', label: 'Constancia' }
    ];
  }, []);

  const filteredAchievements = useMemo(() => {
    if (selectedCategory === 'todos') return achievements;
    return achievements.filter((a) => a.categoria === selectedCategory);
  }, [achievements, selectedCategory]);

  const unlockedCount = useMemo(() => {
    return achievements.filter((a) => a.desbloqueado).length;
  }, [achievements]);

  if (!isOpen) return null;

  return createPortal(
    <div
      className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-fadeIn"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="career-modal-title"
    >
      <div
        className="bg-white rounded-[28px] sm:rounded-[32px] shadow-2xl border border-slate-200/60 max-w-2xl w-full p-5 sm:p-7 flex flex-col max-h-[90vh] animate-scaleUp relative overflow-hidden space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Halos difusos sutiles de fondo para refracción Glassmorphism (Idéntico a JoinRoomModal) */}
        <div
          className="pointer-events-none absolute -top-12 -right-12 w-56 h-56 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -bottom-10 -left-10 w-56 h-56 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />

        {/* Cabecera del Diálogo */}
        <div className="flex items-center justify-between border-b border-slate-100/90 pb-3 relative z-10 shrink-0">
          <div className="flex items-center gap-2.5 min-w-0">
            <GraduationCap className="w-5 h-5 text-blue-600 shrink-0" />
            <div className="min-w-0">
              <h3 id="career-modal-title" className="text-lg font-heading font-normal text-slate-900 tracking-tight truncate">
                Carrera Formativa e Hitos Clínicos
              </h3>
              <p className="text-xs text-slate-500 truncate">
                Sendero de progresión médica y reconocimientos anclados en GPC Ecuador
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer transition-colors shrink-0 ml-2"
            title="Cerrar modal"
            aria-label="Cerrar modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Cuerpo del Diálogo con Scroll Limpio */}
        <div className="flex-1 overflow-y-auto no-scrollbar space-y-4 relative z-10 pr-0.5">
          {loading ? (
            <div className="py-20 text-center text-slate-400 animate-pulse text-xs">
              Cargando sendero de carrera y estado de hitos formativos...
            </div>
          ) : (
            <>
              {/* Hero: Resumen del Rango Actual y Sendero Conectado de Niveles */}
              {profile && (
                <div className="rounded-[22px] bg-slate-50/80 border border-slate-100/90 p-4 sm:p-5 space-y-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200/60">
                          Nivel {profile.nivel_actual}
                        </span>
                        <span className="text-[11px] text-slate-400 font-medium">
                          {profile.casos_resueltos} {profile.casos_resueltos === 1 ? 'caso completado' : 'casos completados'}
                        </span>
                      </div>
                      <h4 className="text-base sm:text-lg font-semibold text-slate-900 tracking-tight truncate">
                        {profile.titulo_rango}
                      </h4>
                      {profile.siguiente_rango && (
                        <p className="text-xs text-slate-500">
                          Próximo rango: <span className="font-medium text-slate-700">{profile.siguiente_rango}</span>
                        </p>
                      )}
                    </div>

                    <div className="text-right shrink-0">
                      <span className="text-[10px] text-slate-400 block font-medium uppercase tracking-wider">Puntos XP</span>
                      <span className="text-xl sm:text-2xl font-mono font-bold text-slate-900">
                        {profile.puntos_xp} <span className="text-xs font-sans font-semibold text-blue-600">XP</span>
                      </span>
                    </div>
                  </div>

                  {/* Sendero Visual de Mini-Niveles (Conectores Gamificados) */}
                  <div className="pt-2 border-t border-slate-200/50">
                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium mb-2.5">
                      <span className="flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                        <span>Sendero de Carrera Médica</span>
                      </span>
                      <span className="font-mono text-slate-700 font-semibold">
                        {profile.porcentaje_avance_nivel}% completado
                      </span>
                    </div>

                    {/* Barra de sendero con estaciones */}
                    <div className="relative flex items-center justify-between px-3 sm:px-6">
                      <div className="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-1 bg-slate-200/80 z-0" />
                      <div
                        className="absolute left-6 top-1/2 -translate-y-1/2 h-1 bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 z-0 transition-all duration-500"
                        style={{
                          width: `${Math.min(
                            100,
                            Math.max(0, ((profile.nivel_actual - 1) / (CAREER_LEVELS_STEPS.length - 1)) * 100)
                          )}%`
                        }}
                      />

                      {CAREER_LEVELS_STEPS.map((st) => {
                        const isPassed = profile.nivel_actual > st.level;
                        const isCurrent = profile.nivel_actual === st.level;
                        const isLocked = profile.nivel_actual < st.level;

                        return (
                          <div key={st.level} className="relative z-10 flex flex-col items-center">
                            <div
                              className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all shadow-xs ${
                                isCurrent
                                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white ring-4 ring-blue-100 scale-110'
                                  : isPassed
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-white border-2 border-slate-200 text-slate-400'
                              }`}
                              title={`Nivel ${st.level}: ${st.title} (${st.minXp} XP)`}
                            >
                              {isPassed ? (
                                <CheckCircle2 className="w-4 h-4" />
                              ) : isLocked ? (
                                <Lock className="w-3 h-3 text-slate-300" />
                              ) : (
                                <span>{st.level}</span>
                              )}
                            </div>
                            <span
                              className={`text-[10px] mt-1 font-medium hidden sm:block truncate max-w-[70px] text-center ${
                                isCurrent
                                  ? 'text-blue-600 font-bold'
                                  : isPassed
                                  ? 'text-slate-700'
                                  : 'text-slate-400'
                              }`}
                            >
                              {st.title}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Filtros de Categoría: Píldoras fluidas */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                  {categories.map((cat) => {
                    const isSelected = selectedCategory === cat.id;
                    return (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => setSelectedCategory(cat.id)}
                        className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer select-none ${
                          isSelected
                            ? 'bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-xs'
                            : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200/70'
                        }`}
                      >
                        {cat.label}
                      </button>
                    );
                  })}
                </div>

                <span className="text-[11px] font-medium text-slate-400 hidden sm:block">
                  Hitos: <strong className="text-slate-700 font-mono">{unlockedCount}/{achievements.length}</strong>
                </span>
              </div>

              {/* El Sendero de Hitos Clínicos (Camino Conectado de Logros) */}
              <div className="space-y-3 pt-2">
                {filteredAchievements.map((ach, idx) => {
                  const IconComp = ICON_MAP[ach.icono] || Award;
                  const isLast = idx === filteredAchievements.length - 1;

                  return (
                    <div key={ach.achievement_id} className="relative flex items-start gap-3 sm:gap-4">
                      {/* Línea conectora del sendero vertical */}
                      {!isLast && (
                        <div
                          className={`absolute left-4 top-8 bottom-[-16px] w-0.5 z-0 transition-colors ${
                            ach.desbloqueado ? 'bg-blue-600/70' : 'bg-slate-200'
                          }`}
                        />
                      )}

                      {/* Nodo de la estación del camino */}
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 z-10 transition-all ${
                          ach.desbloqueado
                            ? 'bg-blue-600 text-white ring-4 ring-blue-50 shadow-xs'
                            : 'bg-white border-2 border-slate-200 text-slate-400'
                        }`}
                      >
                        {ach.desbloqueado ? (
                          <CheckCircle2 className="w-4 h-4 text-white" />
                        ) : (
                          <Lock className="w-3.5 h-3.5 text-slate-400" />
                        )}
                      </div>

                      {/* Tarjeta de Hito Clínico */}
                      <div
                        className={`flex-1 p-3.5 sm:p-4 rounded-[20px] transition-all border ${
                          ach.desbloqueado
                            ? 'bg-blue-50/30 border-blue-200/80 shadow-2xs'
                            : 'bg-slate-50/60 border-slate-200/70 hover:border-slate-300'
                        }`}
                      >
                        <div className="flex items-start gap-2.5">
                          <IconComp
                            className={`w-4 h-4 shrink-0 mt-0.5 ${
                              ach.desbloqueado ? 'text-blue-600' : 'text-slate-400'
                            }`}
                          />
                          <div className="min-w-0 flex-1 space-y-0.5">
                            <div className="flex items-baseline justify-between gap-2">
                              <h5 className="text-xs sm:text-sm font-semibold text-slate-900 tracking-tight leading-snug">
                                {ach.titulo}
                              </h5>
                              <span className="text-[10px] font-mono font-bold text-blue-600 shrink-0">
                                +{ach.puntos_xp} XP
                              </span>
                            </div>
                            <p className="text-[11px] sm:text-xs text-slate-500 leading-relaxed">
                              {ach.descripcion}
                            </p>
                          </div>
                        </div>

                        {/* Pie de la estación de hito */}
                        <div className="mt-2 pt-2 border-t border-slate-200/50 flex items-center justify-between text-[11px]">
                          {ach.desbloqueado ? (
                            <span className="inline-flex items-center gap-1.5 text-emerald-700 font-medium text-[10px] sm:text-[11px]">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                              <span>Desbloqueado</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-slate-400 text-[10px] sm:text-[11px]">
                              <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                              <span>Pendiente</span>
                            </span>
                          )}

                          {ach.desbloqueado_en && (
                            <span className="text-[10px] text-slate-400 font-mono">
                              {new Date(ach.desbloqueado_en).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Pie del Diálogo con botón institucional */}
        <div className="pt-2 border-t border-slate-100 flex justify-end relative z-10 shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 rounded-full border border-slate-200 text-slate-700 bg-white hover:bg-slate-50 text-xs font-medium cursor-pointer transition-colors shadow-2xs"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
