import { lazy, Suspense, useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Send, 
  AlertCircle, 
  AlertTriangle,
  FileImage, 
  Stethoscope, 
  Activity, 
  HelpCircle,
  Layers,
  Maximize2,
  X,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Grid,
  Sliders,
  Sun,
  Contrast
} from 'lucide-react';
import useCaseSolver from '../hooks/useCaseSolver';
import FeedbackCard from '../components/FeedbackCard';
import EvaluationGameLoader from '../components/EvaluationGameLoader';
import VoiceInputButton from '../components/VoiceInputButton';
import ClinicalVoiceRecorder from '../components/ClinicalVoiceRecorder';
import ImageUploadZone from '../components/ImageUploadZone';
import SimulationStepper from '../components/SimulationStepper';
import PhaseFeedbackCard from '../components/PhaseFeedbackCard';
import SocraticDebriefModal from '../components/SocraticDebriefModal';
import { useSocraticDebriefStore } from '../store/useSocraticDebriefStore';
import ClinicalButton from '../../../core/ui/ClinicalButton';
import { ClinicalMarkdownRenderer } from '../../../core/ui/ClinicalMarkdownRenderer';
import useLearningTelemetry from '../../analytics/hooks/useLearningTelemetry';
import { FEATURE_FLAGS } from '../../../core/config/featureFlags';
import { resolveGpcMeta } from '../../cases/hooks/useCases';

const DicomStudyViewer = lazy(() => import('../components/DicomStudyViewer'));

