import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import ReasoningTrends from '../components/ReasoningTrends';
import ClinicalButton from '../../../core/ui/ClinicalButton';

/**
 * StudentAnalyticsPage — Vista canónica de Desempeño y Tendencias Clínicas del Estudiante
 * Desacoplada de CaseList para deep-linking, historial y aislamiento de responsabilidades.
 */
export default function StudentAnalyticsPage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8 animate-fadeIn pb-16">
      {/* 1. Header Principal de Analítica Formativa */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 pt-2">
        <div>
          <h1 className="text-[28px] sm:text-[34px] font-normal tracking-tight text-[#1f1f1f] font-heading">
            Mi Desempeño y Tendencias
          </h1>
          <p className="text-sm font-normal text-[#444746] mt-1 max-w-2xl leading-relaxed">
            Diagnóstico formativo estructurado, radar de competencias clínicas y análisis longitudinal de brechas frente a las Guías de Práctica Clínica.
          </p>
        </div>

        {/* Acciones Rápidas */}
        <div className="flex items-center gap-3">
          <ClinicalButton
            variant="secondary"
            onClick={() => navigate('/cases')}
            icon={ArrowLeft}
          >
            Volver al Catálogo
          </ClinicalButton>
        </div>
      </div>

      {/* 2. Núcleo Analítico Longitudinal y Radar de Competencias */}
      <div className="space-y-6">
        <ReasoningTrends />
      </div>
    </div>
  );
}
