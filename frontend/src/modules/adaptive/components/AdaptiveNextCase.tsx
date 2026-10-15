import { useState, useEffect } from 'react';
import { ChevronRight } from 'lucide-react';
import { adaptiveApi } from '../api/adaptiveApi';
import { useAuth } from '../../../context/AuthContext';
import type { ZDPRecommendation, ClinicalCase } from '../../../types';

export interface AdaptiveNextCaseProps {
  onSelectCase: (clinicalCase: ClinicalCase) => void;
  onToggleGraph?: () => void;
}

export default function AdaptiveNextCase({ onSelectCase, onToggleGraph }: AdaptiveNextCaseProps) {
  const { user } = useAuth();
  const [recommendation, setRecommendation] = useState<ZDPRecommendation | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    async function loadRecommendation() {
      try {
        setLoading(true);
        const data = await adaptiveApi.getNextCase(user?.id);
        if (isMounted) {
          setRecommendation(data);
        }
      } catch (err) {
        console.error('Error cargando recomendación adaptativa:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRecommendation();
    return () => { isMounted = false; };
  }, [user?.id]);

  if (loading) {
    return (
      <div className="relative w-full mb-8">
        {/* Halo estático suave mientras carga */}
        <div 
          className="absolute -inset-1.5 bg-gradient-to-r from-cyan-400/10 via-blue-500/10 to-violet-500/10 rounded-[32px] blur-xl opacity-40 pointer-events-none" 
          aria-hidden="true"
        />
        <div className="relative w-full bg-white/95 backdrop-blur-xl rounded-[24px] sm:rounded-[28px] border border-white/80 shadow-sm p-4 sm:p-6 md:p-7 animate-pulse">
          {/* Encabezado esqueleto */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100/80">
            <div className="h-3.5 bg-slate-200/70 rounded-full w-32"></div>
            <div className="h-3.5 bg-slate-200/50 rounded-full w-16"></div>
          </div>
          {/* Cuerpo esqueleto con dimensiones idénticas a la tarjeta final */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6 items-center pt-3.5">
            <div className="lg:col-span-8 space-y-2">
              <div className="h-5 sm:h-6 bg-slate-200/80 rounded-lg w-4/5 sm:w-3/5"></div>
              <div className="h-3 bg-slate-200/50 rounded-full w-56"></div>
            </div>
            <div className="lg:col-span-4 flex justify-end">
              <div className="h-10 bg-slate-200/70 rounded-[16px] w-full lg:w-32"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!recommendation || !recommendation.case) {
    return null;
  }

  const { case: clinicalCase, competencia_objetivo } = recommendation;

  return (
    <div className="relative w-full mb-8 group animate-fadeIn">
      {/* Halo de Iluminación Ambiental Líquido */}
      <div 
        className="absolute -inset-1 bg-[linear-gradient(90deg,rgba(6,182,212,0.25)_0%,rgba(37,99,235,0.2)_33%,rgba(124,58,237,0.25)_66%,rgba(6,182,212,0.25)_100%)] animate-liquid-wave rounded-[30px] blur-lg opacity-25 group-hover:opacity-60 transition-opacity duration-300 pointer-events-none" 
        aria-hidden="true"
      />

      {/* Tarjeta de Cristal Líquido */}
      <div className="relative w-full bg-white/95 backdrop-blur-xl rounded-[24px] sm:rounded-[28px] border border-white/80 shadow-sm p-4 sm:p-6 md:p-7 transition-all duration-300">
        {/* Encabezado Superior Compacto */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100/80">
          <span className="text-[11px] font-bold uppercase tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-600 via-blue-600 to-violet-600">
            Caso Recomendado
          </span>

          {onToggleGraph && (
            <button
              onClick={onToggleGraph}
              className="text-xs font-semibold text-[#0b57d0] hover:text-blue-700 transition-colors cursor-pointer inline-flex items-center gap-1 group/btn"
            >
              <span>Ver ruta</span>
              <ChevronRight className="w-3.5 h-3.5 text-blue-500 group-hover/btn:translate-x-0.5 transition-transform" />
            </button>
          )}
        </div>

        {/* Cuerpo Principal Simplificado */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6 items-center pt-3.5">
          <div className="lg:col-span-8 space-y-1.5">
            <h3 className="text-base sm:text-lg md:text-xl font-bold font-heading text-slate-900 tracking-tight leading-snug">
              {clinicalCase.titulo}
            </h3>

            <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500">
              <span className="text-slate-400">Competencia en entrenamiento:</span>
              <span className="text-slate-800 font-semibold capitalize">
                {competencia_objetivo?.nombre}
              </span>
              <span className="text-slate-300 font-light">•</span>
              <span className="text-slate-600 font-medium">
                {clinicalCase.especialidad || 'Medicina General'}
              </span>
              {clinicalCase.fases && clinicalCase.fases.length > 0 && (
                <>
                  <span className="text-slate-300 font-light">•</span>
                  <span className="text-slate-600 font-medium">
                    {clinicalCase.fases.length} Fases
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col items-stretch lg:items-end justify-center pt-1 lg:pt-0">
            <button
              onClick={() => onSelectCase(clinicalCase)}
              className="w-full lg:w-auto inline-flex items-center justify-center px-6 py-3 rounded-[16px] bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:via-blue-500 hover:to-indigo-500 text-white text-sm font-semibold shadow-sm hover:shadow-md transition-all duration-300 active:scale-[0.98] cursor-pointer min-h-[44px]"
            >
              <span>Resolver Caso</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
