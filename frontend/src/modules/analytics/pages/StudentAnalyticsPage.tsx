import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, ClipboardCheck, ArrowRight } from 'lucide-react';
import ReasoningTrends from '../components/ReasoningTrends';
import { PrescriptivePlanCard } from '../../study_plans/components/PrescriptivePlanCard';
import { AssessmentRunnerModal } from '../../assessments/components/AssessmentRunnerModal';
import PdfViewerModal from '../../evaluation/components/PdfViewerModal';
import SocraticDebriefModal from '../../evaluation/components/SocraticDebriefModal';
import { useSocraticDebriefStore } from '../../evaluation/store/useSocraticDebriefStore';
import { studyPlanApi } from '../../study_plans/api/studyPlanApi';
import { assessmentApi } from '../../assessments/api/assessmentApi';
import type { PrescriptiveStudyPlan, StudyPlanTask } from '../../study_plans/types';
import type { DiagnosticAssessment, AssessmentSummaryReport } from '../../assessments/types';

interface AssessmentScopeOption {
  id: string;
  label: string;
  shortLabel: string;
  description: string;
  numCases: number;
  badge: string;
}

const ASSESSMENT_SCOPES: AssessmentScopeOption[] = [
  {
    id: 'Batería Troncal CACES (Multidisciplinar)',
    label: 'Batería Troncal CACES (Multidisciplinar)',
    shortLabel: 'Troncal CACES',
    description: 'Muestreo estratificado balanceado: 1 caso por cada una de las 4 troncales (Obstetricia, Pediatría, Medicina Interna, Infectología). Validez psicométrica 1:1:1:1.',
    numCases: 4,
    badge: 'Recomendado CACES / MSP',
  },
  {
    id: 'Ginecología y Obstetricia',
    label: 'Ginecología y Obstetricia',
    shortLabel: 'Gineco-Obstetricia',
    description: 'Preeclampsia con criterios de severidad, hemorragia posparto (Código Rojo) y choque hipovolémico obstétrico.',
    numCases: 3,
    badge: '3 Casos Troncales',
  },
  {
    id: 'Pediatría y Neonatología',
    label: 'Pediatría y Neonatología',
    shortLabel: 'Pediatría',
    description: 'Crisis asmática aguda grave, sepsis neonatal temprana y bronquiolitis aguda.',
    numCases: 3,
    badge: '3 Casos Troncales',
  },
  {
    id: 'Medicina Interna y Crónicos',
    label: 'Medicina Interna y Crónicos',
    shortLabel: 'Medicina Interna',
    description: 'Cetoacidosis diabética moderada/severa y síndrome coronario agudo sin elevación del ST.',
    numCases: 2,
    badge: '2 Casos Troncales',
  },
  {
    id: 'Infectología y Salud Pública',
    label: 'Infectología y Salud Pública',
    shortLabel: 'Infectología',
    description: 'Neumonía adquirida en la comunidad grave y Dengue con signos de alarma.',
    numCases: 2,
    badge: '2 Casos Troncales',
  },
];

/**
 * StudentAnalyticsPage — Vista canónica de Desempeño, Plan Prescriptivo y Tendencias Clínicas
 */
