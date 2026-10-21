import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Activity, 
  ClipboardCheck, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles,
  Award
} from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import { studyPlanApi } from '../../study_plans/api/studyPlanApi';
import { assessmentApi } from '../../assessments/api/assessmentApi';
import { HakeGainBadge } from '../../assessments/components/HakeGainBadge';

/**
 * DiagnosticPreTestBanner — Banner contextual de Nivelación y Plan Prescriptivo
 * Se proyecta en la parte superior del catálogo de casos para guiar proactivamente
 * el flujo del estudiante:
 * 1. Si no tiene Pre-Test previo: Invita a iniciar la Batería Troncal CACES.
 * 2. Si tiene un Plan Prescriptivo en curso: Muestra progreso y acceso a tareas.
 * 3. Si completó las tareas: Invita a iniciar el Post-Test Isomórfico desbloqueado.
 * 4. Si completó un ciclo: Muestra su Ganancia de Hake obtenida.
 */
export const DiagnosticPreTestBanner: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // Exclusivo para el rol estudiante
  if (user?.rol !== 'alumno') {
    return null;
  }

  // Consulta del plan de estudio prescriptivo activo
  const { data: activePlan, isLoading: loadingPlan } = useQuery({
    queryKey: ['activeStudyPlan'],
    queryFn: studyPlanApi.getMyActivePlan,
    staleTime: 1000 * 60 * 2,
  });

  // Consulta del historial de evaluaciones para conocer estado basal
  const { data: history = [], isLoading: loadingHistory } = useQuery({
    queryKey: ['myAssessmentsHistory'],
    queryFn: assessmentApi.getMyHistory,
    staleTime: 1000 * 60 * 2,
  });

  if (loadingPlan || loadingHistory) {
    return null;
  }

  // 1. Estado A: Tiene un Plan Prescriptivo Activo
  if (activePlan && activePlan.status === 'active') {
    const totalTasks = activePlan.tasks?.length || 0;
    const completedTasks = activePlan.tasks?.filter((t) => t.is_completed).length || 0;
    const isPlanFinished = activePlan.progress_percentage >= 100 || (totalTasks > 0 && completedTasks === totalTasks);
    const isMasteryPlan = activePlan.title.toLowerCase().includes('post-test') ||
                          activePlan.title.toLowerCase().includes('maestría') ||
                          activePlan.title.toLowerCase().includes('consolidación');

    return (
      <div className="bg-white rounded-[28px] p-5 sm:p-6 shadow-sm border border-slate-150/70 transition-all hover:shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2 flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              {isMasteryPlan ? (
                <Award className="w-4 h-4 text-indigo-600 shrink-0" />
              ) : (
                <Activity className="w-4 h-4 text-blue-600 shrink-0" />
              )}
              <span className={`text-[11px] font-semibold tracking-wider uppercase ${isMasteryPlan ? 'text-indigo-700' : 'text-blue-700'}`}>
                {isMasteryPlan ? 'Plan de Maestría y Consolidación Clínica (Post-Test)' : 'Plan de Refuerzo Clínico en Curso'}
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-[11px] font-medium text-slate-500">
                {completedTasks} de {totalTasks} actividades formativas
              </span>
            </div>

            <h2 className="text-base sm:text-lg font-bold text-slate-900 truncate">
              {activePlan.title}
            </h2>

            {/* Barra de progreso fluida */}
            <div className="space-y-1.5 pt-1 max-w-xl">
              <div className="flex justify-between text-[11px] font-medium text-slate-600">
                <span>{isMasteryPlan ? 'Progreso de Consolidación' : 'Progreso de Nivelación'}</span>
                <span className={`font-semibold ${isMasteryPlan ? 'text-indigo-700' : 'text-blue-700'}`}>
                  {Math.round(activePlan.progress_percentage)}%
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${
                    isMasteryPlan
                      ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600'
                      : 'bg-gradient-to-r from-blue-600 to-indigo-600'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(0, activePlan.progress_percentage))}%` }}
                />
              </div>
            </div>

            {isPlanFinished && (
              <p className="text-xs font-semibold text-emerald-700 pt-1 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  {isMasteryPlan
                    ? '¡Actividades de maestría completadas al 100%! Ciclo formativo y evaluativo culminado.'
                    : 'Actividades formativas completadas. ¡Tu Post-Test Isomórfico está desbloqueado!'}
                </span>
              </p>
            )}
          </div>

          <div className="shrink-0 flex items-center gap-3 pt-2 md:pt-0">
            <button
              type="button"
              onClick={() => {
                if (isPlanFinished && !isMasteryPlan) {
                  navigate('/analytics?action=start_post_test');
                } else {
                  navigate('/analytics');
                }
              }}
              className={`px-5 py-2.5 rounded-full text-xs font-semibold transition-all shadow-xs hover:shadow flex items-center justify-center gap-2 cursor-pointer ${
                isPlanFinished && !isMasteryPlan
                  ? 'text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700'
                  : isMasteryPlan
                  ? 'text-white bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 hover:from-indigo-700 hover:via-blue-700 hover:to-cyan-700'
                  : 'text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
              }`}
            >
              <span>
                {isMasteryPlan
                  ? (isPlanFinished ? 'Ver Analítica de Maestría' : 'Continuar Plan de Maestría')
                  : (isPlanFinished ? 'Rendir Post-Test Isomórfico' : 'Continuar Plan de Estudio')}
              </span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 2. Estado B: Tiene historial previo completado pero no tiene plan activo (mostrar su última ganancia de Hake si existe)
  const lastCompletedPostTest = history.find((a) => a.assessment_type === 'post_test' && a.hake_gain_g !== null && a.hake_gain_g !== undefined);
  if (lastCompletedPostTest && lastCompletedPostTest.hake_gain_g !== null) {
    return (
      <div className="bg-white rounded-[28px] p-5 sm:p-6 shadow-sm border border-slate-150/70 transition-all hover:shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <Award className="w-4 h-4 text-blue-600 shrink-0" />
              <span className="text-[11px] font-semibold text-blue-700 tracking-wider uppercase">
                Ciclo de Nivelación Completado
              </span>
              <span className="text-slate-300">•</span>
              <HakeGainBadge gain={lastCompletedPostTest.hake_gain_g} showDetails={false} />
            </div>

            <h2 className="text-base sm:text-lg font-bold text-slate-900">
              Evaluación Diagnóstica CACES y Aprendizaje Clínico
            </h2>
            <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
              Completaste tu ciclo de intervención diagnóstica. Puedes iniciar una nueva batería troncal para seguir perfeccionando tus competencias frente a las GPC del MSP.
            </p>
          </div>

          <div className="shrink-0 flex items-center gap-3 pt-2 md:pt-0">
            <button
              type="button"
              onClick={() => navigate('/analytics')}
              className="px-5 py-2.5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-xs hover:shadow transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <ClipboardCheck className="w-3.5 h-3.5" />
              <span>Ver Analítica o Nuevo Diagnóstico</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 3. Estado C: Estudiante sin Pre-Test previo (invitación inicial destacada)
  return (
    <div className="bg-white rounded-[28px] p-5 sm:p-6 shadow-sm border border-slate-150/70 transition-all hover:shadow-md">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
            <span className="text-[11px] font-semibold text-blue-700 tracking-wider uppercase">
              Evaluación Diagnóstica Inicial • Marco CACES / MSP
            </span>
          </div>

          <h2 className="text-base sm:text-lg font-bold text-slate-900">
            Inicia tu Pre-Test Diagnóstico para activar tu Plan de Estudio Prescriptivo
          </h2>

          <p className="text-xs text-slate-600 leading-relaxed">
            Evalúa tu juicio clínico frente a las cuatro áreas troncales de habilitación profesional en Ecuador. Nuestro motor heurístico detectará tus omisiones normativas y diseñará una ruta dosificada de lecturas y simulaciones en tu Zona de Desarrollo Próximo.
          </p>
        </div>

        <div className="shrink-0 pt-2 md:pt-0">
          <button
            type="button"
            onClick={() => navigate('/analytics')}
            className="px-5 py-2.5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-xs hover:shadow transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <ClipboardCheck className="w-3.5 h-3.5" />
            <span>Iniciar Pre-Test CACES</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticPreTestBanner;
