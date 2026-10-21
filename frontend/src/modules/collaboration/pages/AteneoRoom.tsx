import { useMemo, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { 
  Users, 
  Play, 
  CheckCircle2, 
  ArrowLeft, 
  Send, 
  BookOpen, 
  AlertTriangle,
  Activity,
  Award,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  RotateCcw,
  FileText,
  User,
  PenTool
} from 'lucide-react';
import useAteneoRoom, { RoomParticipantDetail } from '../hooks/useAteneoRoom';
import VoiceRoomBar from '../components/VoiceRoomBar';
import ClinicalButton from '../../../core/ui/ClinicalButton';
import ClinicalBadge from '../../../core/ui/ClinicalBadge';
import { ClinicalMarkdownRenderer } from '../../../core/ui';
import type { User as UserType, UserRole } from '../../../types';

/**
 * AteneoRoom — Sala Colaborativa de Simulación Sincrónica (Ateneo+)
 * Permite a los docentes moderar ateneos clínicos en tiempo real, transicionar fases,
 * alternar entre modalidad individual o lienzo grupal con co-escritura en vivo con WebSockets,
 * e inspeccionar el razonamiento diagnóstico y la retroalimentación RAG.
 */
export default function AteneoRoom() {
  const { roomCode = '' } = useParams<{ roomCode: string }>();
  const cleanRoomCode = (roomCode || '').toUpperCase().trim();
  const { user } = useAuth();
  const [copiedCode, setCopiedCode] = useState<boolean>(false);
  const [expandedParticipantEmail, setExpandedParticipantEmail] = useState<string | null>(null);

  const currentUser = useMemo<UserType>(() => user || {
    id: 'usr_alumno_001',
    email: 'alumno@ateneo.edu.ec',
    nombre: 'Estudiante María José Silva',
    rol: 'alumno' as UserRole
  }, [user]);

  const isDocente = currentUser.rol === 'docente' || currentUser.rol === 'administrador';

  const {
    room,
    loading,
    error,
    studentAnswer,
    setStudentAnswer,
    submitting,
    submittedEval,
    connectionStatus,
    connectedCount,
    // Dual Modes
    modoResolucion,
    collaborativeText,
    handleCollaborativeTextChange,
    activeTypers,
    groupEvalResult,
    submittingGroup,
    submitGroupVerdict,
    // Standard Actions
    updateRoomStatus,
    submitAnswer,
  } = useAteneoRoom(cleanRoomCode, currentUser);

  const handleCopyCode = useCallback(async () => {
    const code = room?.room_code || room?.codigo || roomCode;
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    } catch {
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    }
  }, [room, roomCode]);

  const toggleExpandParticipant = (email: string) => {
    setExpandedParticipantEmail(prev => prev === email ? null : email);
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <Activity className="w-10 h-10 text-[#0b57d0] animate-spin" />
        <p className="text-sm font-medium text-[#444746]">
          Sincronizando estado de la Sala de Ateneo...
        </p>
      </div>
    );
  }

  if (error || !room) {
    return (
      <div className="bg-white rounded-[28px] p-8 max-w-lg mx-auto text-center space-y-4 shadow-xs mt-12">
        <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto" />
        <h2 className="text-xl font-normal text-[#1f1f1f] font-heading">
          Sala no disponible
        </h2>
        <p className="text-xs text-[#747775]">{error || 'La sala de Ateneo ha finalizado o no existe.'}</p>
        <Link
          to={isDocente ? "/teacher/cases" : "/"}
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#f0f4f9] hover:bg-slate-200 text-[#1f1f1f] rounded-full text-xs font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{isDocente ? "Volver a Mis Salas" : "Volver al Catálogo"}</span>
        </Link>
      </div>
    );
  }

  const roomDetails = room;
  const rawState = (roomDetails?.estado || 'espera').toLowerCase();
  // Normalizar estado activo para tolerar aliases
  const activePhase = rawState === 'resolviendo' ? 'resolucion'
    : rawState === 'consenso' ? 'discusion'
    : rawState === 'cerrada' ? 'finalizado'
    : rawState;

  const rawParticipants = (roomDetails?.participantes || {}) as Record<string, RoomParticipantDetail>;
  const participantesList: RoomParticipantDetail[] = Object.values(rawParticipants);
  const totalParticipantes = participantesList.length;
  const respondieronCount = participantesList.filter(p => p.respondido).length;
  const consenso = roomDetails?.analitica_consenso;

  const scorePromedio = consenso?.score_promedio ?? consenso?.promedio_sala ?? 0;
  const participationPct = consenso?.porcentaje_participacion ?? (totalParticipantes > 0 ? Math.round((respondieronCount / totalParticipantes) * 100) : 0);
  const codeToDisplay = roomDetails.room_code || room.codigo || roomCode;
  const isConsensusPhase = activePhase === 'discusion' || activePhase === 'finalizado';

  const rankingParticipantes = (() => {
    const conResultado = participantesList.filter(p => p.respondido && p.resultado_evaluacion);
    const sinResultado = participantesList.filter(p => !p.respondido || !p.resultado_evaluacion);
    conResultado.sort((a, b) => (b.resultado_evaluacion?.score ?? 0) - (a.resultado_evaluacion?.score ?? 0));
    return [...conResultado, ...sinResultado];
  })();

  return (
    <div className="space-y-6 animate-fadeIn pb-16">
      
      {/* 1. Cabecera Institucional de la Sala */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-3 border-b border-slate-200/80">
        <div className="flex items-center gap-3">
          <Link
            to={isDocente ? "/teacher/cases" : "/"}
            className="p-2 rounded-full hover:bg-slate-100 text-[#444746] transition-colors"
            title="Salir de la sala"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex flex-wrap items-center gap-2 sm:gap-2.5 text-xs font-medium text-[#0b57d0]">
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5" />
                <span>Sala Colaborativa de Ateneo Sincrónico</span>
              </div>
              
              {/* Código de sala interactivo y destacado para proyección en aula */}
              <button
                type="button"
                onClick={handleCopyCode}
                className="inline-flex items-center gap-2 px-3.5 py-1 sm:py-1.5 rounded-full bg-white hover:bg-blue-50/70 border border-blue-200/90 shadow-2xs font-mono font-bold text-sm sm:text-base text-[#0b57d0] hover:text-blue-800 tracking-wider transition-all cursor-pointer active:scale-95"
                title="Copiar código de acceso para los alumnos"
              >
                <span className="select-all">{codeToDisplay}</span>
                {copiedCode ? (
                  <span className="inline-flex items-center gap-1 text-emerald-600 text-xs font-semibold">
                    <Check className="w-4 h-4 stroke-[2.5]" />
                    <span>Copiado</span>
                  </span>
                ) : (
                  <Copy className="w-4 h-4 text-blue-500 hover:text-blue-700 transition-colors" />
                )}
              </button>

              {/* Badge de Presencia y Conexión en Tiempo Real */}
              <span
                data-testid="connection-status-pill"
                className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium transition-colors ${
                  connectionStatus === 'CONNECTED'
                    ? 'bg-white text-emerald-700 border border-emerald-300'
                    : connectionStatus === 'RECONNECTING' || connectionStatus === 'CONNECTING'
                    ? 'bg-white text-amber-700 border border-amber-300'
                    : 'bg-white text-slate-600 border border-slate-200'
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    connectionStatus === 'CONNECTED'
                      ? 'bg-emerald-500 animate-pulse'
                      : connectionStatus === 'RECONNECTING' || connectionStatus === 'CONNECTING'
                      ? 'bg-amber-500 animate-pulse'
                      : 'bg-slate-400'
                  }`}
                />
                <span>
                  {connectionStatus === 'CONNECTED'
                    ? `En vivo (${connectedCount || totalParticipantes})`
                    : connectionStatus === 'RECONNECTING'
                    ? 'Reconectando...'
                    : 'Modo Seguro (Sondeo)'}
                </span>
              </span>

              {/* Badge de Modalidad Pedagógica (Individual / Grupal) */}
              <div className="inline-flex items-center gap-1.5">
                <span
                  data-testid="room-mode-pill"
                  className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${
                    modoResolucion === 'grupal'
                      ? 'bg-indigo-50 border-indigo-200 text-indigo-800'
                      : 'bg-blue-50 border-blue-200 text-[#0b57d0]'
                  }`}
                >
                  {modoResolucion === 'grupal' ? (
                    <>
                      <Users className="w-3 h-3 text-indigo-600" />
                      <span>Ateneo Grupal (Co-escritura)</span>
                    </>
                  ) : (
                    <>
                      <User className="w-3 h-3 text-[#0b57d0]" />
                      <span>Resolución Individual</span>
                    </>
                  )}
                </span>
              </div>
            </div>

            <h1 className="text-xl sm:text-2xl font-normal text-[#1f1f1f] font-heading tracking-tight mt-1">
              {roomDetails.case_title || 'Caso Clínico de Ateneo'}
            </h1>
          </div>
        </div>

        {/* 1.1 Controles de Moderación del Docente */}
        <div className="flex items-center gap-3 self-start md:self-auto">
          {isDocente ? (
            <div className="flex items-center gap-2">
              {activePhase === 'espera' && (
                <ClinicalButton
                  variant="primary"
                  size="sm"
                  onClick={() => updateRoomStatus('resolucion')}
                  icon={Play}
                >
                  Iniciar Fase de Resolución
                </ClinicalButton>
              )}

              {activePhase === 'resolucion' && (
                <ClinicalButton
                  variant="primary"
                  size="sm"
                  onClick={() => updateRoomStatus('discusion')}
                  icon={Award}
                >
                  Abrir Consenso y Discusión
                </ClinicalButton>
              )}

              {activePhase === 'discusion' && (
                <ClinicalButton
                  variant="danger"
                  size="sm"
                  onClick={() => updateRoomStatus('finalizado')}
                >
                  Finalizar Sesión
                </ClinicalButton>
              )}

              {activePhase === 'finalizado' && (
                <ClinicalButton
                  variant="secondary"
                  size="sm"
                  onClick={() => updateRoomStatus('discusion')}
                  icon={RotateCcw}
                >
                  Reabrir Discusión
                </ClinicalButton>
              )}
            </div>
          ) : (
            <ClinicalBadge
              variant={
                activePhase === 'resolucion'
                  ? 'primary'
                  : activePhase === 'discusion'
                  ? 'success'
                  : 'default'
              }
            >
              Fase: {activePhase.toUpperCase()}
            </ClinicalBadge>
          )}
        </div>
      </div>

      {/* Aviso de Simulación e Investigación en Desarrollo Activo */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong className="text-slate-700">Investigación en Desarrollo Activo:</strong> Caso clínico ficticio dentro de un protocolo científico en curso. Por protección legal institucional, el uso es de momento formativo y experimental rumbo a una versión oficial; no apto para decisiones en pacientes reales.
        </span>
      </div>

      {/* 1.2 Pipeline / Stepper de Fases del Ateneo */}
      <div className="bg-white rounded-[22px] px-5 py-3 border border-slate-200/80 shadow-xs flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 sm:gap-6 w-full justify-between sm:justify-start">
          {[
            { key: 'espera', label: '1. Espera', desc: 'Ingreso' },
            { key: 'resolucion', label: '2. Resolución', desc: modoResolucion === 'grupal' ? 'Co-escritura Grupal' : 'Dictamen Individual' },
            { key: 'discusion', label: '3. Discusión', desc: 'Consenso Grupal' },
            { key: 'finalizado', label: '4. Finalizado', desc: 'Cierre Clínico' },
          ].map((step, idx) => {
            const isCurrent = activePhase === step.key;
            const isPassed = 
              (activePhase === 'resolucion' && idx === 0) ||
              (activePhase === 'discusion' && idx <= 1) ||
              (activePhase === 'finalizado' && idx <= 2);

            const StepContent = (
              <>
                <span
                  className={`flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-semibold transition-colors ${
                    isCurrent
                      ? 'bg-[#0b57d0] text-white shadow-xs'
                      : isPassed
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  {isPassed ? '✓' : idx + 1}
                </span>
                <span className={`font-medium ${isCurrent ? 'inline text-[#0b57d0]' : isPassed ? 'hidden sm:inline text-slate-800' : 'hidden sm:inline text-slate-400'}`}>
                  {step.label}
                </span>
              </>
            );

            return (
              <div key={step.key} className="flex items-center gap-2">
                {isDocente ? (
                  <button
                    type="button"
                    onClick={() => updateRoomStatus(step.key)}
                    className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity focus:outline-none"
                    title={`Cambiar a fase: ${step.label}`}
                  >
                    {StepContent}
                  </button>
                ) : (
                  <div className="flex items-center gap-2">
                    {StepContent}
                  </div>
                )}
                {idx < 3 && <span className="text-slate-300 hidden sm:inline ml-2">•</span>}
              </div>
            );
          })}
        </div>

        <div className="hidden md:flex items-center gap-2 text-[11px] text-[#747775]">
          <span>Moderador: </span>
          <strong className="text-slate-800 font-medium">{roomDetails.docente_nombre || 'Docente Tutor'}</strong>
        </div>
      </div>

      {/* 2. Barra de Control de Audio y Debriefing Sincrónico WebRTC */}
      <VoiceRoomBar
        roomCode={codeToDisplay}
        userId={currentUser.id || currentUser.email}
        userName={currentUser.nombre}
        isDocente={isDocente}
      />

      {/* 3. Panel de Inteligencia Colectiva y Consenso (Docente en todo momento, y Estudiantes en fase de discusión/cierre) */}
      {(isDocente || activePhase === 'discusion' || activePhase === 'finalizado') && (consenso || respondieronCount > 0) && (
        <div className="bg-white rounded-[28px] p-6 shadow-xs border border-slate-200/80 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#0b57d0]">
              <Activity className="w-4 h-4 text-[#0b57d0]" />
              <span>Consenso Diagnóstico de la Cohorte ({participationPct}% de quórum)</span>
            </div>
            <span className="text-xs text-[#747775]">
              {respondieronCount} de {totalParticipantes} dictámenes emitidos
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
            <div className="p-4 bg-[#f0f4f9] rounded-[20px]">
              <span className="text-xs text-[#747775] block font-medium">Puntaje Promedio de Sala</span>
              <p className="text-2xl font-normal text-[#1f1f1f] font-heading mt-1">
                {scorePromedio} <span className="text-sm text-slate-500 font-sans">/ 10</span>
              </p>
            </div>

            <div className="p-4 bg-[#f0f4f9] rounded-[20px] sm:col-span-2 flex flex-col justify-between">
              <div>
                <span className="text-xs text-[#747775] font-medium block">Nivel de Alineación Clínica (GPC Ecuador)</span>
                <p className="text-sm font-semibold text-[#0b57d0] mt-1">
                  {consenso?.nivel_consenso || 'Evaluación en proceso de quórum'}
                </p>
              </div>

              {consenso?.top_brechas_sala && consenso.top_brechas_sala.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-200/60">
                  <span className="text-[11px] font-semibold text-slate-700 block mb-1">
                    Brechas Clínicas Comunes Identificadas por la IA:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {consenso.top_brechas_sala.map((item, i) => (
                      <span
                        key={i}
                        className="text-[11px] bg-white px-2.5 py-1 rounded-full border border-slate-200 text-slate-800"
                      >
                        {item.brecha} ({item.porcentaje}% del grupo)
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 4. Área de Simulación Split-Screen: Caso Clínico (50%) / Resolución Diagnóstica (50%) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Columna Izquierda (50%): Cuadro Clínico de la Sala */}
        <div className="lg:col-span-6 bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-6">
          <div className="space-y-1.5">
            <span className="text-xs font-semibold text-[#0b57d0] flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" />
              <span>Simulación Clínica Moderada</span>
            </span>
            <h2 className="text-lg font-medium text-[#1f1f1f] font-heading">
              {roomDetails.case_title || 'Caso Clínico'}
            </h2>
          </div>

          <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs sm:text-sm text-[#1f1f1f] leading-relaxed">
            <ClinicalMarkdownRenderer content={roomDetails.case_enunciado} />
          </div>

          {roomDetails.case_pregunta && (
            <div className="p-4 bg-white rounded-[18px] border border-blue-200 text-xs text-slate-800 space-y-1">
              <span className="text-[11px] font-semibold text-[#0b57d0] block">Interrogante Formativa del Ateneo:</span>
              <ClinicalMarkdownRenderer content={roomDetails.case_pregunta} compact />
            </div>
          )}

          {/* Guía Pedagógica para el Docente */}
          {isDocente && (
            <div className="p-4 bg-[#f0f4f9] rounded-[20px] border border-slate-200/70 text-xs text-[#444746] space-y-1">
              <span className="font-semibold text-slate-800 block">Instrucciones de Moderación Docente:</span>
              <p className="leading-relaxed">
                {modoResolucion === 'grupal' ? (
                  <>
                    {activePhase === 'espera' && "Sala configurada en Modo Ateneo en Grupo (Co-escritura en Vivo). Espera a que los estudiantes se conecten y pulsa 'Iniciar Fase de Resolución'."}
                    {activePhase === 'resolucion' && "Tus estudiantes redactan colectivamente en el lienzo sincrónico en vivo. Observa las adiciones en tiempo real e indicadores de quién escribe. Cuando el consenso esté formulado, pulsen 'Emitir Dictamen de Consenso Grupal'."}
                    {activePhase === 'discusion' && "Revisen la evaluación formativa del dictamen grupal generada por la IA frente a la GPC. Modera el debriefing socrático colectivo."}
                    {activePhase === 'finalizado' && "Sesión de ateneo grupal finalizada. El dictamen consolidado está guardado en el expediente."}
                  </>
                ) : (
                  <>
                    {activePhase === 'espera' && "Asegúrate de que tus alumnos ingresen con el código de sala. Cuando estén listos, presiona 'Iniciar Fase de Resolución'."}
                    {activePhase === 'resolucion' && "Los estudiantes están redactando sus diagnósticos individuales. Observa en la columna derecha las entregas en tiempo real. Cuando haya quórum suficiente, pulsa 'Abrir Consenso y Discusión'."}
                    {activePhase === 'discusion' && "Haz clic en cada estudiante en la columna derecha para auditar su dictamen y retroalimentación RAG. Conduce el debriefing socrático sobre las brechas detectadas."}
                    {activePhase === 'finalizado' && "La sesión de ateneo ha concluido. Los resultados están guardados en el historial de la cohorte."}
                  </>
                )}
              </p>
            </div>
          )}
        </div>

        {/* Columna Derecha (50%): Resolución Activa / Co-escritura y Participantes */}
        <div className="lg:col-span-6 space-y-6">

          {/* MODALIDAD 1: MODO ATENEO EN GRUPO (CO-ESCRITURA EN VIVO CON WEBSOCKETS) */}
          {modoResolucion === 'grupal' && (
            <>
              {/* FASE 1: ESPERA Y LOBBY DE CONEXIÓN */}
              {activePhase === 'espera' && (
                <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-5">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span className="text-xs font-semibold text-[#0b57d0] flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5" />
                      <span>Fase 1: Antesala y Conexión de la Cohorte</span>
                    </span>
                    <ClinicalBadge variant="default" size="sm">Lobby en Espera</ClinicalBadge>
                  </div>

                  <div className="py-6 text-center space-y-3">
                    <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center mx-auto text-[#0b57d0]">
                      <Users className="w-6 h-6" />
                    </div>
                    <h3 className="text-lg font-medium text-[#1f1f1f] font-heading">
                      {isDocente ? 'Esperando Conexión de Estudiantes' : 'Antesala del Ateneo Clínico'}
                    </h3>
                    <p className="text-xs text-[#747775] max-w-md mx-auto leading-relaxed">
                      {isDocente ? (
                        <>
                          Comparte el código de acceso con tus estudiantes. Actualmente hay <strong className="text-slate-800">{totalParticipantes} participantes</strong> conectados. Cuando haya quórum, pulsa el botón para desbloquear el lienzo sincrónico.
                        </>
                      ) : (
                        <>
                          Te encuentras en la sala de espera. Revisa detalladamente la viñeta clínica en la columna izquierda. El lienzo de co-escritura en vivo se activará automáticamente cuando el docente tutor inicie la <strong>Fase 2 de Resolución</strong>.
                        </>
                      )}
                    </p>

                    {/* Código de Sala Proyectable en Grande para el Aula */}
                    <div className="pt-2 flex flex-col items-center gap-1">
                      <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wider">Código de Acceso a la Sala</span>
                      <button
                        type="button"
                        onClick={handleCopyCode}
                        className="inline-flex items-center gap-3 px-5 py-2 rounded-2xl bg-blue-50/70 hover:bg-blue-100/70 border border-blue-200 transition-all cursor-pointer group active:scale-95 shadow-2xs"
                        title="Clic para copiar código de acceso"
                      >
                        <span className="font-mono text-2xl sm:text-3xl font-bold tracking-widest text-[#0b57d0] group-hover:text-blue-800">
                          {codeToDisplay}
                        </span>
                        {copiedCode ? (
                          <span className="inline-flex items-center gap-1 text-emerald-600 text-xs font-semibold">
                            <Check className="w-5 h-5 stroke-[2.5]" />
                            <span>Copiado</span>
                          </span>
                        ) : (
                          <Copy className="w-5 h-5 text-blue-500 group-hover:text-blue-700 transition-colors" />
                        )}
                      </button>
                    </div>
                  </div>

                  {isDocente ? (
                    <div className="pt-2 flex justify-center">
                      <ClinicalButton
                        type="button"
                        variant="primary"
                        onClick={() => updateRoomStatus('resolucion')}
                        icon={Play}
                      >
                        Iniciar Fase de Resolución Clínica
                      </ClinicalButton>
                    </div>
                  ) : (
                    <div className="flex justify-center">
                      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 bg-[#f0f4f9] rounded-full text-[11px] text-[#747775]">
                        <span className="w-2 h-2 rounded-full bg-[#0b57d0] animate-pulse" />
                        <span>Esperando que el docente moderador inicie la resolución...</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* FASE 2: RESOLUCIÓN DIAGNÓSTICA ACTIVA (LIENZO DE CO-ESCRITURA EN VIVO) */}
              {activePhase === 'resolucion' && (
                <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <label className="text-xs font-semibold text-[#1f1f1f] flex items-center gap-1.5">
                      <PenTool className="w-3.5 h-3.5 text-[#0b57d0]" />
                      <span>Fase 2: Lienzo de Consenso Diagnóstico (Co-escritura en Vivo)</span>
                    </label>

                    {/* Presencia de Escritura Activa */}
                    {activeTypers.length > 0 && (
                      <span className="text-[11px] text-[#0b57d0] font-medium flex items-center gap-1.5 animate-pulse">
                        <span className="w-2 h-2 rounded-full bg-[#0b57d0]" />
                        <span>Escribiendo ahora: {activeTypers.map(t => t.user_nombre).join(', ')}</span>
                      </span>
                    )}
                  </div>

                  <div className="relative">
                    <textarea
                      rows={8}
                      value={collaborativeText}
                      onChange={(e) => handleCollaborativeTextChange(e.target.value)}
                      placeholder="Redacten colectivamente aquí el análisis clínico del caso, hipótesis nosológica alineada a la GPC del MSP, conducta terapéutica de urgencia y esquemas posológicos..."
                      disabled={Boolean(groupEvalResult)}
                      className="w-full p-4 bg-[#f0f4f9] rounded-[20px] text-sm text-[#1f1f1f] border border-slate-200/80 focus:outline-none focus:border-[#0b57d0] focus:bg-white transition-all resize-none leading-relaxed"
                    />

                    <div className="flex items-center justify-between px-2 pt-1 text-[11px] text-[#747775]">
                      <span>
                        {collaborativeText.trim()
                          ? `${collaborativeText.trim().split(/\s+/).length} palabras • ${collaborativeText.length} caracteres`
                          : 'Lienzo abierto • Escribe para co-redactar y sincronizar con la sala'}
                      </span>
                      {roomDetails.borrador_grupal?.ultimo_editor_nombre && (
                        <span>
                          Última edición: {roomDetails.borrador_grupal.ultimo_editor_nombre}
                        </span>
                      )}
                    </div>
                  </div>

                  {!groupEvalResult && (
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                      <p className="text-[11px] text-[#747775]">
                        Los aportes se sincronizan por WebSockets y se reflejan al instante en todos los dispositivos conectados.
                      </p>
                      <ClinicalButton
                        type="button"
                        variant="primary"
                        loading={submittingGroup}
                        onClick={submitGroupVerdict}
                        disabled={!collaborativeText.trim()}
                        icon={Send}
                      >
                        Emitir Dictamen de Consenso Grupal
                      </ClinicalButton>
                    </div>
                  )}

                  {/* Dictamen Grupal Evaluado por el Motor RAG */}
                  {groupEvalResult && (
                    <div className="p-5 bg-emerald-50/70 rounded-[24px] border border-emerald-200/80 space-y-4 animate-fadeIn mt-4">
                      <div className="flex items-center justify-between border-b border-emerald-200/60 pb-3">
                        <div className="flex items-center gap-2">
                          <ShieldCheck className="w-5 h-5 text-emerald-700" />
                          <div>
                            <span className="text-xs font-semibold text-emerald-950 block">
                              Dictamen de Consenso Grupal Evaluado por IA
                            </span>
                            <span className="text-[11px] text-emerald-800">
                              {roomDetails.dictamen_grupal_por ? `Emitido por ${roomDetails.dictamen_grupal_por}` : 'Dictamen oficial de la sala'}
                            </span>
                          </div>
                        </div>

                        <div className="text-right">
                          <span className="text-[11px] text-emerald-800 block font-medium">Calificación Colectiva</span>
                          <span className="text-xl font-heading font-medium text-emerald-950">
                            {groupEvalResult.score} <span className="text-xs text-emerald-700 font-sans">/ 10</span>
                          </span>
                        </div>
                      </div>

                      {groupEvalResult.aciertos && groupEvalResult.aciertos.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-xs font-semibold text-emerald-900 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            Aciertos del Razonamiento Colectivo:
                          </span>
                          <ul className="list-disc list-inside text-xs text-emerald-950 pl-2 space-y-1 bg-white/80 p-3 rounded-[16px] border border-emerald-200/50">
                            {groupEvalResult.aciertos.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {groupEvalResult.omisiones && groupEvalResult.omisiones.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-xs font-semibold text-amber-900 flex items-center gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                            Omisiones Frente a la GPC del MSP:
                          </span>
                          <ul className="list-disc list-inside text-xs text-amber-950 pl-2 space-y-1 bg-white/80 p-3 rounded-[16px] border border-amber-200/50">
                            {groupEvalResult.omisiones.map((o, i) => (
                              <li key={i}>{o}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {groupEvalResult.cita_normativa && (
                        <div className="p-3 bg-white rounded-[16px] border border-emerald-200/70 flex items-center gap-2 text-xs text-slate-800">
                          <BookOpen className="w-4 h-4 text-[#0b57d0] shrink-0" />
                          <div>
                            <span className="font-semibold">{groupEvalResult.cita_normativa.guia}</span>
                            {groupEvalResult.cita_normativa.seccion && <span> — {groupEvalResult.cita_normativa.seccion}</span>}
                            {groupEvalResult.cita_normativa.pagina && <span> (Pág. {groupEvalResult.cita_normativa.pagina})</span>}
                          </div>
                        </div>
                      )}

                      {groupEvalResult.retroalimentacion_general && (
                        <p className="text-xs text-emerald-950 leading-relaxed bg-white/80 p-3 rounded-[16px] border border-emerald-200/50">
                          {groupEvalResult.retroalimentacion_general}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* FASE 3 Y 4: DISCUSIÓN DEBRIEFING O CIERRE DE LA SALA */}
              {(activePhase === 'discusion' || activePhase === 'finalizado') && (
                <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-[#0b57d0]">
                      {activePhase === 'discusion' ? (
                        <>
                          <Activity className="w-3.5 h-3.5 text-[#0b57d0]" />
                          <span>Fase 3: Consenso y Debriefing Socrático</span>
                        </>
                      ) : (
                        <>
                          <Award className="w-3.5 h-3.5 text-emerald-700" />
                          <span className="text-emerald-800">Fase 4: Ateneo Clínico Concluido</span>
                        </>
                      )}
                    </div>
                    <ClinicalBadge variant={activePhase === 'discusion' ? 'primary' : 'success'} size="sm">
                      {activePhase === 'discusion' ? 'Entregas Selladas • Debate Activo' : 'Sesión Archivada'}
                    </ClinicalBadge>
                  </div>

                  {/* Dictamen Grupal Evaluado por el Motor RAG */}
                  {groupEvalResult ? (
                    <div className="p-5 bg-emerald-50/70 rounded-[24px] border border-emerald-200/80 space-y-4 animate-fadeIn">
                      <div className="flex items-center justify-between border-b border-emerald-200/60 pb-3">
                        <div className="flex items-center gap-2">
                          <ShieldCheck className="w-5 h-5 text-emerald-700" />
                          <div>
                            <span className="text-xs font-semibold text-emerald-950 block">
                              Dictamen Oficial Evaluado por IA
                            </span>
                            <span className="text-[11px] text-emerald-800">
                              {roomDetails.dictamen_grupal_por ? `Emitido por ${roomDetails.dictamen_grupal_por}` : 'Dictamen consensuado de la cohorte'}
                            </span>
                          </div>
                        </div>

                        <div className="text-right">
                          <span className="text-[11px] text-emerald-800 block font-medium">Calificación Colectiva</span>
                          <span className="text-xl font-heading font-medium text-emerald-950">
                            {groupEvalResult.score} <span className="text-xs text-emerald-700 font-sans">/ 10</span>
                          </span>
                        </div>
                      </div>

                      {groupEvalResult.aciertos && groupEvalResult.aciertos.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-xs font-semibold text-emerald-900 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            Aciertos del Razonamiento Colectivo:
                          </span>
                          <ul className="list-disc list-inside text-xs text-emerald-950 pl-2 space-y-1 bg-white/80 p-3 rounded-[16px] border border-emerald-200/50">
                            {groupEvalResult.aciertos.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {groupEvalResult.omisiones && groupEvalResult.omisiones.length > 0 && (
                        <div className="space-y-1.5">
                          <span className="text-xs font-semibold text-amber-900 flex items-center gap-1.5">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                            Omisiones Frente a la GPC del MSP:
                          </span>
                          <ul className="list-disc list-inside text-xs text-amber-950 pl-2 space-y-1 bg-white/80 p-3 rounded-[16px] border border-amber-200/50">
                            {groupEvalResult.omisiones.map((o, i) => (
                              <li key={i}>{o}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {groupEvalResult.cita_normativa && (
                        <div className="p-3 bg-white rounded-[16px] border border-emerald-200/70 flex items-center gap-2 text-xs text-slate-800">
                          <BookOpen className="w-4 h-4 text-[#0b57d0] shrink-0" />
                          <div>
                            <span className="font-semibold">{groupEvalResult.cita_normativa.guia}</span>
                            {groupEvalResult.cita_normativa.seccion && <span> — {groupEvalResult.cita_normativa.seccion}</span>}
                            {groupEvalResult.cita_normativa.pagina && <span> (Pág. {groupEvalResult.cita_normativa.pagina})</span>}
                          </div>
                        </div>
                      )}

                      {groupEvalResult.retroalimentacion_general && (
                        <p className="text-xs text-emerald-950 leading-relaxed bg-white/80 p-3 rounded-[16px] border border-emerald-200/50">
                          {groupEvalResult.retroalimentacion_general}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs text-[#747775] text-center space-y-2">
                      <p className="font-medium text-slate-800">
                        La fase de resolución activa ha concluido.
                      </p>
                      <p>
                        {collaborativeText.trim()
                          ? 'El texto del lienzo colaborativo ha quedado sellado en modo lectura para el debriefing colectivo con el tutor.'
                          : 'No se emitió dictamen grupal durante la fase anterior. Utilicen el canal de audio para el debriefing socrático del caso clínico.'}
                      </p>
                    </div>
                  )}

                  {/* Texto redactado en modo solo lectura */}
                  {collaborativeText.trim() && (
                    <div className="space-y-1.5 pt-1">
                      <span className="text-xs font-semibold text-slate-700 block">
                        Dictamen Clínico Consensuado (Solo Lectura):
                      </span>
                      <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs sm:text-sm text-[#1f1f1f] leading-relaxed border border-slate-200/80">
                        <ClinicalMarkdownRenderer content={collaborativeText} />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* MODALIDAD 2: MODO INDIVIDUAL (ALUMNO Y DOCENTE EN FASES 1, 2 Y 3) */}
          {modoResolucion === 'individual' && activePhase !== 'finalizado' && (
            <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="text-base font-medium text-[#1f1f1f] font-heading flex items-center gap-2">
                  <User className="w-4 h-4 text-[#0b57d0]" />
                  {isDocente ? 'Monitoreo de Resoluciones Individuales' : 'Tu Aporte Diagnóstico Individual'}
                </h3>
                <ClinicalBadge
                  variant={
                    activePhase === 'espera' ? 'default'
                    : activePhase === 'resolucion' ? 'primary'
                    : 'success'
                  }
                  size="sm"
                >
                  {activePhase === 'espera' ? 'Fase 1: En Espera'
                    : activePhase === 'resolucion' ? 'Fase 2: Redacción'
                    : 'Fase 3: Discusión'}
                </ClinicalBadge>
              </div>

              {activePhase === 'espera' && (
                <div className="p-6 bg-[#f0f4f9] rounded-[20px] text-center text-xs text-slate-600 space-y-2">
                  <p className="font-semibold text-slate-800 text-sm">Fase 1: Espera y Preparación</p>
                  <p>
                    {isDocente
                      ? 'Los estudiantes están en la sala de espera revisando la viñeta clínica. Cuando haya quórum, pulsa "Iniciar Fase de Resolución".'
                      : 'Lee la viñeta clínica y paraclínicos en la columna izquierda. El formulario de respuesta se desbloqueará cuando el docente moderador inicie la Fase 2 de Resolución.'}
                  </p>
                </div>
              )}

              {activePhase === 'resolucion' && !isDocente && !submittedEval && (
                <form onSubmit={submitAnswer} className="space-y-4 pt-1">
                  <div className="space-y-1.5">
                    <textarea
                      rows={8}
                      value={studentAnswer}
                      onChange={(e) => setStudentAnswer(e.target.value)}
                      placeholder="Escribe tu hipótesis nosológica, esquemas farmacológicos normados e intervenciones de urgencia..."
                      required
                      className="w-full p-4 bg-[#f0f4f9] rounded-[20px] text-sm text-[#1f1f1f] border border-slate-200/80 focus:outline-none focus:border-[#0b57d0] focus:bg-white transition-all resize-none leading-relaxed"
                    />
                  </div>

                  <div className="flex justify-end">
                    <ClinicalButton
                      type="submit"
                      variant="primary"
                      loading={submitting}
                      icon={Send}
                    >
                      Enviar Dictamen a la Sala
                    </ClinicalButton>
                  </div>
                </form>
              )}

              {activePhase === 'resolucion' && !isDocente && submittedEval && (
                <div className="p-5 bg-emerald-50 rounded-[20px] border border-emerald-200/80 space-y-2">
                  <span className="text-xs font-semibold text-emerald-900 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Dictamen Registrado en la Sala
                  </span>
                  <p className="text-xs text-emerald-950 leading-relaxed">
                    Tu dictamen individual se ha registrado con una calificación de <strong>{submittedEval.score} / 10</strong>. En la siguiente fase podrás debatir con el docente y tu cohorte.
                  </p>
                </div>
              )}

              {activePhase === 'resolucion' && isDocente && (
                <div className="p-5 bg-[#f0f4f9] rounded-[20px] border border-slate-200/80 space-y-2 text-xs text-[#444746]">
                  <span className="font-semibold text-slate-800 block text-sm">
                    Recepción de Dictámenes en Vivo
                  </span>
                  <p className="leading-relaxed">
                    Los estudiantes están redactando sus diagnósticos. Actualmente hay <strong className="text-slate-800">{respondieronCount} de {totalParticipantes} dictámenes emitidos</strong> ({participationPct}%).
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Puedes consultar cada dictamen individual en el panel inferior.
                  </p>
                </div>
              )}

              {activePhase === 'discusion' && (
                <div className="space-y-4">
                  {!isDocente && submittedEval && (
                    <div className="p-5 bg-emerald-50 rounded-[20px] border border-emerald-200/80 space-y-3">
                      <div className="flex items-center justify-between border-b border-emerald-200/60 pb-2">
                        <span className="text-xs font-semibold text-emerald-950 flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          Tu Evaluación Formativa Individual
                        </span>
                        <span className="font-heading font-medium text-emerald-950 text-lg">
                          {submittedEval.score} <span className="text-xs text-emerald-700 font-sans">/ 10</span>
                        </span>
                      </div>

                      {submittedEval.aciertos && submittedEval.aciertos.length > 0 && (
                        <div className="space-y-1">
                          <span className="text-xs font-semibold text-emerald-900">Aciertos:</span>
                          <ul className="list-disc list-inside text-xs text-emerald-950 pl-1 space-y-0.5">
                            {submittedEval.aciertos.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {submittedEval.omisiones && submittedEval.omisiones.length > 0 && (
                        <div className="space-y-1 pt-1">
                          <span className="text-xs font-semibold text-amber-900">Omisiones frente a GPC:</span>
                          <ul className="list-disc list-inside text-xs text-amber-950 pl-1 space-y-0.5">
                            {submittedEval.omisiones.map((o, i) => (
                              <li key={i}>{o}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {!isDocente && !submittedEval && (
                    <div className="p-5 bg-[#f0f4f9] rounded-[20px] text-center text-xs text-[#747775] space-y-1">
                      <p className="font-medium text-slate-800">Fase de Resolución Cerrada</p>
                      <p>No se emitió dictamen individual para esta sesión. Participa activamente en el debate grupal por audio y consulta los dictámenes de tus pares.</p>
                    </div>
                  )}

                  {isDocente && (
                    <div className="p-5 bg-[#f0f4f9] rounded-[20px] border border-slate-200/80 space-y-2 text-xs text-[#444746]">
                      <span className="font-semibold text-slate-800 block text-sm">
                        Debriefing Socrático de la Cohorte
                      </span>
                      <p className="leading-relaxed">
                        Conduce el debate socrático con los estudiantes. Haz clic en cualquier estudiante de la lista inferior para examinar su razonamiento clínico y contrastarlo con las GPC del MSP.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* FASE 4: RESULTADOS FINALES DE LA SESIÓN DE ATENEO (VISIBLES PARA DOCENTE Y ALUMNOS) */}
          {activePhase === 'finalizado' && (
            <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-5 animate-fadeIn">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-[#0b57d0]" />
                  <div>
                    <h3 className="text-base font-medium text-[#1f1f1f] font-heading">
                      Resultados Finales del Ateneo Clínico
                    </h3>
                    <p className="text-xs text-[#747775]">
                      Sesión concluida • Registro consolidado de calificaciones y dictámenes
                    </p>
                  </div>
                </div>
                <ClinicalBadge variant="success" size="sm">
                  Sesión Finalizada
                </ClinicalBadge>
              </div>

              {/* Resumen Métrico de Cierre */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                <div className="p-3.5 bg-[#f0f4f9] rounded-[20px] text-center">
                  <span className="text-[11px] text-[#747775] block font-medium">Promedio Sala</span>
                  <p className="text-xl font-normal text-[#1f1f1f] font-heading mt-0.5">
                    {scorePromedio} <span className="text-xs text-slate-500 font-sans">/ 10</span>
                  </p>
                </div>

                <div className="p-3.5 bg-[#f0f4f9] rounded-[20px] text-center">
                  <span className="text-[11px] text-[#747775] block font-medium">Entregas</span>
                  <p className="text-xl font-normal text-[#1f1f1f] font-heading mt-0.5">
                    {respondieronCount} <span className="text-xs text-slate-500 font-sans">de {totalParticipantes}</span>
                  </p>
                </div>

                <div className="p-3.5 bg-[#f0f4f9] rounded-[20px] text-center">
                  <span className="text-[11px] text-[#747775] block font-medium">Quórum</span>
                  <p className="text-xl font-normal text-[#1f1f1f] font-heading mt-0.5">
                    {participationPct}%
                  </p>
                </div>

                <div className="p-3.5 bg-[#f0f4f9] rounded-[20px] text-center">
                  <span className="text-[11px] text-[#747775] block font-medium">Modalidad</span>
                  <p className="text-xs font-semibold text-[#0b57d0] mt-1.5 capitalize">
                    {modoResolucion === 'grupal' ? 'Ateneo Grupal' : 'Individual'}
                  </p>
                </div>
              </div>

              {/* MODO GRUPAL: Dictamen Colectivo Evaluado */}
              {modoResolucion === 'grupal' && (
                <div className="space-y-4 pt-2">
                  {groupEvalResult ? (
                    <div className="p-5 bg-emerald-50/70 rounded-[22px] border border-emerald-200/80 space-y-3">
                      <div className="flex items-center justify-between border-b border-emerald-200/60 pb-2">
                        <span className="text-xs font-semibold text-emerald-950 flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          Dictamen Consensuado por la Cohorte
                        </span>
                        <span className="font-heading font-medium text-emerald-950 text-xl">
                          {groupEvalResult.score} <span className="text-xs text-emerald-700 font-sans">/ 10</span>
                        </span>
                      </div>

                      {groupEvalResult.aciertos && groupEvalResult.aciertos.length > 0 && (
                        <div className="space-y-1">
                          <span className="text-xs font-semibold text-emerald-900">Aciertos Colectivos:</span>
                          <ul className="list-disc list-inside text-xs text-emerald-950 pl-1 space-y-0.5">
                            {groupEvalResult.aciertos.map((a, i) => (
                              <li key={i}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {groupEvalResult.omisiones && groupEvalResult.omisiones.length > 0 && (
                        <div className="space-y-1 pt-1">
                          <span className="text-xs font-semibold text-amber-900">Omisiones frente a GPC MSP Ecuador:</span>
                          <ul className="list-disc list-inside text-xs text-amber-950 pl-1 space-y-0.5">
                            {groupEvalResult.omisiones.map((o, i) => (
                              <li key={i}>{o}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {groupEvalResult.cita_normativa && (
                        <div className="p-3 bg-white rounded-[16px] border border-emerald-200/70 flex items-center gap-2 text-xs text-slate-800">
                          <BookOpen className="w-4 h-4 text-[#0b57d0] shrink-0" />
                          <div>
                            <span className="font-semibold">{groupEvalResult.cita_normativa.guia}</span>
                            {groupEvalResult.cita_normativa.seccion && <span> — {groupEvalResult.cita_normativa.seccion}</span>}
                            {groupEvalResult.cita_normativa.pagina && <span> (Pág. {groupEvalResult.cita_normativa.pagina})</span>}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs text-[#747775] text-center">
                      No se registró dictamen de consenso colectivo en esta sesión.
                    </div>
                  )}

                  {collaborativeText.trim() && (
                    <div className="space-y-1.5">
                      <span className="text-xs font-semibold text-slate-700 block">Texto del Dictamen Consensuado:</span>
                      <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs sm:text-sm text-[#1f1f1f] leading-relaxed border border-slate-200/80">
                        <ClinicalMarkdownRenderer content={collaborativeText} />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* MODO INDIVIDUAL: Resultados y Dictámenes de Todos los Participantes */}
              {modoResolucion === 'individual' && (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
                      Dictámenes y Calificaciones de la Cohorte
                    </span>
                    <span className="text-[11px] text-slate-500">
                      {respondieronCount} de {totalParticipantes} emitieron dictamen
                    </span>
                  </div>

                  {rankingParticipantes.length === 0 ? (
                    <div className="p-4 bg-[#f0f4f9] rounded-[20px] text-xs text-[#747775] text-center">
                      No hubo participantes registrados en esta sesión.
                    </div>
                  ) : (
                    <div className="space-y-2.5">
                      {rankingParticipantes.map((p, idx) => {
                        const email = p.email || `participant_${idx}`;
                        const isExpanded = expandedParticipantEmail === email;
                        const hasResult = p.respondido && p.resultado_evaluacion;
                        const isMe = currentUser?.email && p.email && currentUser.email.toLowerCase() === p.email.toLowerCase();

                        return (
                          <div
                            key={idx}
                            className={`rounded-[20px] p-3.5 transition-all border ${
                              isMe
                                ? 'bg-blue-50/50 border-blue-200'
                                : 'bg-[#f0f4f9] border-slate-200/70'
                            }`}
                          >
                            <div
                              className={`flex items-center justify-between ${hasResult ? 'cursor-pointer' : ''}`}
                              onClick={() => hasResult && toggleExpandParticipant(email)}
                            >
                              <div className="flex items-center gap-2 truncate pr-2">
                                <span className="w-5 h-5 rounded-full bg-white flex items-center justify-center text-[10px] font-bold text-slate-700 border border-slate-200 shrink-0">
                                  {idx + 1}
                                </span>
                                <div className="truncate">
                                  <span className="font-semibold text-[#1f1f1f] text-xs inline-flex items-center gap-1.5 truncate">
                                    {p.nombre || 'Estudiante'}
                                    {isMe && (
                                      <span className="text-[10px] bg-blue-100 text-[#0b57d0] font-bold px-1.5 py-0.2 rounded-full">
                                        Tú
                                      </span>
                                    )}
                                  </span>
                                  <span className="text-[10px] text-[#747775] block truncate">{p.email || p.rol || 'alumno'}</span>
                                </div>
                              </div>

                              <div className="flex items-center gap-2 shrink-0">
                                {hasResult ? (
                                  <ClinicalBadge
                                    variant={
                                      (p.resultado_evaluacion?.score ?? 0) >= 8
                                        ? 'success'
                                        : (p.resultado_evaluacion?.score ?? 0) >= 6
                                        ? 'warning'
                                        : 'danger'
                                    }
                                    size="sm"
                                  >
                                    {p.resultado_evaluacion?.score} / 10
                                  </ClinicalBadge>
                                ) : (
                                  <ClinicalBadge variant="default" size="sm">
                                    Sin Entrega
                                  </ClinicalBadge>
                                )}

                                {hasResult && (
                                  <button
                                    type="button"
                                    className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
                                    title={isExpanded ? "Ocultar evaluación" : "Ver dictamen y evaluación"}
                                  >
                                    {isExpanded ? (
                                      <ChevronUp className="w-4 h-4" />
                                    ) : (
                                      <ChevronDown className="w-4 h-4" />
                                    )}
                                  </button>
                                )}
                              </div>
                            </div>

                            {/* Detalle del Dictamen y Evaluación RAG Expandible para Todos */}
                            {isExpanded && p.resultado_evaluacion && (
                              <div className="mt-3 pt-3 border-t border-slate-200/80 space-y-2 text-xs animate-fadeIn">
                                {p.respuesta && (
                                  <div className="space-y-1">
                                    <span className="font-semibold text-slate-800 flex items-center gap-1">
                                      <FileText className="w-3.5 h-3.5 text-[#0b57d0]" />
                                      Dictamen Clínico Emitido:
                                    </span>
                                    <div className="p-3 bg-white rounded-[14px] text-slate-800 leading-relaxed border border-slate-200/60">
                                      <ClinicalMarkdownRenderer content={p.respuesta} compact />
                                    </div>
                                  </div>
                                )}

                                {p.resultado_evaluacion.aciertos && p.resultado_evaluacion.aciertos.length > 0 && (
                                  <div className="space-y-0.5">
                                    <span className="font-semibold text-emerald-800">Aciertos Identificados:</span>
                                    <ul className="list-disc list-inside text-emerald-950 pl-1 space-y-0.5">
                                      {p.resultado_evaluacion.aciertos.map((a, i) => (
                                        <li key={i}>{a}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {p.resultado_evaluacion.omisiones && p.resultado_evaluacion.omisiones.length > 0 && (
                                  <div className="space-y-0.5 pt-1">
                                    <span className="font-semibold text-amber-800">Omisiones frente a GPC:</span>
                                    <ul className="list-disc list-inside text-amber-950 pl-1 space-y-0.5">
                                      {p.resultado_evaluacion.omisiones.map((o, i) => (
                                        <li key={i}>{o}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {p.resultado_evaluacion.cita_normativa && (
                                  <div className="mt-2 p-2 bg-white rounded-[12px] border border-blue-100 flex items-center gap-1.5 text-slate-700">
                                    <ShieldCheck className="w-3.5 h-3.5 text-[#0b57d0] shrink-0" />
                                    <span className="truncate">
                                      {p.resultado_evaluacion.cita_normativa.guia} (Pág. {p.resultado_evaluacion.cita_normativa.pagina || '1'})
                                    </span>
                                  </div>
                                )}

                                {p.resultado_evaluacion.retroalimentacion_general && (
                                  <p className="text-[11px] text-slate-600 bg-white/80 p-2.5 rounded-[12px] border border-slate-200/50 leading-relaxed">
                                    {p.resultado_evaluacion.retroalimentacion_general}
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Panel de Participantes (Docente Auditor o Resumen de Integrantes) */}
          <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-medium text-[#1f1f1f] font-heading flex items-center gap-2">
                <Users className="w-4 h-4 text-[#0b57d0]" />
                Participantes ({totalParticipantes})
              </h3>
              <span className="text-xs text-[#747775]">
                {modoResolucion === 'grupal'
                  ? groupEvalResult ? 'Dictamen consensuado' : 'Co-escritura activa'
                  : `${respondieronCount} con dictamen`}
              </span>
            </div>

            <div className="space-y-3 max-h-[560px] overflow-y-auto pr-1">
              {participantesList.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-400">
                  Aún no hay participantes conectados a esta sala.
                </div>
              ) : (
                participantesList.map((p, idx) => {
                  const email = p.email || `participant_${idx}`;
                  const isExpanded = expandedParticipantEmail === email;
                  const canExpand = p.respondido && p.resultado_evaluacion && modoResolucion === 'individual' && (isDocente || isConsensusPhase);

                  return (
                    <div
                      key={idx}
                      className="rounded-[18px] bg-[#f0f4f9] p-3 text-xs transition-all border border-slate-200/60"
                    >
                      <div 
                        className={`flex items-center justify-between ${canExpand ? 'cursor-pointer hover:opacity-90' : ''}`}
                        onClick={() => canExpand && toggleExpandParticipant(email)}
                      >
                        <div className="truncate pr-2">
                          <span className="font-semibold text-[#1f1f1f] block truncate">
                            {p.nombre || 'Estudiante'}
                          </span>
                          <span className="text-[10px] text-[#747775]">{p.rol || 'alumno'}</span>
                        </div>

                        <div className="flex items-center gap-2">
                          {modoResolucion === 'grupal' ? (
                            <ClinicalBadge
                              variant={groupEvalResult ? 'success' : activeTypers.some(t => t.user_id === p.id || t.user_nombre === p.nombre) ? 'primary' : 'default'}
                              size="sm"
                            >
                              {groupEvalResult
                                ? 'Consenso Listo'
                                : activeTypers.some(t => t.user_id === p.id || t.user_nombre === p.nombre)
                                ? 'Redactando...'
                                : 'En Línea'}
                            </ClinicalBadge>
                          ) : (
                            <ClinicalBadge
                              variant={
                                p.respondido
                                  ? (isDocente || isConsensusPhase) && p.resultado_evaluacion?.score !== undefined
                                    ? p.resultado_evaluacion.score >= 8 ? 'success' : p.resultado_evaluacion.score >= 6 ? 'warning' : 'danger'
                                    : 'success'
                                  : 'default'
                              }
                              size="sm"
                            >
                              {p.respondido
                                ? (isDocente || isConsensusPhase) && p.resultado_evaluacion?.score !== undefined
                                  ? `${p.resultado_evaluacion.score}/10`
                                  : 'Dictamen Enviado'
                                : 'Pensando...'}
                            </ClinicalBadge>
                          )}

                          {canExpand && (
                            <button
                              type="button"
                              className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
                              title={isExpanded ? "Ocultar dictamen" : "Ver dictamen"}
                            >
                              {isExpanded ? (
                                <ChevronUp className="w-3.5 h-3.5" />
                              ) : (
                                <ChevronDown className="w-3.5 h-3.5" />
                              )}
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Inspector de Dictamen para Docente y Alumnos (Debriefing Socrático) */}
                      {isExpanded && p.resultado_evaluacion && (
                        <div className="mt-3 pt-3 border-t border-slate-200/80 space-y-2 text-[11px] animate-fadeIn">
                          {p.respuesta && (
                            <div className="space-y-1">
                              <span className="font-semibold text-slate-800 flex items-center gap-1">
                                <FileText className="w-3 h-3 text-[#0b57d0]" />
                                Dictamen Clínico Emitido:
                              </span>
                              <div className="p-2.5 bg-white rounded-[12px] text-slate-800 leading-relaxed border border-slate-200/60">
                                <ClinicalMarkdownRenderer content={p.respuesta} compact />
                              </div>
                            </div>
                          )}

                          {p.resultado_evaluacion.aciertos && p.resultado_evaluacion.aciertos.length > 0 && (
                            <div className="space-y-0.5">
                              <span className="font-semibold text-emerald-800">Aciertos Identificados:</span>
                              <ul className="list-disc list-inside text-emerald-950 pl-1 space-y-0.5">
                                {p.resultado_evaluacion.aciertos.map((a, i) => (
                                  <li key={i}>{a}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {p.resultado_evaluacion.omisiones && p.resultado_evaluacion.omisiones.length > 0 && (
                            <div className="space-y-0.5 pt-1">
                              <span className="font-semibold text-amber-800">Omisiones frente a GPC:</span>
                              <ul className="list-disc list-inside text-amber-950 pl-1 space-y-0.5">
                                {p.resultado_evaluacion.omisiones.map((o, i) => (
                                  <li key={i}>{o}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {p.resultado_evaluacion.cita_normativa && (
                            <div className="mt-2 p-2 bg-white rounded-[12px] border border-blue-100 flex items-center gap-1.5 text-slate-700">
                              <ShieldCheck className="w-3 h-3 text-[#0b57d0] shrink-0" />
                              <span className="truncate">
                                {p.resultado_evaluacion.cita_normativa.guia} (Pág. {p.resultado_evaluacion.cita_normativa.pagina || '1'})
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
