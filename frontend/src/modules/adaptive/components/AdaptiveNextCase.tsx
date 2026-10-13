import { useState, useEffect } from 'react';
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
      <div className="w-full bg-white rounded-[24px] border border-slate-200/80 p-6 animate-pulse mb-8 shadow-sm">
        <div className="h-4 bg-slate-200 rounded w-1/4 mb-4"></div>
        <div className="h-6 bg-slate-200 rounded w-3/4 mb-3"></div>
        <div className="h-4 bg-slate-100 rounded w-1/2"></div>
      </div>
    );
  }

  if (!recommendation || !recommendation.case) {
    return null;
  }

  const { case: clinicalCase, competencia_objetivo, promedio_dominio_global } = recommendation;
  const pPct = Math.round((competencia_objetivo?.p_dominio || 0.4) * 100);

  return (
    <div className="relative w-full mb-8 group">
      {/* Halo de Iluminación Ambiental Líquido con Barrido hacia la Derecha (Adaptativo Móvil/Escritorio) */}
      <div 
        className="absolute -inset-1.5 bg-[linear-gradient(90deg,rgba(6,182,212,0.35)_0%,rgba(37,99,235,0.3)_33%,rgba(124,58,237,0.35)_66%,rgba(6,182,212,0.35)_100%)] animate-liquid-wave rounded-[32px] blur-xl opacity-30 touch-ambient-glow group-hover:opacity-75 group-active:opacity-95 transition-opacity duration-300 pointer-events-none" 
        aria-hidden="true"
      />

      {/* Tarjeta de Cristal Líquido (Liquid Glassmorphism) */}
      <div className="relative w-full bg-white/90 backdrop-blur-xl rounded-[28px] border border-white/80 shadow-sm p-6 md:p-8 transition-all duration-300 active:scale-[0.995]">
        {/* Encabezado Superior */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="font-bold uppercase tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-600 via-blue-600 to-violet-600">
              Caso Recomendado
            </span>
            <span className="text-slate-300 font-light">•</span>
            <span className="text-slate-500 font-medium">
              {Math.round(promedio_dominio_global * 100)}% de avance global
            </span>
          </div>

          {onToggleGraph && (
            <button
              onClick={onToggleGraph}
              className="text-xs font-semibold text-slate-700 hover:text-blue-600 transition-colors cursor-pointer"
            >
              <span>Ver Ruta de Competencias</span>
            </button>
          )}
        </div>

        {/* Cuerpo Principal */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center pt-4">
          <div className="lg:col-span-8 space-y-2.5">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-500 font-medium">Objetivo a entrenar:</span>
              <span className="text-slate-900 font-bold capitalize">
                {competencia_objetivo?.nombre} ({pPct}%)
              </span>
            </div>

            <h3 className="text-xl md:text-2xl font-bold font-heading text-slate-900 tracking-tight leading-snug">
              {clinicalCase.titulo}
            </h3>

            <div className="flex flex-wrap items-center gap-3 pt-0.5 text-xs text-slate-600">
              <span className="font-medium text-slate-700">{clinicalCase.especialidad || 'Medicina General'}</span>
              <span className="text-slate-300 font-light">•</span>
              <span className="font-medium text-slate-700">Dificultad {clinicalCase.dificultad || 'Intermedia'}</span>
              {clinicalCase.fases && (
                <>
                  <span className="text-slate-300 font-light">•</span>
                  <span className="text-blue-700 font-semibold">
                    3 Fases Clínicas
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col items-start lg:items-end justify-center">
            <button
              onClick={() => onSelectCase(clinicalCase)}
              className="w-full lg:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-[18px] bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-500 hover:via-blue-500 hover:to-indigo-500 text-white text-sm font-semibold shadow-md shadow-blue-600/20 hover:shadow-lg hover:shadow-indigo-600/30 transition-all duration-300 active:scale-[0.98] cursor-pointer"
            >
              <span>Resolver Caso</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