export default function StudentAnalyticsPage() {
  const navigate = useNavigate();

  const [activePlan, setActivePlan] = useState<PrescriptiveStudyPlan | null>(null);
  const [loadingPlan, setLoadingPlan] = useState(true);
  const [isCompletingTask, setIsCompletingTask] = useState(false);

  // Selector institucional de ámbito de evaluación
  const [selectedScopeId, setSelectedScopeId] = useState<string>('Batería Troncal CACES (Multidisciplinar)');
  const currentScope = ASSESSMENT_SCOPES.find((s) => s.id === selectedScopeId) || ASSESSMENT_SCOPES[0];

  // Estado para el modal de evaluación activa (Pre-Test o Post-Test)
  const [activeAssessment, setActiveAssessment] = useState<DiagnosticAssessment | null>(null);
  const [isAssessmentModalOpen, setIsAssessmentModalOpen] = useState(false);
  const [startingAssessment, setStartingAssessment] = useState(false);

  // Estados para Visor oficial de GPC desde el plan prescriptivo
  const [readingGpcTask, setReadingGpcTask] = useState<StudyPlanTask | null>(null);
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);

  const extractSection = (desc?: string): string => {
    if (!desc) return '';
    const match = desc.match(/(Sección[^,.]+)/i);
    return match ? match[1] : '';
  };

  const handleReadGpc = (task: StudyPlanTask) => {
    setReadingGpcTask(task);
    setIsPdfModalOpen(true);
  };

  const handleConfirmGpcReading = async () => {
    if (!readingGpcTask || !readingGpcTask.id) return;
    await handleCompleteTask(readingGpcTask.id);
    setReadingGpcTask((prev) => (prev ? { ...prev, is_completed: true } : null));
  };

  const handleOpenDebrief = (task: StudyPlanTask) => {
    let omision = '';
    if (task.description) {
      const match = task.description.match(/'([^']+)'/);
      if (match) {
        omision = match[1];
      }
    }
    if (!omision) {
      omision = task.title.replace(/^Debriefing Socrático:\s*/i, '');
    }
    const caseId = task.resource_reference || 'case_preeclampsia_01';
    useSocraticDebriefStore.getState().openDebrief(caseId, task.title, [omision]);
  };

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
      const assessment = await assessmentApi.startPreTest(currentScope.id, currentScope.numCases);
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
            onReadGpc={handleReadGpc}
            onOpenDebrief={handleOpenDebrief}
            isCompletingTask={isCompletingTask}
          />
        ) : (
          /* Banner para Iniciar Pre-Test Diagnóstico con Selector Institucional */
          <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-sm space-y-6">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="space-y-2 max-w-2xl">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-blue-600 shrink-0" />
                  <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
                    Nivelación Formativa Heurística • Marco CACES / MSP
                  </span>
                </div>
                <h2 className="text-lg sm:text-xl font-bold text-slate-900">
                  Plan de Estudio Prescriptivo y Evaluación Diagnóstica
                </h2>
                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  Inicia un Pre-Test diagnóstico estructurado. La batería oficial aplica muestreo estratificado balanceado por las cuatro troncales del examen de habilitación médica profesional en Ecuador.
                </p>
              </div>

              <button
                type="button"
                onClick={handleStartPreTest}
                disabled={startingAssessment}
                className="px-6 py-3 rounded-full text-xs sm:text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-sm hover:shadow transition-all shrink-0 flex items-center justify-center gap-2 disabled:opacity-50 self-start md:self-auto cursor-pointer"
              >
                <ClipboardCheck className="w-4 h-4" />
                <span>{startingAssessment ? 'Cargando reactivos...' : `Iniciar Pre-Test (${currentScope.numCases} casos)`}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            {/* Selector de Ámbito Troncal */}
            <div className="space-y-3 pt-2 border-t border-slate-100">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Selecciona el Ámbito de Evaluación
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
                {ASSESSMENT_SCOPES.map((scope) => {
                  const isSelected = scope.id === selectedScopeId;
                  return (
                    <button
                      key={scope.id}
                      type="button"
                      onClick={() => setSelectedScopeId(scope.id)}
                      className={`text-left p-3.5 rounded-2xl transition-all duration-200 cursor-pointer border ${
                        isSelected
                          ? 'border-blue-600 bg-blue-50/40 shadow-xs'
                          : 'border-slate-150 hover:border-slate-300 bg-white hover:bg-slate-50/50'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-1 mb-1.5">
                        <span className={`text-xs font-bold leading-tight ${isSelected ? 'text-blue-900' : 'text-slate-800'}`}>
                          {scope.shortLabel}
                        </span>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                            isSelected
                              ? 'bg-blue-600 text-white'
                              : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {scope.numCases} {scope.numCases === 1 ? 'caso' : 'casos'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                        {scope.description}
                      </p>
                    </button>
                  );
                })}
              </div>

              {/* Detalle del Ámbito Activo */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-150 text-xs text-slate-600 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-900">{currentScope.label}:</span>
                  <span className="text-slate-600">{currentScope.description}</span>
                </div>
                <div className="shrink-0 font-medium text-blue-700 bg-blue-100/60 px-2.5 py-1 rounded-full text-[11px]">
                  {currentScope.badge} • {(10 / currentScope.numCases).toFixed(2)} pts por caso
                </div>
              </div>
            </div>
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

      {/* 5. Visor Oficial de GPC para Lecturas Normativas del Plan Prescriptivo */}
      {readingGpcTask && (
        <PdfViewerModal
          isOpen={isPdfModalOpen}
          onClose={() => {
            setIsPdfModalOpen(false);
            setReadingGpcTask(null);
          }}
          guiaId={readingGpcTask.resource_reference || readingGpcTask.title}
          seccion={extractSection(readingGpcTask.description)}
          onConfirmReading={handleConfirmGpcReading}
          isCompleted={readingGpcTask.is_completed}
          confirmButtonText="Confirmar Lectura Normativa"
        />
      )}

      {/* 6. Modal de Debriefing Socrático */}
      <SocraticDebriefModal />
    </div>
  );
}
