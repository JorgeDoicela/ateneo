import { useState, useMemo, useEffect } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  BookOpen, 
  RefreshCw, 
  User, 
  Stethoscope, 
  Pill, 
  ShieldAlert, 
  Activity, 
  Download, 
  Loader2,
  ShieldCheck,
  ArrowRight,
  LucideIcon,
  MessageSquare,
  Mic,
  GraduationCap,
  Award
} from 'lucide-react';
import SkillRadarChart from '../../analytics/components/SkillRadarChart';
import PdfViewerModal from './PdfViewerModal';
import evaluationApi from '../api/evaluationApi';
import { useAuth } from '../../../context/AuthContext';
import { useSocraticDebriefStore } from '../store/useSocraticDebriefStore';
import { EvaluationResult } from '../../../types';
import useLearningTelemetry from '../../analytics/hooks/useLearningTelemetry';
import { ClinicalMarkdownRenderer } from '../../../core/ui';

interface EjeConfig {
  key: string;
  label: string;
  icon: LucideIcon;
  badge: string;
}

const EJES_CONFIG: EjeConfig[] = [
  { key: 'diagnóstico', label: 'Diagnóstico', icon: Stethoscope, badge: 'bg-sky-50 text-sky-800 border-sky-200' },
  { key: 'tratamiento', label: 'Tratamiento', icon: Pill, badge: 'bg-rose-50 text-rose-800 border-rose-200' },
  { key: 'prevención', label: 'Prevención', icon: ShieldAlert, badge: 'bg-purple-50 text-purple-800 border-purple-200' },
  { key: 'seguimiento', label: 'Seguimiento', icon: Activity, badge: 'bg-emerald-50 text-emerald-800 border-emerald-200' },
];

export interface FeedbackCardProps {
  result: EvaluationResult;
  studentAnswer?: string;
  audioBlob?: Blob | null;
  onReset?: () => void;
}

