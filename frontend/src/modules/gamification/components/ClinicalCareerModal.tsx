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
  GraduationCap
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
                Reconocimientos académicos y progresión diagnóstica anclada en GPC Ecuador
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
              Cargando perfil formativo y estado de hitos clínicos...
            </div>
          ) : (
            <>
              {/* Hero: Resumen de Rango y Progreso de XP */}
              {profile && (
                <div className="rounded-[22px] bg-slate-50/80 border border-slate-100/90 p-4 sm:p-5 space-y-3">
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
                          Siguiente rango: <span className="font-medium text-slate-700">{profile.siguiente_rango}</span>
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

                  {/* Barra de Progreso */}
                  <div className="space-y-1 pt-1.5 border-t border-slate-200/60">
                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                      <span>Progreso de Nivel</span>
                      <span className="font-mono">{profile.porcentaje_avance_nivel}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-200/70 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 rounded-full transition-all duration-500"
                        style={{ width: `${profile.porcentaje_avance_nivel}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Selector de Categorías (Píldoras adaptativas fluidas que nunca se tapan ni se cortan) */}
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

              {/* Cuadrícula de Hitos Clínicos */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3">
                {filteredAchievements.map((ach) => {
                  const IconComp = ICON_MAP[ach.icono] || Award;
                  return (
                    <div
                      key={ach.achievement_id}
                      className={`p-3.5 sm:p-4 rounded-[20px] transition-all flex flex-col justify-between gap-3 ${
                        ach.desbloqueado
                          ? 'bg-emerald-50/40 border border-emerald-200/80 shadow-2xs'
                          : 'bg-slate-50/60 border border-slate-200/70 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <IconComp 
                          className={`w-5 h-5 shrink-0 mt-0.5 ${
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

                      {/* Pie de la tarjeta */}
                      <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
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
