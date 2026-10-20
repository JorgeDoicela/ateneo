import { useEffect, useCallback, FormEvent, useRef } from 'react';
import { useAteneoRoomStore, type ExtendedAteneoRoom } from '../../../core/stores/useAteneoRoomStore';
import { ateneoSocketClient } from '../../../core/realtime/socketClient';
import type { User, EvaluationResult } from '../../../types';

export type { RoomParticipantDetail, ExtendedAteneoRoom, ConnectionStatus, ActiveTyper, SharedDraft } from '../../../core/stores/useAteneoRoomStore';

/**
 * useAteneoRoom — Hook de orquestación reactiva para Salas de Ateneo+ con WebSockets y fallback resiliente.
 * Sustituye el sondeo constante por eventos en tiempo real con latidos de presencia, co-escritura en vivo
 * y consenso grupal instantáneo evaluado por RAG.
 */
export function useAteneoRoom(roomCode: string, currentUser: User | null) {
  const room = useAteneoRoomStore((state) => state.room);
  const loading = useAteneoRoomStore((state) => state.loading);
  const error = useAteneoRoomStore((state) => state.error);
  const studentAnswer = useAteneoRoomStore((state) => state.studentAnswer);
  const submitting = useAteneoRoomStore((state) => state.submitting);
  const submittedEval = useAteneoRoomStore((state) => state.submittedEval);
  const connectionStatus = useAteneoRoomStore((state) => state.connectionStatus);
  const connectedCount = useAteneoRoomStore((state) => state.connectedCount);

  // Estado del Modo Grupal / Co-escritura
  const collaborativeText = useAteneoRoomStore((state) => state.collaborativeText);
  const activeTypers = useAteneoRoomStore((state) => state.activeTypers);
  const groupEvalResult = useAteneoRoomStore((state) => state.groupEvalResult);
  const submittingGroup = useAteneoRoomStore((state) => state.submittingGroup);

  const setStudentAnswer = useAteneoRoomStore((state) => state.setStudentAnswer);
  const fetchRoomState = useAteneoRoomStore((state) => state.fetchRoomState);
  const setRoom = useAteneoRoomStore((state) => state.setRoom);
  const setConnectionStatus = useAteneoRoomStore((state) => state.setConnectionStatus);
  const setConnectedCount = useAteneoRoomStore((state) => state.setConnectedCount);
  const updateStatusInStore = useAteneoRoomStore((state) => state.updateRoomStatus);
  const updateRoomModeInStore = useAteneoRoomStore((state) => state.updateRoomMode);
  const submitInStore = useAteneoRoomStore((state) => state.submitAnswer);
  const submitGroupInStore = useAteneoRoomStore((state) => state.submitGroupAnswer);
  const setCollaborativeText = useAteneoRoomStore((state) => state.setCollaborativeText);
  const setActiveTypers = useAteneoRoomStore((state) => state.setActiveTypers);
  const setGroupEvalResult = useAteneoRoomStore((state) => state.setGroupEvalResult);
  const resetRoom = useAteneoRoomStore((state) => state.resetRoom);

  const userEmail = currentUser?.email;
  const userId = currentUser?.id || 'usr_docente_001';
  const userName = currentUser?.nombre || (currentUser?.rol === 'docente' ? 'Docente Tutor' : 'Estudiante');
  const cleanRoomCode = (roomCode || '').toUpperCase().trim();

  const fallbackPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const typingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const syncDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const clientIdRef = useRef<string>(
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : Math.random().toString(36).substring(2) + Date.now().toString(36)
  );

  useEffect(() => {
    if (!cleanRoomCode) return;

    // 1. Carga inicial inmediata de estado vía REST (registrando al alumno si no es docente)
    fetchRoomState(cleanRoomCode, userEmail, currentUser);

    // 2. Conectar cliente WebSocket bidireccional con código normalizado
    ateneoSocketClient.connect(cleanRoomCode, {
      user_id: currentUser?.id,
      nombre: currentUser?.nombre,
      email: currentUser?.email,
      rol: currentUser?.rol,
    });

    // 3. Suscripción reactiva al estado de la conexión
    const unsubStatus = ateneoSocketClient.onStatusChange((status) => {
      setConnectionStatus(status);
      if (status === 'CONNECTED') {
        if (fallbackPollRef.current) {
          clearInterval(fallbackPollRef.current);
          fallbackPollRef.current = null;
        }
      } else {
        // En cualquier estado no conectado (CONNECTING, RECONNECTING, DISCONNECTED),
        // activar sondeo continuo de alta frecuencia (cada 2.5s) para reflejar cambios docentes sin latencia
        if (!fallbackPollRef.current) {
          fallbackPollRef.current = setInterval(() => {
            fetchRoomState(cleanRoomCode, userEmail);
          }, 2500);
          if (typeof (fallbackPollRef.current as any)?.unref === 'function') {
            (fallbackPollRef.current as any).unref();
          }
        }
      }
    });

    const unsubReconnectFailed = ateneoSocketClient.on('RECONNECT_FAILED', () => {
      if (!fallbackPollRef.current) {
        fallbackPollRef.current = setInterval(() => {
          fetchRoomState(cleanRoomCode, userEmail);
        }, 2500);
        if (typeof (fallbackPollRef.current as any)?.unref === 'function') {
          (fallbackPollRef.current as any).unref();
        }
      }
    });

    // Sincronización instantánea al cambiar de pestaña o retornar foco al navegador
    const handleVisibilityOrFocus = () => {
      if (typeof document !== 'undefined' && document.visibilityState === 'visible') {
        fetchRoomState(cleanRoomCode, userEmail);
      }
    };
    if (typeof window !== 'undefined') {
      window.addEventListener('focus', handleVisibilityOrFocus);
      document.addEventListener('visibilitychange', handleVisibilityOrFocus);
    }

    // 4. Suscripción a eventos en tiempo real
    const unsubRoomUpdate = ateneoSocketClient.on<ExtendedAteneoRoom>('ROOM_STATE_UPDATED', (payload) => {
      if (payload) {
        setRoom(payload, userEmail);
      }
    });

    const unsubPhaseTransition = ateneoSocketClient.on<{ room?: ExtendedAteneoRoom; nuevo_estado?: string }>('PHASE_TRANSITION', (payload) => {
      if (payload?.room) {
        setRoom(payload.room, userEmail);
      } else {
        fetchRoomState(cleanRoomCode, userEmail);
      }
    });

    const unsubAnswerSubmitted = ateneoSocketClient.on<{ room: ExtendedAteneoRoom }>('ANSWER_SUBMITTED', (payload) => {
      if (payload?.room) {
        setRoom(payload.room, userEmail);
      }
    });

    const unsubParticipantJoined = ateneoSocketClient.on<{ total_conectados: number; room?: ExtendedAteneoRoom }>('PARTICIPANT_JOINED', (payload) => {
      if (payload?.total_conectados !== undefined) {
        setConnectedCount(payload.total_conectados);
      }
      if (payload?.room) {
        setRoom(payload.room, userEmail);
      }
    });

    const unsubParticipantLeft = ateneoSocketClient.on<{ total_conectados: number }>('PARTICIPANT_LEFT', (payload) => {
      if (payload?.total_conectados !== undefined) {
        setConnectedCount(payload.total_conectados);
      }
    });

    // 5. Eventos de Modo Grupal y Co-escritura Sincrónica
    const unsubCollabSync = ateneoSocketClient.on<{ texto: string; user_id: string; user_nombre: string; client_id?: string }>(
      'COLLAB_TEXT_SYNC',
      (payload) => {
        // Ignorar si el mensaje fue originado por esta misma pestaña cliente
        const isFromThisTab = payload?.client_id && payload.client_id === clientIdRef.current;
        if (payload && !isFromThisTab) {
          setCollaborativeText(payload.texto);
        }
      }
    );

    const unsubCollabTyping = ateneoSocketClient.on<{ user_id: string; user_nombre: string; is_typing: boolean; client_id?: string }>(
      'COLLAB_TYPING_INDICATOR',
      (payload) => {
        const isFromThisTab = payload?.client_id && payload.client_id === clientIdRef.current;
        if (!payload || isFromThisTab) return;

        const currentTypers = useAteneoRoomStore.getState().activeTypers;
        if (payload.is_typing) {
          if (!currentTypers.some((t) => t.user_id === payload.user_id)) {
            setActiveTypers([...currentTypers, { user_id: payload.user_id, user_nombre: payload.user_nombre }]);
          }
        } else {
          setActiveTypers(currentTypers.filter((t) => t.user_id !== payload.user_id));
        }
      }
    );

    const unsubGroupSubmitted = ateneoSocketClient.on<{
      room: ExtendedAteneoRoom;
      evaluacion: EvaluationResult;
      submitted_by: string;
    }>('GROUP_ANSWER_SUBMITTED', (payload) => {
      if (payload?.room) {
        setRoom(payload.room, userEmail);
      }
      if (payload?.evaluacion) {
        setGroupEvalResult(payload.evaluacion);
      }
    });

    const unsubModeChanged = ateneoSocketClient.on<{ modo_resolucion: 'individual' | 'grupal'; room: ExtendedAteneoRoom }>(
      'MODE_CHANGED',
      (payload) => {
        if (payload?.room) {
          setRoom(payload.room, userEmail);
        }
      }
    );

    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('focus', handleVisibilityOrFocus);
        document.removeEventListener('visibilitychange', handleVisibilityOrFocus);
      }
      if (fallbackPollRef.current) {
        clearInterval(fallbackPollRef.current);
        fallbackPollRef.current = null;
      }
      if (typingTimerRef.current) {
        clearTimeout(typingTimerRef.current);
        typingTimerRef.current = null;
      }
      if (syncDebounceRef.current) {
        clearTimeout(syncDebounceRef.current);
        syncDebounceRef.current = null;
      }
      unsubStatus();
      unsubReconnectFailed();
      unsubRoomUpdate();
      unsubPhaseTransition();
      unsubAnswerSubmitted();
      unsubParticipantJoined();
      unsubParticipantLeft();
      unsubCollabSync();
      unsubCollabTyping();
      unsubGroupSubmitted();
      unsubModeChanged();
      ateneoSocketClient.disconnect();
      resetRoom();
    };
  }, [
    cleanRoomCode,
    userEmail,
    userId,
    currentUser?.nombre,
    currentUser?.rol,
    fetchRoomState,
    setRoom,
    setConnectionStatus,
    setConnectedCount,
    setCollaborativeText,
    setActiveTypers,
    setGroupEvalResult,
    resetRoom,
  ]);

  const updateRoomStatus = useCallback(
    async (nuevoEstado: string) => {
      ateneoSocketClient.send('PHASE_TRANSITION_REQUEST', { nuevo_estado: nuevoEstado, user_id: userId });
      await updateStatusInStore(cleanRoomCode, nuevoEstado, userId);
    },
    [cleanRoomCode, userId, updateStatusInStore]
  );

  const changeResolutionMode = useCallback(
    async (modo: 'individual' | 'grupal') => {
      await updateRoomModeInStore(cleanRoomCode, modo, userId);
    },
    [cleanRoomCode, userId, updateRoomModeInStore]
  );

  const submitAnswer = useCallback(
    async (e?: FormEvent) => {
      if (e) e.preventDefault();
      await submitInStore(cleanRoomCode, userEmail || 'alumno@ateneo.edu.ec');
    },
    [cleanRoomCode, userEmail, submitInStore]
  );

  const handleCollaborativeTextChange = useCallback(
    (newText: string) => {
      setCollaborativeText(newText);

      // Notificar que está escribiendo
      ateneoSocketClient.send('COLLAB_TYPING', {
        user_id: userId,
        user_nombre: userName,
        client_id: clientIdRef.current,
        is_typing: true,
      });

      if (typingTimerRef.current) {
        clearTimeout(typingTimerRef.current);
      }
      typingTimerRef.current = setTimeout(() => {
        ateneoSocketClient.send('COLLAB_TYPING', {
          user_id: userId,
          user_nombre: userName,
          client_id: clientIdRef.current,
          is_typing: false,
        });
      }, 1500);

      // Sincronizar texto mediante debounce para no saturar el canal (150ms)
      if (syncDebounceRef.current) {
        clearTimeout(syncDebounceRef.current);
      }
      syncDebounceRef.current = setTimeout(() => {
        ateneoSocketClient.send('COLLAB_TEXT_UPDATE', {
          texto: newText,
          user_id: userId,
          user_nombre: userName,
          client_id: clientIdRef.current,
        });
      }, 150);
    },
    [userId, userName, setCollaborativeText]
  );

  const submitGroupVerdict = useCallback(
    async (e?: FormEvent) => {
      if (e) e.preventDefault();
      await submitGroupInStore(cleanRoomCode, collaborativeText, userName);
    },
    [cleanRoomCode, collaborativeText, userName, submitGroupInStore]
  );

  const castVote = useCallback(
    (opcionId: string) => {
      ateneoSocketClient.send('VOTE_CAST', {
        user_id: userId,
        user_nombre: currentUser?.nombre,
        opcion: opcionId,
      });
    },
    [userId, currentUser]
  );

  return {
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
    modoResolucion: room?.modo_resolucion || 'individual',
    changeResolutionMode,
    collaborativeText,
    handleCollaborativeTextChange,
    activeTypers,
    groupEvalResult: groupEvalResult || room?.resultado_evaluacion_grupal || null,
    submittingGroup,
    submitGroupVerdict,
    // Controles estándar
    updateRoomStatus,
    submitAnswer,
    castVote,
    reloadRoom: () => fetchRoomState(roomCode, userEmail),
  };
}

export default useAteneoRoom;
