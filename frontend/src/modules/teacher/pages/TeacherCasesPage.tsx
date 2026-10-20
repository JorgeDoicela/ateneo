import React, { useEffect, useState, useCallback } from 'react';
import { 
  Plus, 
  ArrowRight, 
  Loader2, 
  Users, 
  Copy, 
  Check, 
  Trash2, 
  Radio, 
  Award,
  Stethoscope,
  RefreshCw,
  User,
  X,
  AlertTriangle
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import casesApi from '../../cases/api/casesApi';
import collaborationApi from '../../collaboration/api/collaborationApi';
import ClinicalButton from '../../../core/ui/ClinicalButton';
import ClinicalBadge from '../../../core/ui/ClinicalBadge';
import type { ExtendedClinicalCase } from '../../cases/hooks/useCases';
import type { ExtendedAteneoRoom, RoomParticipantDetail } from '../../../core/stores/useAteneoRoomStore';
import { resolveGpcMeta } from '../../cases/hooks/useCases';

/**
 * Vista de Casos y Gestión de Salas Clínicas Sincrónicas (Ateneo+)
 * Permite a los docentes moderar ateneos en vivo, supervisar participantes y crear nuevas salas
 * con selección de modalidad (Resolución Individual o Ateneo en Grupo con co-escritura).
 */
export const TeacherCasesPage: React.FC = () => {
  const { user } = useAuth();
  const [cases, setCases] = useState<ExtendedClinicalCase[]>([]);
  const [teacherRooms, setTeacherRooms] = useState<ExtendedAteneoRoom[]>([]);
  const [loadingCases, setLoadingCases] = useState<boolean>(true);
  const [loadingRooms, setLoadingRooms] = useState<boolean>(true);
  const [selectedCaseForModal, setSelectedCaseForModal] = useState<ExtendedClinicalCase | null>(null);
  const [modalResolutionMode, setModalResolutionMode] = useState<'individual' | 'grupal'>('individual');
  const [isCreatingRoom, setIsCreatingRoom] = useState<boolean>(false);
  const [deletingRoomCode, setDeletingRoomCode] = useState<string | null>(null);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  const loadTeacherRooms = useCallback(async () => {
    setLoadingRooms(true);
    try {
      const roomsData = await collaborationApi.getTeacherRooms();
      setTeacherRooms((roomsData as ExtendedAteneoRoom[]) || []);
    } catch (err: unknown) {
      console.warn('Error al cargar salas del docente:', err);
    } finally {
      setLoadingRooms(false);
    }
  }, []);

  useEffect(() => {
    async function loadData() {
      setLoadingCases(true);
      setErrorMsg(null);
      try {
        const data = await casesApi.getCases();
        setCases(data as ExtendedClinicalCase[]);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Error al cargar catálogo de casos';
        setErrorMsg(msg);
      } finally {
        setLoadingCases(false);
      }
    }

    loadData();
    loadTeacherRooms();
  }, [loadTeacherRooms]);

  const handleCopyCode = async (code: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(code);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch {
      // Fallback si clipboard API no está disponible
      setCopiedCode(code);
      setTimeout(() => setCopiedCode(null), 2000);
    }
  };

  const handleOpenCreateModal = (clinicalCase: ExtendedClinicalCase) => {
    setSelectedCaseForModal(clinicalCase);
    setModalResolutionMode('individual');
    setErrorMsg(null);
  };

  const handleConfirmCreateRoom = async () => {
    if (!selectedCaseForModal) return;
    setIsCreatingRoom(true);
    setErrorMsg(null);
    try {
      const room = await collaborationApi.createRoom(
        selectedCaseForModal.id,
        user?.id || 'usr_docente_001',
        user?.nombre ? `${user.nombre} (Docente)` : 'Dr. Carlos Andrade (Docente)',
        modalResolutionMode
      );
      const targetCode = room.room_code || room.codigo || '';
      setSelectedCaseForModal(null);
      navigate(`/ateneo/${targetCode}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al crear sala de Ateneo';
      setErrorMsg(msg);
    } finally {
      setIsCreatingRoom(false);
    }
  };

  const handleDeleteRoom = async (roomCode: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeletingRoomCode(roomCode);
    try {
      await collaborationApi.deleteRoom(roomCode);
      setTeacherRooms(prev => prev.filter(r => (r.room_code || r.codigo) !== roomCode));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al eliminar sala';
      setErrorMsg(msg);
    } finally {
      setDeletingRoomCode(null);
    }
  };

  const renderStatusBadge = (estado?: string) => {
    switch (estado) {
      case 'espera':
        return <ClinicalBadge variant="default" size="sm">En Espera</ClinicalBadge>;
      case 'resolucion':
      case 'resolviendo':
        return <ClinicalBadge variant="primary" size="sm">Resolución Activa</ClinicalBadge>;
      case 'discusion':
      case 'consenso':
        return <ClinicalBadge variant="success" size="sm">Consenso Grupal</ClinicalBadge>;
      case 'finalizado':
      case 'cerrada':
        return <ClinicalBadge variant="default" size="sm">Finalizada</ClinicalBadge>;
      default:
        return <ClinicalBadge variant="default" size="sm">{estado || 'En Espera'}</ClinicalBadge>;
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      
      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-[20px] text-xs text-rose-800">
          {errorMsg}
        </div>
      )}

      {/* Aviso de Simulación e Investigación en Desarrollo Activo */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong className="text-slate-700">Investigación en Desarrollo Activo:</strong> Plataforma pedagógica dentro de un protocolo científico en curso. Por protección legal institucional, el uso es de momento formativo y experimental rumbo a una versión oficial; no apto para decisiones en pacientes reales.
        </span>
      </div>

      {/* SECCIÓN 1: Mis Salas de Ateneo Activas */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-[#0b57d0]" />
            <h2 className="text-base font-semibold text-slate-900 font-heading">
              Salas de Simulación en Vivo
            </h2>
            <span className="text-xs font-medium text-[#747775] bg-white px-2.5 py-0.5 rounded-full border border-slate-200/80">
              {teacherRooms.length}
            </span>
          </div>

          <button
            type="button"
            onClick={loadTeacherRooms}
            disabled={loadingRooms}
            className="text-xs text-[#747775] hover:text-[#0b57d0] flex items-center gap-1.5 transition-colors cursor-pointer"
            title="Actualizar listado de salas"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingRooms ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Actualizar salas</span>
          </button>
        </div>

        {loadingRooms ? (
          <div className="py-8 flex flex-col items-center justify-center gap-2 text-xs text-slate-500 bg-white rounded-[28px] border border-slate-200/80">
            <Loader2 className="w-5 h-5 animate-spin text-[#0b57d0]" />
            <span>Consultando tus salas activas...</span>
          </div>
        ) : teacherRooms.length === 0 ? (
          <div className="bg-white rounded-[28px] p-6 text-center border border-slate-200/80 space-y-2">
            <p className="text-xs text-[#444746]">
              No tienes salas de ateneo en curso. Selecciona un caso clínico a continuación para aperturar una sala sincrónica con tus estudiantes.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {teacherRooms.map((room) => {
              const code = room.room_code || room.codigo || '';
              const rawParticipants = (room.participantes || {}) as Record<string, RoomParticipantDetail>;
              const participantsList = Object.values(rawParticipants);
              const totalCount = participantsList.length;
              const answeredCount = participantsList.filter(p => p.respondido).length;
              const isCopied = copiedCode === code;
              const gpcMeta = resolveGpcMeta(room.guia_asociada || '');
              const consensusScore = room.analitica_consenso?.score_promedio ?? room.analitica_consenso?.promedio_sala;

              return (
                <div
                  key={code}
                  className="bg-white rounded-[28px] p-6 shadow-xs border border-slate-200/80 hover:border-blue-300 transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    {/* Fila superior: Código de sala y estado */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-[#0b57d0]">
                          {code}
                        </span>
                        <button
                          type="button"
                          onClick={(e) => handleCopyCode(code, e)}
                          className="p-1 text-slate-400 hover:text-[#0b57d0] transition-colors"
                          title="Copiar código de sala"
                        >
                          {isCopied ? (
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                        {isCopied && (
                          <span className="text-[10px] text-emerald-700 font-medium animate-fadeIn">
                            Copiado
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full border font-medium ${
                          room.modo_resolucion === 'grupal'
                            ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                            : 'bg-slate-50 border-slate-200 text-slate-700'
                        }`}>
                          {room.modo_resolucion === 'grupal' ? 'Ateneo en Grupo' : 'Resolución Individual'}
                        </span>
                        {renderStatusBadge(room.estado)}
                      </div>
                    </div>

                    {/* Título del caso moderado */}
                    <div>
                      <span className={`text-[11px] font-semibold block ${gpcMeta.isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                        {gpcMeta.label}
                      </span>
                      <h3 className="text-sm font-medium text-[#1f1f1f] font-heading mt-0.5 line-clamp-2">
                        {room.case_title || 'Caso Clínico de Ateneo'}
                      </h3>
                    </div>

                    {/* Métricas de quórum y dictámenes */}
                    <div className="flex items-center gap-4 text-xs text-[#747775] pt-1">
                      <span className="flex items-center gap-1.5">
                        <Users className="w-3.5 h-3.5 text-slate-400" />
                        <span>{totalCount} conectados</span>
                      </span>

                      <span className="flex items-center gap-1.5">
                        <Award className="w-3.5 h-3.5 text-slate-400" />
                        <span>{answeredCount} con dictamen</span>
                      </span>
                    </div>

                    {consensusScore !== undefined && consensusScore > 0 && (
                      <div className="text-[11px] text-[#444746] bg-[#f0f4f9] px-3 py-1.5 rounded-[14px]">
                        <span>Promedio grupal: </span>
                        <strong className="text-slate-900">{consensusScore} / 10</strong>
                      </div>
                    )}
                  </div>

                  {/* Fila de Acciones */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                    <button
                      type="button"
                      onClick={(e) => handleDeleteRoom(code, e)}
                      disabled={deletingRoomCode === code}
                      className="text-xs text-rose-600 hover:text-rose-700 flex items-center gap-1 transition-colors p-1"
                      title="Eliminar sala"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Cerrar</span>
                    </button>

                    <ClinicalButton
                      variant="primary"
                      size="sm"
                      onClick={() => navigate(`/ateneo/${code}`)}
                      icon={ArrowRight}
                    >
                      Entrar a Sala
                    </ClinicalButton>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* SECCIÓN 2: Catálogo de Casos para Nueva Sala */}
      <section className="space-y-4 pt-4 border-t border-slate-200/80">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-[#0b57d0]" />
              <h2 className="text-base font-semibold text-slate-900 font-heading">
                Catálogo de Casos para Nueva Sala de Ateneo
              </h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Selecciona un caso clínico para moderar una sesión en vivo o inspeccionar sus fases diagnósticas.
            </p>
          </div>
          <span className="text-xs font-medium text-[#747775] bg-white px-3 py-1 rounded-full border border-slate-200/80">
            {cases.length} casos disponibles
          </span>
        </div>

        {loadingCases ? (
          <div className="py-12 flex flex-col items-center justify-center gap-2 text-xs text-slate-500">
            <Loader2 className="w-6 h-6 animate-spin text-[#0b57d0]" />
            <span>Cargando catálogo de casos clínicos...</span>
          </div>
        ) : cases.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-400 bg-white rounded-[28px] border border-slate-200/80">
            No hay casos clínicos disponibles en la cohorte.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cases.map((c) => (
              <div
                key={c.id}
                className="bg-white rounded-[28px] p-6 shadow-xs border border-slate-200/80 hover:border-slate-300 transition-all flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-semibold ${resolveGpcMeta(c.guia_asociada || c.gpc_referencia).isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                      {resolveGpcMeta(c.guia_asociada || c.gpc_referencia).label}
                    </span>
                    {c.fases && (
                      <span className="text-[11px] text-[#747775] font-medium">{c.fases.length} Fases</span>
                    )}
                  </div>
                  <h3 className="text-base font-medium text-[#1f1f1f] font-heading line-clamp-2">
                    {c.titulo}
                  </h3>
                  <p className="text-xs text-[#444746] line-clamp-3 leading-relaxed">
                    {c.enunciado || c.caso_preambulo}
                  </p>
                </div>

                <div className="pt-5 border-t border-slate-100 flex items-center justify-between mt-4">
                  <Link
                    to={`/cases/${c.id}`}
                    className="text-xs font-medium text-[#444746] hover:text-[#0b57d0] flex items-center gap-1 transition-colors"
                  >
                    <span>Inspeccionar</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>

                  <ClinicalButton
                    variant="primary"
                    size="sm"
                    onClick={() => handleOpenCreateModal(c)}
                    icon={Plus}
                  >
                    Crear Sala Ateneo
                  </ClinicalButton>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Modal de Configuración y Apertura de Sala Sincrónica */}
      {selectedCaseForModal && (
        <div
          className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-fadeIn"
          onClick={() => !isCreatingRoom && setSelectedCaseForModal(null)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-white rounded-[28px] max-w-lg w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-slate-200/80 animate-scaleUp relative"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header del Diálogo */}
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-semibold text-[#0b57d0] block">
                  Configuración de Simulación Sincrónica
                </span>
                <h3 className="text-lg font-medium text-[#1f1f1f] font-heading mt-0.5">
                  Aperturar Sala de Ateneo
                </h3>
              </div>
              <button
                type="button"
                disabled={isCreatingRoom}
                onClick={() => setSelectedCaseForModal(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 transition-colors"
                title="Cerrar"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Caso Clínico Seleccionado */}
            <div className="p-3.5 bg-[#f0f4f9] rounded-[20px] text-xs text-slate-800 space-y-1">
              <span className="font-semibold text-[#0b57d0] block">Caso Seleccionado:</span>
              <p className="font-medium text-[#1f1f1f]">{selectedCaseForModal.titulo}</p>
            </div>

            {/* Selector de Modo de Resolución */}
            <div className="space-y-3">
              <label className="text-xs font-semibold text-[#1f1f1f] block">
                Selecciona la Modalidad Pedagógica:
              </label>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Opción 1: Modo Individual */}
                <div
                  onClick={() => setModalResolutionMode('individual')}
                  className={`p-4 rounded-[20px] border cursor-pointer transition-all flex flex-col justify-between space-y-2 ${
                    modalResolutionMode === 'individual'
                      ? 'border-[#0b57d0] bg-blue-50/40 shadow-xs ring-1 ring-[#0b57d0]/20'
                      : 'border-slate-200/80 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <User className={`w-4 h-4 ${modalResolutionMode === 'individual' ? 'text-[#0b57d0]' : 'text-slate-400'}`} />
                    <span className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
                      modalResolutionMode === 'individual' ? 'border-[#0b57d0] bg-[#0b57d0] text-white' : 'border-slate-300'
                    }`}>
                      {modalResolutionMode === 'individual' ? '✓' : ''}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-[#1f1f1f] block">
                      Resolución Individual
                    </span>
                    <p className="text-[11px] text-[#747775] leading-relaxed mt-1">
                      Cada alumno redacta y envía su dictamen clínico independiente. Permite auditar hipótesis y brechas individuales.
                    </p>
                  </div>
                </div>

                {/* Opción 2: Modo Ateneo en Grupo */}
                <div
                  onClick={() => setModalResolutionMode('grupal')}
                  className={`p-4 rounded-[20px] border cursor-pointer transition-all flex flex-col justify-between space-y-2 ${
                    modalResolutionMode === 'grupal'
                      ? 'border-[#0b57d0] bg-blue-50/40 shadow-xs ring-1 ring-[#0b57d0]/20'
                      : 'border-slate-200/80 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <Users className={`w-4 h-4 ${modalResolutionMode === 'grupal' ? 'text-[#0b57d0]' : 'text-slate-400'}`} />
                    <span className={`w-4 h-4 rounded-full border flex items-center justify-center text-[10px] ${
                      modalResolutionMode === 'grupal' ? 'border-[#0b57d0] bg-[#0b57d0] text-white' : 'border-slate-300'
                    }`}>
                      {modalResolutionMode === 'grupal' ? '✓' : ''}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-[#1f1f1f] block">
                      Ateneo en Grupo
                    </span>
                    <p className="text-[11px] text-[#747775] leading-relaxed mt-1">
                      Co-escritura en vivo con WebSockets. Todos colaboran sobre un lienzo compartido y emiten un dictamen consensuado.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Botones de Acción */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
              <button
                type="button"
                disabled={isCreatingRoom}
                onClick={() => setSelectedCaseForModal(null)}
                className="px-4 py-2 text-xs font-medium text-[#444746] hover:text-slate-900 transition-colors"
              >
                Cancelar
              </button>
              <ClinicalButton
                variant="primary"
                loading={isCreatingRoom}
                onClick={handleConfirmCreateRoom}
                icon={Radio}
              >
                Crear y Abrir Sala
              </ClinicalButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherCasesPage;
