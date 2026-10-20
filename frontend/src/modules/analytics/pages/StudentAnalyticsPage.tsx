import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Sparkles, ClipboardCheck, ArrowRight } from 'lucide-react';
import ReasoningTrends from '../components/ReasoningTrends';
import { PrescriptivePlanCard } from '../../study_plans/components/PrescriptivePlanCard';
import { AssessmentRunnerModal } from '../../assessments/components/AssessmentRunnerModal';
import { studyPlanApi } from '../../study_plans/api/studyPlanApi';
import { assessmentApi } from '../../assessments/api/assessmentApi';
import type { PrescriptiveStudyPlan } from '../../study_plans/types';
import type { DiagnosticAssessment, AssessmentSummaryReport } from '../../assessments/types';

/**
 * StudentAnalyticsPage — Vista canónica de Desempeño, Plan Prescriptivo y Tendencias Clínicas
 */
export default function StudentAnalyticsPage() {
  const navigate = useNavigate();

  const [activePlan, setActivePlan] = useState<PrescriptiveStudyPlan | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(true);
  const [isCompletingTask, setIsCompletingTask] = useState(false);

  // Estado para el modal de evaluación activa (Pre-Test o Post-Test)
  const [activeAssessment, setActiveAssessment] = useState<DiagnosticAssessment | null>(null);
  const [isAssessmentModalOpen, setIsAssessmentModalOpen] = useState(false);
  const [startingAssessment, setStartingAssessment] = useState(false);

  const fetchActivePlan = useCallback(async () => {
    try {
      setLoadingPlan(true);
      const plan = await studyPlanApi.getMyActivePlan();
      setActivePlan(plan);
    } catch {
      setActivePlan(null);
    } finally {
      setLoadingPlan(false);
    }
  }, []);

  useEffect(() => {
    fetchActivePlan();
  }, [fetchActivePlan]);

  const handleCompleteTask = async (taskId: number) => {
    try {
      setIsCompletingTask(true);
      const res = await studyPlanApi.completeTask(taskId);
      setActivePlan((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          progress_percentage: res.progress_percentage,
          status: res.plan_completed ? 'completed' : prev.status,
          tasks: prev.tasks.map((t) =>
            t.id === taskId ? { ...t, is_completed: true, completed_at: res.completed_at } : t
          ),
        };
      });
    } catch (err) {
      console.error('Error al completar la tarea del plan:', err);
    } finally {
      setIsCompletingTask(false);
    }
  };

  const handleStartPreTest = async () => {
    try {
      setStartingAssessment(true);
      const assessment = await assessmentApi.startPreTest('Multidisciplinar GPC', 3);
      setActiveAssessment(assessment);
      setIsAssessmentModalOpen(true);
    } catch (err) {
      console.error('Error al iniciar Pre-Test:', err);
    } finally {
      setStartingAssessment(false);
    }
  };

  const handleStartPostTest = async (preTestId: string) => {
    try {
      setStartingAssessment(true);
      const assessment = await assessmentApi.startPostTest(preTestId);
      setActiveAssessment(assessment);
      setIsAssessmentModalOpen(true);
    } catch (err) {
      console.error('Error al iniciar Post-Test isomórfico:', err);
    } finally {
      setStartingAssessment(false);
    }
  };

  const handleAssessmentCompleted = (_report: AssessmentSummaryReport) => {
    // Recargar el plan prescriptivo tras finalizar la evaluación
    fetchActivePlan();
  };

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
            Diagnóstico formativo estructurado, plan prescriptivo adaptativo y análisis longitudinal de brechas frente a las Guías de Práctica Clínica.
          </p>
        </div>
      </div>

      {/* 2. Sección del Plan de Estudio Prescriptivo o Banner de Entrada */}
      <section className="space-y-4">
        {loadingPlan ? (
          <div className="bg-white rounded-[28px] p-6 shadow-sm animate-pulse space-y-4">
            <div className="h-4 bg-slate-100 rounded w-1/4" />
            <div className="h-6 bg-slate-100 rounded w-1/2" />
            <div className="h-2 bg-slate-100 rounded w-full" />
          </div>
        ) : activePlan ? (
          <PrescriptivePlanCard
            plan={activePlan}
            onCompleteTask={handleCompleteTask}
            onStartPostTest={handleStartPostTest}
            onNavigateToCase={(caseId) => navigate(`/cases/${encodeURIComponent(caseId)}`)}
            isCompletingTask={isCompletingTask}
          />
        ) : (
          /* Banner para Iniciar Pre-Test Diagnóstico */
          <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="space-y-2 max-w-xl">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
                <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
                  Nivelación Formativa Heurística
                </span>
              </div>
              <h2 className="text-lg sm:text-xl font-bold text-slate-900">
                Plan de Estudio Prescriptivo y Evaluación Diagnóstica
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                Inicia un Pre-Test diagnóstico de casos representativos. Nuestro motor heurístico evaluará tus decisiones frente a las GPC del MSP, ponderará la severidad de las omisiones y prescribirá una ruta de estudio personalizada con lecturas y simulaciones en tu Zona de Desarrollo Próximo.
              </p>
            </div>

            <button
              type="button"
              onClick={handleStartPreTest}
              disabled={startingAssessment}
              className="px-6 py-3 rounded-full text-xs sm:text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-sm hover:shadow transition-all shrink-0 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <ClipboardCheck className="w-4 h-4" />
              <span>{startingAssessment ? 'Cargando reactivos...' : 'Iniciar Pre-Test Diagnóstico'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </section>

      {/* 3. Núcleo Analítico Longitudinal y Radar de Competencias */}
      <section className="space-y-6">
        <ReasoningTrends />
      </section>

      {/* 4. Modal de Ejecución de Evaluación (Pre-Test / Post-Test) */}
      {activeAssessment && (
        <AssessmentRunnerModal
          isOpen={isAssessmentModalOpen}
          onClose={() => setIsAssessmentModalOpen(false)}
          assessment={activeAssessment}
          onAssessmentCompleted={handleAssessmentCompleted}
        />
      )}
    </div>
  );
}