export default function CaseSolve() {
  const { id } = useParams<{ id: string }>();

  // Limpiar y cerrar cualquier diálogo socrático remanente al cambiar de caso o salir de la resolución
  useEffect(() => {
    useSocraticDebriefStore.getState().closeDebrief();
    return () => {
      useSocraticDebriefStore.getState().closeDebrief();
    };
  }, [id]);

  const {
    caso,
    loading,
    error,
    respuesta,
    setRespuesta,
    imagenes,
    setImagenes,
    audioBlob,
    setAudioBlob,
    evaluating,
    resultado,
    isPhaseMode,
    currentPhase,
    setCurrentPhase,
    totalPhases,
    activePhaseData,
    phaseScores,
    completedPhases,
    currentPhaseResult,
    showingPhaseFeedback,
    submitSingleTurn,
    submitPhase,
    proceedToNextPhase,
    resetCase,
  } = useCaseSolver(id);

  const [studyViewerTab, setStudyViewerTab] = useState<'standard' | 'dicom'>('standard');
  const [isViewerModalOpen, setIsViewerModalOpen] = useState<boolean>(false);

  // Determinar la imagen médica activa (priorizando la fase clínica actual o el caso general)
  const activeImageUrl = isPhaseMode ? activePhaseData?.imagen_url : (caso?.imagen_url || activePhaseData?.imagen_url);

  // Estados de manipulación diagnóstica (Zoom, Paneo, Ventana y Rejilla ECG)
  const [studyZoom, setStudyZoom] = useState<number>(1.0);
  const [studyPan, setStudyPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDraggingStudy, setIsDraggingStudy] = useState<boolean>(false);
  const dragStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const [studyBrightness, setStudyBrightness] = useState<number>(100);
  const [studyContrast, setStudyContrast] = useState<number>(100);
  const [isStudyInverted, setIsStudyInverted] = useState<boolean>(false);
  const [showEcgGrid, setShowEcgGrid] = useState<boolean>(false);
  const [showFiltersPopover, setShowFiltersPopover] = useState<boolean>(false);
  const [isDictating, setIsDictating] = useState<boolean>(false);
  const [isRecordingVoiceNote, setIsRecordingVoiceNote] = useState<boolean>(false);

  const resetStudyTransformations = () => {
    setStudyZoom(1.0);
    setStudyPan({ x: 0, y: 0 });
    setStudyBrightness(100);
    setStudyContrast(100);
    setIsStudyInverted(false);
  };

  const openStudyModal = () => {
    resetStudyTransformations();
    setShowEcgGrid(Boolean(caso?.id?.toLowerCase().includes('ecg') || activeImageUrl?.toLowerCase().includes('ecg')));
    setIsViewerModalOpen(true);
  };

  const handleStudyZoomIn = () => setStudyZoom((z) => Math.min(Number((z * 1.25).toFixed(2)), 5.0));
  const handleStudyZoomOut = () => setStudyZoom((z) => Math.max(Number((z * 0.8).toFixed(2)), 0.6));

  const handleStudyWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 1.15 : 0.85;
    setStudyZoom((z) => Math.min(Math.max(Number((z * delta).toFixed(2)), 0.6), 5.0));
  };

  const handleStudyMouseDown = (e: React.MouseEvent) => {
    setIsDraggingStudy(true);
    dragStartRef.current = { x: e.clientX - studyPan.x, y: e.clientY - studyPan.y };
  };

  const handleStudyMouseMove = (e: React.MouseEvent) => {
    if (!isDraggingStudy) return;
    setStudyPan({
      x: e.clientX - dragStartRef.current.x,
      y: e.clientY - dragStartRef.current.y,
    });
  };

  const handleStudyMouseUp = () => {
    setIsDraggingStudy(false);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isViewerModalOpen) {
        setIsViewerModalOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isViewerModalOpen]);

  const { trackCaseOpened } = useLearningTelemetry();

  useEffect(() => {
    if (caso?.id) {
      trackCaseOpened(caso.id, { titulo: caso.titulo, guia: caso.guia_asociada });
    }
  }, [caso?.id, trackCaseOpened]);

  // Asegurar que al cargar el caso o al cambiar de fase/feedback la vista inicie en el tope absoluto
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' as ScrollBehavior });
    }
  }, [caso?.id]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    }
  }, [currentPhase, showingPhaseFeedback, Boolean(resultado)]);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <Activity className="w-10 h-10 text-[#0b57d0] animate-spin" />
        <p className="text-sm font-medium text-[#444746]">
          Cargando entorno de simulación clínica...
        </p>
      </div>
    );
  }

  if (error && !caso) {
    return (
      <div className="bg-white rounded-[28px] p-8 max-w-lg mx-auto text-center space-y-4 shadow-xs">
        <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
        <h2 className="text-xl font-normal text-[#1f1f1f] font-heading">
          Caso No Disponible
        </h2>
        <p className="text-xs text-[#747775]">{error}</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#f0f4f9] hover:bg-slate-200 text-[#1f1f1f] rounded-full text-xs font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Volver al Catálogo
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      
      {/* 1. Header de Simulación */}
      {(() => {
        const gpcMeta = resolveGpcMeta(caso?.guia_asociada || caso?.gpc_referencia);
        return (
          <div className="flex items-start sm:items-center justify-between gap-4 pb-3 border-b border-slate-200/80">
            <div className="flex items-center gap-3 min-w-0">
              <Link
                to="/"
                className="p-2 -ml-2 rounded-full hover:bg-slate-100 text-[#444746] transition-colors shrink-0"
                title="Volver al catálogo"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="space-y-0.5 min-w-0">
                <h1 className="text-lg sm:text-xl md:text-2xl font-normal text-[#1f1f1f] font-heading tracking-tight leading-snug">
                  {caso?.titulo}
                </h1>
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className={`font-semibold ${gpcMeta.isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                    {gpcMeta.label}
                  </span>
                  {gpcMeta.isUrgent && (
                    <span className="text-[11px] font-semibold text-rose-700">
                      • Código Rojo
                    </span>
                  )}
                  {caso?.fases && (
                    <span className="text-slate-400 font-normal">
                      • {caso.fases.length} Fases
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* Aviso de Simulación e Investigación en Desarrollo Activo */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong className="text-slate-700">Investigación en Desarrollo Activo:</strong> Caso clínico ficticio dentro de un protocolo científico en curso. Por protección legal institucional, el uso es de momento formativo y experimental rumbo a una versión oficial; no apto para decisiones en pacientes reales.
        </span>
      </div>

      {/* 2. Barra de Progreso Secuencial por Fases */}
      {isPhaseMode && !resultado && (
        <SimulationStepper
          currentPhase={currentPhase}
          totalPhases={totalPhases}
          phaseScores={phaseScores}
          completedPhases={completedPhases}
          onSelectPhase={(f) => setCurrentPhase(f)}
        />
      )}

      {/* 3. Modal de Feedback Inmediato por Fase */}
      {showingPhaseFeedback && currentPhaseResult && (
        <PhaseFeedbackCard
          phaseResult={currentPhaseResult}
          currentPhase={currentPhase}
          caseId={caso?.id}
          caseTitle={caso?.titulo}
          audioBlob={audioBlob}
          onProceedNextPhase={proceedToNextPhase}
          isLastPhase={currentPhase >= totalPhases}
        />
      )}

      {/* 4. Dictamen Formativo Global (cuando finaliza la simulación) */}
      {resultado && (
        <FeedbackCard
          result={resultado}
          studentAnswer={respuesta}
          audioBlob={audioBlob}
          onReset={resetCase}
        />
      )}

      {/* 5. Área de Trabajo Split-Screen (50% Caso / 50% Resolución) */}
      {!resultado && !showingPhaseFeedback && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Panel Izquierdo: Enunciado Clínico y Hallazgos */}
          <div className="lg:col-span-6 bg-white rounded-[24px] sm:rounded-[28px] p-5 sm:p-7 md:p-8 shadow-xs border-0 space-y-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs font-medium text-[#444746]">
                <Stethoscope className="w-4 h-4 text-[#0b57d0]" />
                <span>Presentación del Cuadro Clínico</span>
              </div>
              <h2 className="text-lg font-normal text-[#1f1f1f] font-heading leading-snug">
                {isPhaseMode && activePhaseData
                  ? (activePhaseData.titulo_fase || activePhaseData.titulo)
                  : caso?.titulo}
              </h2>
            </div>

            <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs sm:text-sm text-[#1f1f1f] leading-relaxed">
              <ClinicalMarkdownRenderer
                content={
                  isPhaseMode && activePhaseData
                    ? (activePhaseData.escenario_clinico || [activePhaseData.descripcion, activePhaseData.datos_revelados].filter(Boolean).join('\n\n'))
                    : caso?.enunciado
                }
              />
            </div>

            {/* Visor Diagnóstico de Estudio Paraclínico (Condicionado estrictamente a los estudios reales del caso) */}
            {(() => {
              const hasStandardImage = Boolean(activeImageUrl);
              const activeDicom = isPhaseMode && activePhaseData?.dicom_study ? activePhaseData.dicom_study : caso?.dicom_study;
              const hasDicomStudy = Boolean(activeDicom);

              // 1. Si el caso no tiene ningún estudio paraclínico, omitir el bloque por completo
              if (!hasStandardImage && !hasDicomStudy) {
                return null;
              }

              const studyTypeLabel = (() => {
                const targetId = (caso?.id || '').toLowerCase();
                const targetImg = (activeImageUrl || '').toLowerCase();

                if (targetId.includes('coagulograma') || targetImg.includes('coagulograma') || targetImg.includes('lab')) {
                  return 'Laboratorio Clínico';
                }
                if (targetId.includes('ecg') || targetImg.includes('ecg')) {
                  return 'Electrocardiograma';
                }
                if (targetImg.includes('rx') || targetId.includes('rx') || targetId.includes('nac') || targetImg.includes('cavitacion')) {
                  return 'Estudio Radiológico';
                }
                return 'Estudio Paraclínico';
              })();

              // 2. Si el caso tiene tanto Imagen 2D como Tomografía DICOM real, mostrar pestañas de conmutación
              if (hasStandardImage && hasDicomStudy) {
                return (
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                      <div className="flex items-center gap-6">
                        <button
                          type="button"
                          onClick={() => setStudyViewerTab('standard')}
                          className={`text-xs pb-1.5 font-medium flex items-center gap-1.5 border-b-2 transition-colors ${
                            studyViewerTab === 'standard'
                              ? 'border-blue-600 text-blue-700 font-semibold -mb-[2px]'
                              : 'border-transparent text-[#747775] hover:text-[#1f1f1f]'
                          }`}
                        >
                          <FileImage className="w-3.5 h-3.5" />
                          <span>Imagen 2D</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setStudyViewerTab('dicom')}
                          className={`text-xs pb-1.5 font-medium flex items-center gap-1.5 border-b-2 transition-colors ${
                            studyViewerTab === 'dicom'
                              ? 'border-cyan-600 text-cyan-700 font-semibold -mb-[2px]'
                              : 'border-transparent text-[#747775] hover:text-[#1f1f1f]'
                          }`}
                        >
                          <Layers className="w-3.5 h-3.5" />
                          <span>Tomografía Volumétrica DICOM</span>
                        </button>
                      </div>

                      <span className="text-[11px] text-[#747775]">
                        {studyViewerTab === 'dicom' ? 'PACS WADO-RS' : 'Estudio Paraclínico'}
                      </span>
                    </div>

                    {studyViewerTab === 'dicom' ? (
                      <Suspense
                        fallback={
                          <div className="min-h-[460px] bg-[#090d16] rounded-[24px] flex flex-col items-center justify-center space-y-3 text-slate-400 border border-slate-800">
                            <Activity className="w-7 h-7 text-cyan-400 animate-spin" />
                            <span className="text-xs font-medium">Inicializando visor tomográfico DICOM...</span>
                          </div>
                        }
                      >
                        <DicomStudyViewer study={activeDicom} />
                      </Suspense>
                    ) : (
                      <div className="relative group rounded-[20px] overflow-hidden bg-[#f0f4f9] p-3 border border-slate-200/80 shadow-xs flex items-center justify-center">
                        <img
                          src={activeImageUrl}
                          alt={caso?.titulo || 'Estudio paraclínico'}
                          className="w-full h-auto object-contain max-h-80 sm:max-h-96 rounded-[14px] mx-auto cursor-pointer transition-transform duration-200 hover:scale-[1.01]"
                          onClick={openStudyModal}
                        />
                        <button
                          type="button"
                          onClick={openStudyModal}
                          className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-xs text-[#1f1f1f] text-xs px-3 py-1.5 rounded-full shadow-xs border border-slate-200/70 flex items-center gap-1.5 opacity-90 hover:opacity-100 transition-opacity cursor-pointer"
                          title="Inspeccionar estudio paraclínico en alta resolución"
                        >
                          <Maximize2 className="w-3.5 h-3.5 text-[#0b57d0]" />
                          <span className="text-[11px] font-medium">Ampliar Estudio</span>
                        </button>
                      </div>
                    )}
                  </div>
                );
              }

              // 3. Si el caso solo tiene estudio tomográfico DICOM
              if (hasDicomStudy) {
                return (
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center justify-between pb-1">
                      <div className="flex items-center gap-2 text-xs font-semibold text-[#1f1f1f]">
                        <Layers className="w-4 h-4 text-cyan-600" />
                        <span>Tomografía Volumétrica DICOM</span>
                      </div>
                      <span className="text-[11px] text-[#747775]">PACS WADO-RS</span>
                    </div>

                    <Suspense
                      fallback={
                        <div className="min-h-[460px] bg-[#090d16] rounded-[24px] flex flex-col items-center justify-center space-y-3 text-slate-400 border border-slate-800">
                          <Activity className="w-7 h-7 text-cyan-400 animate-spin" />
                          <span className="text-xs font-medium">Inicializando visor tomográfico DICOM...</span>
                        </div>
                      }
                    >
                      <DicomStudyViewer study={activeDicom} />
                    </Suspense>
                  </div>
                );
              }

              // 4. Si el caso solo tiene estudio 2D (Radiografía, ECG o Laboratorio real)
              return (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between pb-1">
                    <div className="flex items-center gap-2 text-xs font-semibold text-[#1f1f1f]">
                      <FileImage className="w-4 h-4 text-[#0b57d0]" />
                      <span>Estudio Paraclínico Complementario</span>
                    </div>
                    <span className="text-[11px] text-[#747775]">
                      {studyTypeLabel}
                    </span>
                  </div>

                  <div className="relative group rounded-[20px] overflow-hidden bg-[#f0f4f9] p-3 border border-slate-200/80 shadow-xs flex items-center justify-center">
                    <img
                      src={activeImageUrl}
                      alt={caso?.titulo || 'Estudio paraclínico'}
                      className="w-full h-auto object-contain max-h-72 sm:max-h-80 rounded-[14px] mx-auto cursor-pointer transition-transform duration-200 hover:scale-[1.01]"
                      onClick={openStudyModal}
                    />
                    <button
                      type="button"
                      onClick={openStudyModal}
                      className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-xs text-[#1f1f1f] text-xs px-3 py-1.5 rounded-full shadow-xs border border-slate-200/70 flex items-center gap-1.5 opacity-90 hover:opacity-100 transition-opacity cursor-pointer"
                      title="Inspeccionar estudio paraclínico en alta resolución"
                    >
                      <Maximize2 className="w-3.5 h-3.5 text-[#0b57d0]" />
                      <span className="text-[11px] font-medium">Ampliar Estudio</span>
                    </button>
                  </div>
                </div>
              );
            })()}

            {/* Pregunta Orientadora */}
            <div className="p-4 bg-sky-50/60 rounded-[20px] border border-sky-100 space-y-1.5">
              <span className="text-xs font-semibold text-[#0b57d0] flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5" />
                Interrogante Formativa
              </span>
              <div className="text-xs sm:text-sm text-[#1f1f1f] leading-relaxed">
                <ClinicalMarkdownRenderer
                  compact
                  content={
                    (isPhaseMode && activePhaseData
                      ? (activePhaseData.pregunta_orientadora || activePhaseData.pregunta_evaluativa || activePhaseData.pregunta_fase)
                      : caso?.pregunta) || 'Plantee su juicio diagnóstico, exámenes prioritarios y esquema terapéutico de acuerdo a la GPC oficial de Ecuador.'
                  }
                />
              </div>
            </div>
          </div>

          {/* Panel Derecho: Área de Resolución Diagnóstica */}
          <div className="lg:col-span-6 bg-white rounded-[24px] sm:rounded-[28px] p-5 sm:p-7 md:p-8 shadow-xs border-0 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-100">
              <div className="space-y-0.5">
                <h3 className="text-base font-normal text-[#1f1f1f] font-heading">
                  {isPhaseMode ? `Tu Resolución Clínica — Fase ${currentPhase}` : 'Tu Resolución Clínica'}
                </h3>
                <p className="text-xs text-[#747775]">
                  {isPhaseMode
                    ? currentPhase === 1
                      ? 'Escribe o dicta tu sospecha diagnóstica, signos de alarma y criterios de severidad para esta fase'
                      : currentPhase === 2
                        ? 'Escribe o dicta tu solicitud e interpretación de paraclínicos y afectación orgánica'
                        : currentPhase === 3
                          ? 'Escribe o dicta tu esquema terapéutico, dosificación normada y conducta clínica'
                          : `Responde a la interrogante formativa de la Fase ${currentPhase} según la GPC Ecuador`
                    : 'Escribe o dicta tu razonamiento clínico estructurado (Diagnóstico, Tratamiento, Prevención y Seguimiento normado)'}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <VoiceInputButton
                  value={respuesta}
                  onChange={setRespuesta}
                  disabled={evaluating || isRecordingVoiceNote}
                  onRecordingChange={setIsDictating}
                />
                <ClinicalVoiceRecorder
                  onAudioChange={setAudioBlob}
                  disabled={evaluating || isDictating}
                  onRecordingStateChange={setIsRecordingVoiceNote}
                />
              </div>
            </div>

            <form
              onSubmit={isPhaseMode ? submitPhase : submitSingleTurn}
              className="space-y-5"
            >
              <div>
                <textarea
                  id="clinical-answer-input"
                  rows={7}
                  value={respuesta}
                  onChange={(e) => setRespuesta(e.target.value)}
                  disabled={evaluating}
                  placeholder={
                    audioBlob 
                      ? "Opcional: agrega notas escritas complementarias a tu nota de voz..."
                      : isPhaseMode
                        ? currentPhase === 1
                          ? "Describe tu sospecha diagnóstica sindrómica, signos de severidad identificados y conducta clínica inicial según la GPC..."
                          : currentPhase === 2
                            ? "Detalla los estudios paraclínicos solicitados, interpretación de hallazgos analíticos u órganos afectados y confirmación diagnóstica..."
                            : currentPhase === 3
                              ? "Detalla el esquema terapéutico normado, fármacos de primera línea, dosificación, vías de administración y plan de seguimiento..."
                              : "Redacta tu fundamentación clínica orientada a responder puntualmente la interrogante formativa de esta fase..."
                        : "Detalla tu sospecha diagnóstica, estudios prioritarios, esquema terapéutico de primera línea y plan de seguimiento según la GPC oficial del MSP Ecuador..."
                  }
                  className="w-full p-4 bg-[#f0f4f9] rounded-[20px] text-sm text-[#1f1f1f] border border-slate-200/80 focus:outline-none focus:border-[#0b57d0] focus:bg-white transition-all leading-relaxed placeholder:text-[#747775] resize-none"
                  required={!audioBlob}
                />
              </div>

              {/* Subida de Estudios Diagnósticos Multimodales (Gobernado por Feature Flag) */}
              {FEATURE_FLAGS.ENABLE_STUDENT_IMAGE_UPLOAD && (
                <ImageUploadZone
                  files={imagenes}
                  onChange={setImagenes}
                  disabled={evaluating}
                />
              )}

              {error && (
                <div className="p-3.5 bg-rose-50 border border-rose-200/80 rounded-[16px] flex items-start gap-2.5 text-xs text-rose-800 animate-fadeIn">
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                  <span className="leading-snug">{error}</span>
                </div>
              )}

              <div className="flex items-center justify-end pt-2">
                <ClinicalButton
                  type="submit"
                  variant="primary"
                  size="md"
                  className="w-full sm:w-auto min-h-[44px]"
                  loading={evaluating}
                  disabled={(!respuesta.trim() && !audioBlob) || evaluating}
                  icon={Send}
                >
                  {isPhaseMode
                    ? `Evaluar Fase ${currentPhase}`
                    : (audioBlob && !respuesta.trim() ? 'Evaluar Nota de Voz' : 'Emitir Diagnóstico')}
                </ClinicalButton>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Loader de Juego Evaluador */}
      {evaluating && (
        <EvaluationGameLoader hasImage={FEATURE_FLAGS.ENABLE_STUDENT_IMAGE_UPLOAD && imagenes.length > 0} />
      )}

      {/* Modal de Debate y Debriefing Socrático Multiturno */}
      <SocraticDebriefModal />

      {/* Modal de Estudio Paraclínico de Referencia (Ateneo+ Design System con Herramientas) */}
      {isViewerModalOpen && activeImageUrl && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="paraclinical-modal-title"
          className="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-5 bg-slate-900/60 backdrop-blur-sm animate-fadeIn"
          onClick={() => {
            setShowFiltersPopover(false);
            setIsViewerModalOpen(false);
          }}
        >
          <div
            className="bg-white w-full max-w-5xl rounded-[28px] shadow-2xl flex flex-col max-h-[90vh] overflow-hidden animate-scaleUp"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Cabecera Institucional con Herramientas Diagnósticas Integradas */}
            <div className="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between gap-3 select-none">
              <div className="flex items-center space-x-3 min-w-0">
                <FileImage className="w-6 h-6 text-[#0b57d0] shrink-0" />
                <div className="min-w-0">
                  <h2 id="paraclinical-modal-title" className="text-sm sm:text-base font-semibold text-slate-900 tracking-tight truncate">
                    Estudio Paraclínico de Referencia
                  </h2>
                  <p className="text-xs text-slate-500 font-medium truncate max-w-xs sm:max-w-md md:max-w-lg">
                    {caso?.titulo || 'Simulación Clínica Formativa'}
                  </p>
                </div>
              </div>

              {/* Botonera de Herramientas Clínicas */}
              <div className="flex items-center gap-1 shrink-0">
                <button
                  type="button"
                  onClick={handleStudyZoomOut}
                  className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                  title="Alejar imagen (Zoom Out)"
                  aria-label="Alejar imagen"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <span className="text-[11px] font-mono text-slate-600 px-1 select-none min-w-[36px] text-center">
                  {(studyZoom * 100).toFixed(0)}%
                </span>
                <button
                  type="button"
                  onClick={handleStudyZoomIn}
                  className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                  title="Acercar imagen (Zoom In)"
                  aria-label="Acercar imagen"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={resetStudyTransformations}
                  className="p-1.5 text-slate-500 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                  title="Restablecer vista"
                  aria-label="Restablecer vista"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>

                <div className="w-[1px] h-4 bg-slate-200 mx-1" />

                <button
                  type="button"
                  onClick={() => setShowEcgGrid((prev) => !prev)}
                  className={`p-1.5 rounded-lg transition-colors ${
                    showEcgGrid
                      ? 'text-rose-600 bg-rose-50 border border-rose-200'
                      : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                  title="Rejilla Milimétrica ECG (25mm/s)"
                  aria-label="Rejilla ECG"
                >
                  <Grid className="w-4 h-4" />
                </button>

                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setShowFiltersPopover((prev) => !prev)}
                    className={`p-1.5 rounded-lg transition-colors ${
                      showFiltersPopover
                        ? 'text-[#0b57d0] bg-blue-50 border border-blue-200'
                        : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                    title="Calibración de Ventana Radiológica"
                    aria-label="Ajuste de filtros"
                  >
                    <Sliders className="w-4 h-4" />
                  </button>

                  {/* Popover de Ventana Radiológica */}
                  {showFiltersPopover && (
                    <div
                      className="absolute top-10 right-0 z-30 bg-white p-4 rounded-[20px] border border-slate-200 text-xs text-slate-800 space-y-3 w-56 shadow-xl animate-fadeIn"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="font-semibold text-slate-900 border-b border-slate-100 pb-1.5 flex items-center justify-between">
                        <span>Ventana Radiológica</span>
                        <button
                          type="button"
                          onClick={() => {
                            setStudyBrightness(100);
                            setStudyContrast(100);
                            setIsStudyInverted(false);
                          }}
                          className="text-[10px] text-[#0b57d0] hover:underline font-normal"
                        >
                          Reset
                        </button>
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-[11px] text-slate-600">
                          <span className="flex items-center gap-1.5">
                            <Sun className="w-3.5 h-3.5 text-[#0b57d0]" />
                            Brillo
                          </span>
                          <span className="font-mono">{studyBrightness}%</span>
                        </div>
                        <input
                          type="range"
                          min={40}
                          max={180}
                          value={studyBrightness}
                          onChange={(e) => setStudyBrightness(Number(e.target.value))}
                          className="w-full accent-[#0b57d0] cursor-pointer h-1.5 bg-slate-200 rounded-lg"
                        />
                      </div>

                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-[11px] text-slate-600">
                          <span className="flex items-center gap-1.5">
                            <Contrast className="w-3.5 h-3.5 text-[#0b57d0]" />
                            Contraste
                          </span>
                          <span className="font-mono">{studyContrast}%</span>
                        </div>
                        <input
                          type="range"
                          min={50}
                          max={220}
                          value={studyContrast}
                          onChange={(e) => setStudyContrast(Number(e.target.value))}
                          className="w-full accent-[#0b57d0] cursor-pointer h-1.5 bg-slate-200 rounded-lg"
                        />
                      </div>

                      <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                        <span className="text-[11px] text-slate-600">Inversión Negativo</span>
                        <button
                          type="button"
                          onClick={() => setIsStudyInverted((inv) => !inv)}
                          className={`px-3 py-1 rounded-full text-[10px] font-medium transition-colors ${
                            isStudyInverted
                              ? 'bg-[#0b57d0] text-white font-medium shadow-xs'
                              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                          }`}
                        >
                          {isStudyInverted ? 'Activo' : 'Invertir'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                <div className="w-[1px] h-4 bg-slate-200 mx-1" />

                <button
                  type="button"
                  onClick={() => setIsViewerModalOpen(false)}
                  className="text-slate-400 hover:text-slate-700 p-1.5 rounded-full transition-colors hover:bg-slate-100"
                  aria-label="Cerrar estudio paraclínico"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Contenedor Interactivo de Estudio Diagnóstico con Paneo y Zoom */}
            <div
              className={`relative p-4 sm:p-6 bg-[#f0f4f9] flex items-center justify-center overflow-hidden h-[72vh] select-none ${
                isDraggingStudy ? 'cursor-grabbing' : 'cursor-grab'
              }`}
              onWheel={handleStudyWheel}
              onMouseDown={handleStudyMouseDown}
              onMouseMove={handleStudyMouseMove}
              onMouseUp={handleStudyMouseUp}
              onMouseLeave={handleStudyMouseUp}
            >
              <div
                className="relative flex items-center justify-center transition-transform duration-75 ease-out"
                style={{
                  transform: `translate(${studyPan.x}px, ${studyPan.y}px) scale(${studyZoom})`,
                  transformOrigin: 'center center',
                }}
              >
                <img
                  src={activeImageUrl}
                  alt={caso?.titulo || 'Estudio paraclínico de referencia'}
                  draggable={false}
                  className="max-h-[66vh] max-w-full w-auto object-contain rounded-[16px] shadow-xs select-none pointer-events-none"
                  style={{
                    filter: `brightness(${studyBrightness}%) contrast(${studyContrast}%) invert(${isStudyInverted ? 100 : 0}%)`,
                  }}
                />

                {showEcgGrid && (
                  <div
                    className="absolute inset-0 pointer-events-none rounded-[16px] overflow-hidden"
                    style={{
                      backgroundImage: `
                        linear-gradient(to right, rgba(239, 68, 68, 0.28) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(239, 68, 68, 0.28) 1px, transparent 1px),
                        linear-gradient(to right, rgba(220, 38, 38, 0.6) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(220, 38, 38, 0.6) 1px, transparent 1px)
                      `,
                      backgroundSize: '16px 16px, 16px 16px, 80px 80px, 80px 80px',
                    }}
                  />
                )}
              </div>

              {/* Indicador de Rejilla Calibrada en Esquina Inferior */}
              {showEcgGrid && (
                <div className="absolute bottom-4 left-6 pointer-events-none z-10">
                  <span className="bg-white/95 backdrop-blur-xs text-rose-600 font-mono text-[10px] px-2.5 py-1 rounded-full border border-rose-200 shadow-xs">
                    Rejilla Calibrada: 25mm/s (0.04s/mm)
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
