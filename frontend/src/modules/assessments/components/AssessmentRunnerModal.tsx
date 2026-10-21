import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, ArrowRight, ArrowLeft, Send, AlertTriangle } from 'lucide-react';
import type { DiagnosticAssessment, AssessmentSummaryReport } from '../types';
import { assessmentApi } from '../api/assessmentApi';
import { HakeGainBadge } from './HakeGainBadge';
import { ClinicalMarkdownRenderer } from '../../../core/ui';

interface AssessmentRunnerModalProps {
  isOpen: boolean;
  onClose: () => void;
  assessment: DiagnosticAssessment;
  onAssessmentCompleted?: (report: AssessmentSummaryReport) => void;
}

export const AssessmentRunnerModal: React.FC<AssessmentRunnerModalProps> = ({
  isOpen,
  onClose,
  assessment,
  onAssessmentCompleted,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [report, setReport] = useState<AssessmentSummaryReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isSubmitting) {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isSubmitting, onClose]);

  if (!isOpen) return null;

  const items = assessment.items || [];
  const currentItem = items[currentIndex];
  const isLast = currentIndex === items.length - 1;
  const isPostTest = assessment.assessment_type === 'post_test';

  const handleAnswerChange = (val: string) => {
    if (!currentItem?.id) return;
    setAnswers((prev) => ({
      ...prev,
      [currentItem.id!]: val,
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const payload = items.map((it) => ({
        item_id: it.id!,
        student_answer: answers[it.id!] || '',
      }));
      const summary = await assessmentApi.submitAssessment(assessment.id, payload);
      setReport(summary);
      onAssessmentCompleted?.(summary);
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : 'Error al procesar la evaluación diagnóstica.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const modalContent = (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-[28px] w-full max-w-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Cabecera */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between gap-4">
          <div>
            <span className="text-xs font-semibold text-blue-600 uppercase tracking-wider">
              {isPostTest ? 'Evaluación Formativa de Salida (Post-Test)' : 'Evaluación Diagnóstica Inicial (Pre-Test)'}
            </span>
            <h3 className="text-base sm:text-lg font-bold text-slate-900 mt-0.5">
              {assessment.specialty_scope}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-colors"
            title="Cerrar evaluación"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {report ? (
            /* Vista de Reporte de Resultados */
            <div className="space-y-6">
              <div className="bg-slate-50 rounded-[20px] p-6 space-y-4">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    Dictamen Evaluativo Formativo
                  </span>
                  {isPostTest && (
                    <HakeGainBadge gain={report.hake_gain_g} category={report.hake_category} />
                  )}
                </div>

                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-slate-900">
                    {report.score_total.toFixed(1)}
                  </span>
                  <span className="text-sm text-slate-500">
                    / {report.score_max.toFixed(0)} pts
                  </span>
                </div>

                <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                  {isPostTest
                    ? 'Evaluación completada. Se ha contrastado tu desempeño con la línea base para medir la ganancia cognitiva normalizada de Hake.'
                    : 'Evaluación diagnóstica inicial completada. Se ha generado un Plan de Estudio Prescriptivo con actividades personalizadas en tus brechas clínicas.'}
                </p>
              </div>

              {report.total_omisiones_detectadas > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-slate-700 block">
                    Brechas detectadas frente a las GPC del MSP
                  </span>
                  <div className="bg-amber-50/50 rounded-[18px] p-4 text-xs text-amber-900 leading-relaxed">
                    Se identificaron {report.total_omisiones_detectadas} omisiones normativas. Revisa los módulos formativos prescritos para consolidar el estándar clínico.
                  </div>
                </div>
              )}
            </div>
          ) : currentItem ? (
            /* Vista de Resolución de Reactivo */
            <div className="space-y-5">
              {/* Indicador de reactivo */}
              <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
                <span>
                  Reactivo {currentIndex + 1} de {items.length}
                </span>
                <span className="text-blue-600">
                  {isPostTest ? 'Variante Isomórfica Paralela' : 'Caso Basal GPC'}
                </span>
              </div>

              {/* Enunciado del caso renderizado con Markdown clínico */}
              <div className="bg-[#f0f4f9] rounded-[20px] p-5 text-xs sm:text-sm text-slate-800 leading-relaxed">
                <ClinicalMarkdownRenderer content={currentItem.prompt_text} />
              </div>

              {/* Área de Respuesta del Estudiante */}
              <div className="space-y-1.5">
                <label
                  htmlFor={`answer_${currentItem.id}`}
                  className="text-xs font-semibold text-slate-700 block"
                >
                  Tu Resolución Clínica y Plan Terapéutico Normado
                </label>
                <textarea
                  id={`answer_${currentItem.id}`}
                  value={answers[currentItem.id!] || ''}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  placeholder="Escribe tu razonamiento diagnóstico, conducta terapéutica y fármacos según la GPC..."
                  rows={6}
                  disabled={isSubmitting}
                  className="w-full text-xs sm:text-sm text-slate-900 bg-white border border-slate-200 rounded-[18px] p-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder:text-slate-400"
                />
              </div>

              {errorMessage && (
                <div className="text-xs font-medium text-rose-600 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500 text-center py-8">
              No hay reactivos disponibles en esta evaluación.
            </p>
          )}
        </div>

        {/* Pie de navegación */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between gap-3">
          {report ? (
            <button
              type="button"
              onClick={onClose}
              className="w-full sm:w-auto ml-auto px-6 py-2.5 rounded-full text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 transition-colors"
            >
              Cerrar y Ver Resultados
            </button>
          ) : (
            <>
              <button
                type="button"
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                disabled={currentIndex === 0 || isSubmitting}
                className="px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:bg-slate-200/60 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center gap-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Anterior</span>
              </button>

              <div className="flex items-center gap-2">
                {!isLast ? (
                  <button
                    type="button"
                    onClick={() => setCurrentIndex((prev) => Math.min(items.length - 1, prev + 1))}
                    disabled={isSubmitting}
                    className="px-5 py-2.5 rounded-full text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors flex items-center gap-1.5 shadow-xs"
                  >
                    <span>Siguiente</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="px-6 py-2.5 rounded-full text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all flex items-center gap-2 shadow-xs disabled:opacity-50"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{isSubmitting ? 'Calificando...' : 'Finalizar y Calificar'}</span>
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );

  return typeof document !== 'undefined'
    ? createPortal(modalContent, document.body)
    : null;
};
