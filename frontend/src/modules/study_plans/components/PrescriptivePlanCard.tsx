import React from 'react';
import { BookOpen, Stethoscope, MessageSquare, CheckCircle2, Circle, ArrowRight } from 'lucide-react';
import type { PrescriptiveStudyPlan, StudyPlanTask } from '../types';

interface PrescriptivePlanCardProps {
  plan: PrescriptiveStudyPlan;
  onCompleteTask?: (taskId: number) => void;
  onStartPostTest?: (preTestId: string) => void;
  onNavigateToCase?: (caseId: string) => void;
  isCompletingTask?: boolean;
}

export const PrescriptivePlanCard: React.FC<PrescriptivePlanCardProps> = ({
  plan,
  onCompleteTask,
  onStartPostTest,
  onNavigateToCase,
  isCompletingTask = false,
}) => {
  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'gpc_reading':
        return <BookOpen className="w-4 h-4 text-cyan-600 shrink-0" />;
      case 'case_simulation':
        return <Stethoscope className="w-4 h-4 text-blue-600 shrink-0" />;
      case 'socratic_review':
        return <MessageSquare className="w-4 h-4 text-indigo-600 shrink-0" />;
      default:
        return <BookOpen className="w-4 h-4 text-slate-500 shrink-0" />;
    }
  };

  const getTaskTypeLabel = (type: string) => {
    switch (type) {
      case 'gpc_reading':
        return 'Lectura Normativa GPC';
      case 'case_simulation':
        return 'Simulación Clínica ZDP';
      case 'socratic_review':
        return 'Debriefing Socrático';
      default:
        return 'Actividad Formativa';
    }
  };

  const completedTasksCount = plan.tasks.filter((t) => t.is_completed).length;
  const isPlanFinished = plan.progress_percentage >= 100 || plan.status === 'completed';

  return (
    <div className="bg-white rounded-[28px] p-6 shadow-sm space-y-6">
      {/* Cabecera del Plan */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
            Plan de Estudio Prescriptivo
          </span>
          <h3 className="text-lg sm:text-xl font-bold text-slate-900 mt-0.5">
            {plan.title}
          </h3>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs font-semibold text-slate-500">
            {completedTasksCount} de {plan.tasks.length} completadas
          </span>
          <span className="text-xs font-bold text-slate-900">
            {Math.round(plan.progress_percentage)}%
          </span>
        </div>
      </div>

      {/* Barra de Progreso */}
      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className="bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(100, Math.max(0, plan.progress_percentage))}%` }}
        />
      </div>

      {/* Diagnóstico de Brechas */}
      {plan.diagnosis_summary && (
        <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
          {plan.diagnosis_summary}
        </p>
      )}

      {/* Lista de Tareas Dosificadas */}
      <div className="space-y-3">
        <span className="text-xs font-semibold text-slate-700 block">
          Tareas Formativas Dosificadas
        </span>
        <div className="divide-y divide-slate-100">
          {plan.tasks.map((task: StudyPlanTask) => {
            const isClickable = !task.is_completed && !isCompletingTask;

            return (
              <div
                key={task.id || task.title}
                className="py-3 flex items-start justify-between gap-3 group"
              >
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  {/* Botón interactivo de checklist */}
                  <button
                    type="button"
                    onClick={() => task.id && isClickable && onCompleteTask?.(task.id)}
                    disabled={!isClickable}
                    className="mt-0.5 shrink-0 transition-opacity hover:opacity-80 disabled:cursor-default"
                    title={task.is_completed ? 'Tarea completada' : 'Marcar como completada'}
                  >
                    {task.is_completed ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-300 group-hover:text-blue-500" />
                    )}
                  </button>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      {getTaskIcon(task.task_type)}
                      <span className="text-xs font-semibold text-slate-500">
                        {getTaskTypeLabel(task.task_type)}
                      </span>
                      <span className="text-xs text-slate-400">
                        • {task.estimated_minutes} min
                      </span>
                    </div>

                    <h4
                      className={`text-sm font-semibold mt-0.5 ${
                        task.is_completed ? 'line-through text-slate-400' : 'text-slate-900'
                      }`}
                    >
                      {task.title}
                    </h4>

                    {task.description && (
                      <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">
                        {task.description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Acciones contextuales (resolver caso) */}
                {task.task_type === 'case_simulation' && task.resource_reference && !task.is_completed && onNavigateToCase && (
                  <button
                    type="button"
                    onClick={() => onNavigateToCase(task.resource_reference)}
                    className="shrink-0 text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors mt-0.5"
                  >
                    <span>Resolver</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Botón de Post-Test Isomórfico */}
      {plan.source_assessment_id && onStartPostTest && (
        <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <p className="text-xs text-slate-500">
            {isPlanFinished
              ? 'Has completado las actividades del plan. Verifica tu aprendizaje con el Post-Test isomórfico.'
              : 'Puedes iniciar el Post-Test isomórfico cuando sientas que has consolidado las competencias normadas.'}
          </p>
          <button
            type="button"
            onClick={() => onStartPostTest(plan.source_assessment_id!)}
            className="w-full sm:w-auto px-5 py-2.5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-xs transition-all shrink-0 flex items-center justify-center gap-2"
          >
            <span>Iniciar Post-Test Isomórfico</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
};
