import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ReasoningTrends from '../components/ReasoningTrends';

/**
 * StudentAnalyticsPage — Vista canónica de Desempeño y Tendencias Clínicas del Estudiante
 * Desacoplada de CaseList para deep-linking, historial y aislamiento de responsabilidades.
 */
export default function StudentAnalyticsPage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8 animate-fadeIn pb-16">
      {/* 1. Navegación Superior y Header Principal */}
      <div className="space-y-3 pb-2 pt-1">
        <div>
          <button
            type="button"
            onClick={() => navigate('/cases')}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200 bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-[#0b57d0] border border-blue-200/60 hover:border-blue-300/90 shadow-xs hover:shadow-sm cursor-pointer select-none"
          >
            <ArrowLeft className="w-3.5 h-3.5 text-[#0b57d0]" />
            <span>Volver al Catálogo</span>
          </button>
        </div>

        <div>
          <h1 className="text-[28px] sm:text-[34px] font-normal tracking-tight text-[#1f1f1f] font-heading">
            Mi Desempeño y Tendencias
          </h1>
          <p className="text-sm font-normal text-[#444746] mt-1 max-w-2xl leading-relaxed">
            Diagnóstico formativo estructurado, radar de competencias clínicas y análisis longitudinal de brechas frente a las Guías de Práctica Clínica.
          </p>
        </div>
      </div>

      {/* 2. Núcleo Analítico Longitudinal y Radar de Competencias */}
      <div className="space-y-6">
        <ReasoningTrends />
      </div>
    </div>
  );
}
