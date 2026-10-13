import { Link } from 'react-router-dom';
import { ArrowRight, Layers, Stethoscope } from 'lucide-react';
import type { ExtendedClinicalCase, GpcMeta, ViewMode } from '../hooks/useCases';

export interface CaseCardProps {
  caso: ExtendedClinicalCase;
  gpcMeta?: GpcMeta;
  viewMode?: ViewMode;
}

/**
 * CaseCard — Tarjeta de caso clínico individual
 */
export default function CaseCard({ caso, gpcMeta, viewMode = 'grid' }: CaseCardProps) {
  const isUrgent = gpcMeta?.isUrgent || false;
  const labelGpc = gpcMeta?.label || caso.guia_asociada || caso.gpc_referencia;

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
          className="relative block bg-white/95 backdrop-blur-xl rounded-[20px] p-5 shadow-xs border border-white/80 group-hover:border-white/90 group-hover:-translate-y-0.5 active:scale-[0.995] transition-all duration-300 focus:outline-none"
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="space-y-1.5 flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className={`text-xs font-semibold ${isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                  {labelGpc}
                </span>
                {caso.fases && (
                  <span className="text-[11px] font-medium text-[#0b57d0] inline-flex items-center gap-1">
                    <Layers className="w-3 h-3" />
                    3 Fases
                  </span>
                )}
              </div>
              <h3 className="text-base font-normal text-[#1f1f1f] group-hover:text-[#0b57d0] transition-colors truncate font-heading">
                {caso.titulo}
              </h3>
              <p className="text-xs text-[#747775] line-clamp-1 leading-relaxed">
                {caso.enunciado || caso.caso_preambulo}
              </p>
            </div>

            <div className="flex items-center shrink-0">
              <div className="w-8 h-8 rounded-full bg-[#f0f4f9] group-hover:bg-gradient-to-tr group-hover:from-cyan-600 group-hover:to-indigo-600 group-hover:text-white flex items-center justify-center transition-all duration-300 shadow-xs">
                <ArrowRight className="w-4 h-4" />
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
        className="relative flex flex-col h-full bg-white/95 backdrop-blur-xl rounded-[28px] p-6 shadow-xs border border-white/80 group-hover:border-white/90 group-hover:-translate-y-0.5 active:scale-[0.995] transition-all duration-300 justify-between focus:outline-none"
      >
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2">
            <span className={`text-xs font-semibold ${isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
              {labelGpc}
            </span>
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

          <div className="w-8 h-8 rounded-full bg-[#f0f4f9] group-hover:bg-gradient-to-tr group-hover:from-cyan-600 group-hover:to-indigo-600 group-hover:text-white flex items-center justify-center transition-all duration-300 shadow-xs">
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>
      </Link>
    </div>
  );
}