export default function FeedbackCard({ result, studentAnswer = '', audioBlob = null, onReset }: FeedbackCardProps) {
  const [pdfModalOpen, setPdfModalOpen] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);
  const { user } = useAuth();
  const openDebrief = useSocraticDebriefStore((state) => state.openDebrief);
  const { trackSocraticDebriefOpened } = useLearningTelemetry();

  const audioUrl = useMemo(() => {
    return audioBlob ? URL.createObjectURL(audioBlob) : null;
  }, [audioBlob]);

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  useEffect(() => {
    if (result?.gamification_update) {
      window.dispatchEvent(new CustomEvent('ateneo:gamification-updated'));
    }
  }, [result?.gamification_update]);

  const handleOpenDebrief = (omisionesParam: string[] | string) => {
    const caseId = result.case_id || 'case_preeclampsia_01';
    const primaryOmision = Array.isArray(omisionesParam) ? (omisionesParam[0] || '') : omisionesParam;
    trackSocraticDebriefOpened(caseId, primaryOmision);
    openDebrief(caseId, result.case_title || 'Caso Clínico Formativo', omisionesParam);
  };

  if (!result) return null;

  const {
    score,
    score_max = 10,
    aciertos = [],
    omisiones = [],
    competencias_deficientes = [],
    cita_normativa,
    retroalimentacion_general
  } = result;

  const scorePercentage = Math.round((score / score_max) * 100);
  
  let scoreBadgeColor = 'bg-sky-50 text-[#0b57d0] border border-sky-200';
  if (scorePercentage < 60) {
    scoreBadgeColor = 'bg-rose-50 text-rose-700 border border-rose-200';
  } else if (scorePercentage < 80) {
    scoreBadgeColor = 'bg-amber-50 text-amber-700 border border-amber-200';
  } else {
    scoreBadgeColor = 'bg-emerald-50 text-emerald-700 border border-emerald-200';
  }

  // Agrupar competencias deficientes y calcular puntaje/estado por eje clínico
  const competenciasPorEje = EJES_CONFIG.map(ejeConfig => {
    const items = competencias_deficientes.filter(item => {
      if (!item || !item.eje) return false;
      const ejeNormalizado = item.eje.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      const keyNormalizada = ejeConfig.key.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      return ejeNormalizado.includes(keyNormalizada);
    });

    const tieneDeficiencias = items.length > 0;
    let axisScore = 0;
    let estadoLabel = '';
    let estadoBadgeClass = '';

    if (scorePercentage === 0) {
      axisScore = 0;
      if (tieneDeficiencias) {
        estadoLabel = `${items.length} brecha(s)`;
        estadoBadgeClass = 'bg-rose-50 text-rose-700 border-rose-200';
      } else {
        estadoLabel = 'No Demostrado';
        estadoBadgeClass = 'bg-slate-100 text-[#444746] border-slate-200';
      }
    } else {
      if (tieneDeficiencias) {
        axisScore = Math.max(15, Math.min(scorePercentage, 100 - items.length * 25));
        estadoLabel = `${items.length} brecha(s)`;
        estadoBadgeClass = 'bg-amber-50 text-amber-700 border-amber-200';
      } else {
        if (scorePercentage >= 80) {
          axisScore = Math.min(100, Math.max(scorePercentage, 92));
          estadoLabel = 'Consolidado';
          estadoBadgeClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
        } else if (scorePercentage >= 50) {
          axisScore = Math.min(85, Math.max(scorePercentage, 70));
          estadoLabel = 'Competente';
          estadoBadgeClass = 'bg-sky-50 text-[#0b57d0] border-sky-200';
        } else {
          axisScore = scorePercentage;
          estadoLabel = 'No Abordado';
          estadoBadgeClass = 'bg-amber-50 text-amber-700 border-amber-200';
        }
      }
    }

    return {
      ...ejeConfig,
      items,
      score: axisScore,
      estadoLabel,
      estadoBadgeClass,
      tieneDeficiencias
    };
  });

  const handleDownloadPdf = async (): Promise<void> => {
    setDownloadingPdf(true);
    try {
      const blob = await evaluationApi.exportEvaluationPdf({
        case_id: result.case_id || 'case_preeclampsia_01',
        case_title: result.case_title || 'Caso Clínico Formativo GPC',
        student_name: user?.nombre || 'Estudiante de Medicina',
        guia_asociada: result.cita_normativa?.guia || 'Norma Oficial GPC Ecuador',
        student_answer: studentAnswer || '',
        eval_result: result
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Informe_Clinico_Ateneo_${result.case_id || 'evaluacion'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: unknown) {
      console.error('Error al exportar PDF:', err);
      alert('Hubo un problema al generar el PDF del informe clínico.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-8">
      
      {/* 1. Header de Evaluación con Puntaje y Descarga */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border-0 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-medium text-[#0b57d0] mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span>Dictamen Formativo Contrastado con GPC</span>
            </div>
            <h2 className="text-2xl font-normal text-[#1f1f1f] font-heading">
              Evaluación Diagnóstica
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-slate-300 bg-white hover:bg-slate-50 text-xs font-medium text-[#1f1f1f] transition-colors cursor-pointer shadow-xs"
            >
              {downloadingPdf ? <Loader2 className="w-3.5 h-3.5 animate-spin text-[#0b57d0]" /> : <Download className="w-3.5 h-3.5 text-[#0b57d0]" />}
              <span>{downloadingPdf ? "Generando..." : "Descargar Dictamen"}</span>
            </button>

            <div className={`flex items-baseline gap-1.5 px-4 py-2 rounded-full font-heading font-medium ${scoreBadgeColor}`}>
              <span className="text-2xl font-semibold">{score}</span>
              <span className="text-xs opacity-75">/ {score_max} pts</span>
            </div>
          </div>
        </div>

        <div className="bg-[#f0f4f9] p-5 rounded-[20px] text-sm text-[#1f1f1f] leading-relaxed">
          <ClinicalMarkdownRenderer content={retroalimentacion_general} />
        </div>
      </div>

      {/* 2. Reconocimiento Formativo y Progresión de Carrera Médica */}
      {result.gamification_update && (
        <div className="bg-gradient-to-br from-cyan-50/40 via-blue-50/30 to-indigo-50/40 rounded-[28px] p-6 sm:p-7 shadow-xs border border-blue-200/60 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-2xl bg-white shadow-xs text-[#0b57d0] border border-blue-100">
                <GraduationCap className="w-5 h-5 text-[#0b57d0]" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-slate-900 tracking-tight">
                  Progresión en Carrera Formativa
                </h3>
                <p className="text-xs text-slate-500">
                  Puntos clínicos obtenidos por adherencia diagnóstica y resolución
                </p>
              </div>
            </div>

            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-100/80 text-blue-800 text-xs font-semibold self-start sm:self-auto">
              <span>+{result.gamification_update.xp_ganados} XP ganados</span>
            </div>
          </div>

          {result.gamification_update.subio_nivel && (
            <div className="p-3.5 rounded-[18px] bg-white border border-blue-300/80 flex items-center gap-3">
              <Award className="w-5 h-5 text-amber-500 shrink-0" />
              <div className="text-xs">
                <span className="font-bold text-slate-900 block">
                  Ascenso de Rango Clínico Formativo
                </span>
                <span className="text-slate-600">
                  Has alcanzado el rango de <span className="font-semibold text-blue-700">{result.gamification_update.nuevo_rango}</span> (Nivel {result.gamification_update.nuevo_nivel}).
                </span>
              </div>
            </div>
          )}

          {result.gamification_update.nuevos_logros_desbloqueados && result.gamification_update.nuevos_logros_desbloqueados.length > 0 && (
            <div className="space-y-2 pt-1">
              <span className="text-xs font-medium text-slate-700 block">
                Nuevos hitos clínicos alcanzados en esta simulación:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {result.gamification_update.nuevos_logros_desbloqueados.map((ach) => (
                  <div
                    key={ach.achievement_id}
                    className="p-3 rounded-[16px] bg-white border border-emerald-200/80 flex items-center justify-between gap-3 shadow-2xs"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <div className="min-w-0">
                        <span className="text-xs font-bold text-slate-900 block truncate">
                          {ach.titulo}
                        </span>
                        <span className="text-[11px] text-slate-500 block truncate">
                          {ach.descripcion}
                        </span>
                      </div>
                    </div>
                    <span className="text-[11px] font-mono font-bold text-emerald-700 shrink-0">
                      +{ach.puntos_xp} XP
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Razonamiento Registrado del Estudiante (Nota de Voz o Texto) */}
      {(audioUrl || result.transcripcion_audio) && (
        <div className="bg-white rounded-[28px] p-6 shadow-xs border-0 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-medium text-[#0b57d0]">
              <Mic className="w-4 h-4 text-[#0b57d0]" />
              <span>Tu Nota de Voz Clínica Registrada</span>
            </div>
            <span className="text-[11px] text-[#747775]">Evaluada directamente por la IA multimodal</span>
          </div>
          {audioUrl ? (
            <div className="bg-[#f0f4f9] p-3 rounded-[16px] flex items-center">
              <audio controls src={audioUrl} className="w-full h-10 accent-[#0b57d0]" />
            </div>
          ) : (
            <div className="bg-[#f0f4f9] p-4 rounded-[16px] text-xs sm:text-sm text-[#1f1f1f] leading-relaxed italic border-l-3 border-[#0b57d0]">
              "{result.transcripcion_audio}"
            </div>
          )}
        </div>
      )}

      {studentAnswer && (
        <div className="bg-white rounded-[28px] p-6 shadow-xs border-0 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-medium text-[#444746]">
              <User className="w-4 h-4 text-[#0b57d0]" />
              <span>Tu Razonamiento Clínico Registrado (Texto)</span>
            </div>
          </div>
          <div className="bg-[#f0f4f9] p-4 rounded-[16px] text-xs sm:text-sm text-[#1f1f1f] leading-relaxed whitespace-pre-wrap">
            {studentAnswer}
          </div>
        </div>
      )}

      {/* 3. Gráfico Interactivo de Radar de Habilidades (4 Ejes) */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border-0">
        <SkillRadarChart competenciasPorEje={competenciasPorEje} />
      </div>

      {/* 3b. Faithfulness Score */}
      {result.faithfulness_score !== undefined && result.faithfulness_score !== null && (
        <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border-0 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-blue-600 shrink-0" />
              <div>
                <p className="text-xs font-medium text-blue-700 uppercase tracking-wider">
                  Verificación de Fidelidad Normativa
                </p>
                <h3 className="text-sm font-semibold text-slate-900 font-heading">
                  Fidelidad con la Guía de Práctica Clínica (GPC Ecuador)
                </h3>
              </div>
            </div>
            <span className={`text-sm font-bold px-4 py-1.5 rounded-full ${
              result.faithfulness_score >= 0.80
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-amber-50 text-amber-700 border border-amber-200'
            }`}>
              {(result.faithfulness_score * 100).toFixed(1)}% de Fidelidad
            </span>
          </div>
        </div>
      )}

      {/* 4. Aciertos y Omisiones Clínicas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Aciertos */}
        <div className="bg-white rounded-[28px] p-6 shadow-xs border-0 space-y-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800 border-b border-slate-100 pb-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Aciertos Normativos Identificados ({aciertos.length})</span>
          </div>
          <ul className="space-y-2 text-xs text-[#1f1f1f]">
            {aciertos.map((a, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-600 font-bold">•</span>
                <span>{a}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Omisiones */}
        <div className="bg-white rounded-[28px] p-6 shadow-xs border-0 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-amber-800">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
              <span>Omisiones Formativas y Mejoras ({omisiones.length})</span>
            </div>
            {omisiones.length > 0 && (
              <button
                type="button"
                onClick={() => handleOpenDebrief(omisiones)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-[#0b57d0] border border-blue-200/60 hover:border-blue-300/90 shadow-2xs active:scale-95 transition-all cursor-pointer self-start sm:self-auto"
                title="Iniciar sesión de debriefing socrático sobre todas las omisiones del caso"
              >
                <MessageSquare className="w-3.5 h-3.5 text-[#0b57d0]" />
                <span>Debate Socrático Integral</span>
              </button>
            )}
          </div>
          <ul className="space-y-2.5 text-xs text-[#1f1f1f]">
            {omisiones.map((o, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 p-2 rounded-xl hover:bg-slate-50 transition-colors"
              >
                <span className="text-amber-600 font-bold mt-0.5">•</span>
                <span className="leading-relaxed flex-1">{o}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 5. Cita Normativa Oficial */}
      {cita_normativa && (
        <div className="bg-white rounded-[28px] p-6 shadow-xs border-0 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#0b57d0]">
              <BookOpen className="w-4 h-4" />
              <span>Cita Normativa Oficial</span>
            </div>
            {cita_normativa.pagina && (
              <span className="text-xs text-[#747775]">Pág. {cita_normativa.pagina}</span>
            )}
          </div>

          <div className="space-y-1">
            <p className="text-sm font-medium text-[#1f1f1f]">{cita_normativa.guia}</p>
            {cita_normativa.seccion && (
              <p className="text-xs text-[#444746] font-medium">{cita_normativa.seccion}</p>
            )}
            {cita_normativa.texto_relevante && (
              <div className="mt-2 p-3.5 bg-[#f0f4f9] rounded-[16px] text-xs text-[#1e293b] border-l-3 border-[#0b57d0] leading-relaxed">
                <ClinicalMarkdownRenderer content={cita_normativa.texto_relevante} />
              </div>
            )}
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => setPdfModalOpen(true)}
              className="text-xs font-medium text-[#0b57d0] hover:underline cursor-pointer flex items-center gap-1"
            >
              <span>Ver Guía Oficial en PDF</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* 6. Auditoría y Telemetría Clínica de Inferencia */}
      {(result.llm_latency_ms !== undefined || result.faithfulness_score !== undefined) && (
        <div className="flex flex-wrap items-center justify-between gap-2 px-5 py-2.5 rounded-[20px] bg-white border border-slate-200/80 text-[11px] text-[#444746] shadow-xs">
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-[#0b57d0]" />
            <span className="font-semibold text-[#1f1f1f]">
              Tiempo:
            </span>
            {result.llm_latency_ms !== undefined && result.llm_latency_ms > 0 ? (
              <span>
                {(result.llm_latency_ms / 1000).toFixed(2)}s
              </span>
            ) : (
              <span>--</span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {result.faithfulness_score !== undefined && (
              <span>
                Fidelidad Normativa: {Math.round(result.faithfulness_score * 100)}%
              </span>
            )}
            {result.paraclinical_studies_count !== undefined && result.paraclinical_studies_count > 0 && (
              <span>
                • {result.paraclinical_studies_count} estudio(s) paraclínico(s)
              </span>
            )}
          </div>
        </div>
      )}

      {/* Descargo Legal y Advertencia de Investigación en Desarrollo Activo */}
      <div className="pt-4 border-t border-slate-100 flex items-start gap-2.5 text-[11px] text-slate-500 leading-relaxed">
        <ShieldAlert className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        <p>
          <strong className="text-slate-700">Investigación en Desarrollo Activo:</strong> Esta evaluación y sus sugerencias normativas forman parte de una investigación clínica real en curso. Por protección legal institucional, el uso es de momento exclusivamente formativo con proyección a una versión oficial tras la validación experimental; no constituyen criterio médico vinculante ni deben emplearse en pacientes reales.
        </p>
      </div>

      {/* Botón de Reinicio */}
      {onReset && (
        <div className="flex justify-center pt-4">
          <button
            onClick={onReset}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full border border-slate-300 bg-white hover:bg-slate-50 text-xs font-medium text-[#1f1f1f] transition-colors cursor-pointer shadow-xs"
          >
            <RefreshCw className="w-3.5 h-3.5 text-[#0b57d0]" />
            <span>Intentar Caso Nuevamente</span>
          </button>
        </div>
      )}

      <PdfViewerModal
        isOpen={pdfModalOpen}
        onClose={() => setPdfModalOpen(false)}
        guiaId={cita_normativa?.guia || 'preeclampsia'}
        pagina={cita_normativa?.pagina || 1}
        seccion={cita_normativa?.seccion || ''}
      />
    </div>
  );
}
