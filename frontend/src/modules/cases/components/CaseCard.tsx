import { Link } from 'react-router-dom';
import { ArrowRight, Layers, Stethoscope, CheckCircle2, Clock } from 'lucide-react';
import type { ExtendedClinicalCase, GpcMeta, ViewMode } from '../hooks/useCases';

export interface CaseCardProps {
  caso: ExtendedClinicalCase;
  gpcMeta?: GpcMeta;
  viewMode?: ViewMode;
}

/**
 * CaseCard — Tarjeta de caso clínico individual
 * Presenta estado de avance (Completado, En progreso o Por resolver) con diseño institucional plano.
 */
export default function CaseCard({ caso, gpcMeta, viewMode = 'grid' }: CaseCardProps) {
  const isUrgent = gpcMeta?.isUrgent || false;
  const labelGpc = gpcMeta?.label || caso.guia_asociada || caso.gpc_referencia;

  const progress = caso.progress;
  const isCompleted = progress?.status === 'completed';
  const isInProgress = progress?.status === 'in_progress';
  const actionText = isCompleted ? 'Revisar' : isInProgress ? 'Continuar' : 'Resolver';

  if (viewMode === 'list') {
    return (
      <div className="relative group">
        {/* Halo de Iluminación Ambiental Líquido con Barrido hacia la Derecha (Adaptativo Móvil/Escritorio) */}
        <div 
          className="absolute -inset-1.5 bg-[linear-gradient(90deg,rgba(6,182,212,0.35)_0%,rgba(37,99,235,0.3)_33%,rgba(124,58,237,0.35)_66%,rgba(6,182,212,0.35)_100%)] animate-liquid-wave rounded-[24px] blur-xl opacity-0 touch-ambient-glow group-hover:opacity-65 group-active:opacity-85 transition-opacity duration-300 pointer-events-none" 
          aria-hidden="true"
        />

        <Link
          to={`/cases/${caso.id}`}
          className="relative block bg-white/95 backdrop-blur-xl rounded-[20px] p-4 sm:p-5 shadow-xs border border-white/80 group-hover:border-white/90 active:scale-[0.995] transition-all duration-300 focus:outline-none"
        >
          <div className="flex items-center justify-between gap-3 sm:gap-4">
            <div className="space-y-1 sm:space-y-1.5 flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                <span className={`text-[11px] sm:text-xs font-semibold ${isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                  {labelGpc}
                </span>
                {caso.fases && (
                  <span className="text-[10px] sm:text-[11px] font-medium text-[#0b57d0] inline-flex items-center gap-1">
                    <Layers className="w-3 h-3" />
                    3 Fases
                  </span>
                )}
                {isCompleted && (
                  <span className="text-[10px] sm:text-[11px] font-semibold text-emerald-600 inline-flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    Completado • {progress?.score}/10
                  </span>
                )}
                {isInProgress && (
                  <span className="text-[10px] sm:text-[11px] font-semibold text-amber-600 inline-flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    En progreso • Fase {progress?.currentPhase}/3
                  </span>
                )}
              </div>
              <h3 className="text-sm sm:text-base font-normal text-[#1f1f1f] group-hover:text-[#0b57d0] transition-colors line-clamp-2 sm:truncate font-heading leading-snug">
                {caso.titulo}
              </h3>
              <p className="text-xs text-[#444746] line-clamp-2 sm:line-clamp-1 leading-relaxed">
                {caso.enunciado || caso.caso_preambulo}
              </p>
            </div>

            <div className="flex items-center shrink-0 self-center">
              <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-xs shadow-blue-500/20 group-hover:shadow-md group-hover:shadow-blue-500/30 group-hover:scale-[1.02] active:scale-[0.98] transition-all duration-300">
                <span className="hidden sm:inline">{actionText}</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
              </div>
            </div>
          </div>
        </Link>
      </div>
    );
  }

  return (
    <div className="relative group flex flex-col h-full">
      {/* Halo de Iluminación Ambiental Líquido con Barrido hacia la Derecha (Adaptativo Móvil/Escritorio) */}
      <div 
        className="absolute -inset-1.5 bg-[linear-gradient(90deg,rgba(6,182,212,0.35)_0%,rgba(37,99,235,0.3)_33%,rgba(124,58,237,0.35)_66%,rgba(6,182,212,0.35)_100%)] animate-liquid-wave rounded-[32px] blur-xl opacity-0 touch-ambient-glow group-hover:opacity-65 group-active:opacity-85 transition-opacity duration-300 pointer-events-none" 
        aria-hidden="true"
      />

      <Link
        to={`/cases/${caso.id}`}
        className="relative flex flex-col h-full bg-white/95 backdrop-blur-xl rounded-[28px] p-6 shadow-xs border border-white/80 group-hover:border-white/90 active:scale-[0.995] transition-all duration-300 justify-between focus:outline-none"
      >
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <span className={`text-xs font-semibold ${isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
              {labelGpc}
            </span>
            {isCompleted && (
              <span className="text-xs font-semibold text-emerald-600 inline-flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                Completado • {progress?.score}/10
              </span>
            )}
            {isInProgress && (
              <span className="text-xs font-semibold text-amber-600 inline-flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                En progreso • Fase {progress?.currentPhase}/3
              </span>
            )}
          </div>

          <h3 className="text-lg font-normal text-[#1f1f1f] group-hover:text-[#0b57d0] transition-colors line-clamp-2 font-heading leading-snug">
            {caso.titulo}
          </h3>

          <p className="text-xs text-[#444746] line-clamp-3 leading-relaxed">
            {caso.enunciado || caso.caso_preambulo}
          </p>
        </div>

        <div className="pt-4 border-t border-slate-100 flex items-center justify-between mt-4">
          {caso.fases ? (
            <span className="text-xs font-medium text-[#0b57d0] inline-flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              Simulación 3 Fases
            </span>
          ) : (
            <span className="text-xs text-[#747775] flex items-center gap-1.5">
              <Stethoscope className="w-3.5 h-3.5 text-[#0b57d0]" />
              Caso Clínico Estándar
            </span>
          )}

          <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-xs shadow-blue-500/20 group-hover:shadow-md group-hover:shadow-blue-500/30 group-hover:scale-[1.02] active:scale-[0.98] transition-all duration-300">
            <span>{actionText}</span>
            <ArrowRight className="w-3.5 h-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
          </div>
        </div>
      </Link>
    </div>
  );
}
