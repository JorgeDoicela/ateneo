import { create } from 'zustand';
import collaborationApi from '../../modules/collaboration/api/collaborationApi';
import type { AteneoRoom, EvaluationResult, User } from '../../types';

export interface RoomParticipantDetail {
  id?: string;
  email?: string;
  nombre?: string;
  rol?: string;
  respuesta?: string;
  respondido?: boolean;
  respondido_en?: string;
  unido_en?: string;
  resultado_evaluacion?: EvaluationResult;
}

export interface RoomClinicalGap {
  brecha: string;
  estudiantes_afectados: number;
  porcentaje: number;
}

export interface RoomConsensus {
  porcentaje_participacion?: number;
  score_promedio?: number;
  diagnostico_mayoritario?: string;
  promedio_sala?: number;
  total_respondidos?: number;
  total_conectados?: number;
  nivel_consenso?: string;
  top_brechas_sala?: RoomClinicalGap[];
}

export type ConnectionStatus = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED' | 'RECONNECTING';

export interface SharedDraft {
  texto: string;
  ultimo_editor_id?: string | null;
  ultimo_editor_nombre?: string | null;
  actualizado_en?: string;
}

export interface ExtendedAteneoRoom extends Omit<AteneoRoom, 'participantes'> {
  participantes?: Record<string, RoomParticipantDetail>;
  estado?: string;
  modo_resolucion?: 'individual' | 'grupal';
  borrador_grupal?: SharedDraft;
  resultado_evaluacion_grupal?: EvaluationResult | null;
  dictamen_grupal_emitido?: boolean;
  dictamen_grupal_emitido_en?: string;
  dictamen_grupal_por?: string;
  analitica_consenso?: RoomConsensus;
}

export interface ActiveTyper {
  user_id: string;
  user_nombre: string;
}

export interface AteneoRoomState {
  room: ExtendedAteneoRoom | null;
  loading: boolean;
  error: string | null;
  studentAnswer: string;
  submitting: boolean;
  submittedEval: EvaluationResult | null;
  connectionStatus: ConnectionStatus;
  connectedCount: number;

  // Modo Grupal / Lienzo Colaborativo
  collaborativeText: string;
  activeTypers: ActiveTyper[];
  groupEvalResult: EvaluationResult | null;
  submittingGroup: boolean;

  setStudentAnswer: (answer: string) => void;
  setSubmittedEval: (evaluation: EvaluationResult | null) => void;
  setConnectionStatus: (status: ConnectionStatus) => void;
  setConnectedCount: (count: number) => void;
  setCollaborativeText: (text: string) => void;
  setActiveTypers: (typers: ActiveTyper[]) => void;
  setGroupEvalResult: (evalResult: EvaluationResult | null) => void;
  setRoom: (room: ExtendedAteneoRoom, userEmail?: string) => void;
  fetchRoomState: (roomCode: string, userEmail?: string, currentUser?: User | null) => Promise<void>;
  updateRoomStatus: (roomCode: string, nuevoEstado: string, userId: string) => Promise<void>;
  updateRoomMode: (roomCode: string, modo: 'individual' | 'grupal', userId: string) => Promise<void>;
  submitAnswer: (roomCode: string, userEmail: string) => Promise<void>;
  submitGroupAnswer: (roomCode: string, respuestaGrupal: string, userNombre: string) => Promise<void>;
  resetRoom: () => void;
}

export const useAteneoRoomStore = create<AteneoRoomState>((set, get) => ({
  room: null,
  loading: true,
  error: null,
  studentAnswer: '',
  submitting: false,
  submittedEval: null,
  connectionStatus: 'DISCONNECTED',
  connectedCount: 0,

  // Modo Grupal
  collaborativeText: '',
  activeTypers: [],
  groupEvalResult: null,
  submittingGroup: false,

  setStudentAnswer: (studentAnswer) => set({ studentAnswer }),
  setSubmittedEval: (submittedEval) => set({ submittedEval }),
  setConnectionStatus: (connectionStatus) => set({ connectionStatus }),
  setConnectedCount: (connectedCount) => set({ connectedCount }),
  setCollaborativeText: (collaborativeText) => set({ collaborativeText }),
  setActiveTypers: (activeTypers) => set({ activeTypers }),
  setGroupEvalResult: (groupEvalResult) => set({ groupEvalResult }),

  setRoom: (data: ExtendedAteneoRoom, userEmail?: string) => {
    set({
      room: data,
      loading: false,
      error: null,
    });

    if (data.resultado_evaluacion_grupal) {
      set({ groupEvalResult: data.resultado_evaluacion_grupal });
    }

    if (data.borrador_grupal?.texto !== undefined && !get().collaborativeText) {
      set({ collaborativeText: data.borrador_grupal.texto });
    }

    if (userEmail) {
      const myEmail = userEmail.toLowerCase();
      const rawParticipants = data.participantes as unknown;
      if (rawParticipants && typeof rawParticipants === 'object' && !Array.isArray(rawParticipants)) {
        const dict = rawParticipants as Record<string, RoomParticipantDetail>;
        const myParticipantData = dict[myEmail];
        if (myParticipantData?.respondido && myParticipantData.resultado_evaluacion) {
          set({ submittedEval: myParticipantData.resultado_evaluacion });
        }
      }
    }
  },

  fetchRoomState: async (roomCode: string, userEmail?: string, currentUser?: User | null) => {
    if (!roomCode) return;
    try {
      let data: AteneoRoom;
      if (currentUser && currentUser.rol !== 'docente') {
        data = await collaborationApi.joinRoom(
          roomCode,
          currentUser.id,
          currentUser.email,
          currentUser.nombre,
          currentUser.rol
        );
      } else {
        data = await collaborationApi.getRoom(roomCode);
      }
      get().setRoom(data as ExtendedAteneoRoom, userEmail);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'La sala no existe o ha finalizado';
      set({ error: msg, loading: false });
    }
  },

  updateRoomStatus: async (roomCode: string, nuevoEstado: string, userId: string) => {
    try {
      await collaborationApi.updateRoomStatus(roomCode, nuevoEstado, userId);
      await get().fetchRoomState(roomCode);
    } catch (err) {
      console.error('Error al actualizar fase de la sala:', err);
    }
  },

  updateRoomMode: async (roomCode: string, modo: 'individual' | 'grupal', userId: string) => {
    try {
      await collaborationApi.updateRoomMode(roomCode, modo, userId);
      await get().fetchRoomState(roomCode);
    } catch (err) {
      console.error('Error al cambiar modo de resolución:', err);
    }
  },

  submitAnswer: async (roomCode: string, userEmail: string) => {
    const { studentAnswer, submitting } = get();
    if (!studentAnswer.trim() || submitting) return;

    set({ submitting: true });
    try {
      const res = (await collaborationApi.submitRoomAnswer(
        roomCode,
        userEmail || 'alumno@ateneo.edu.ec',
        studentAnswer
      )) as { resultado_evaluacion?: EvaluationResult };

      if (res?.resultado_evaluacion) {
        set({ submittedEval: res.resultado_evaluacion });
      }
      await get().fetchRoomState(roomCode, userEmail);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al enviar diagnóstico';
      alert(msg);
    } finally {
      set({ submitting: false });
    }
  },

  submitGroupAnswer: async (roomCode: string, respuestaGrupal: string, userNombre: string) => {
    const { submittingGroup } = get();
    if (!respuestaGrupal.trim() || submittingGroup) return;

    set({ submittingGroup: true });
    try {
      const res = (await collaborationApi.submitGroupAnswer(
        roomCode,
        respuestaGrupal,
        userNombre
      )) as { evaluacion?: EvaluationResult; room?: ExtendedAteneoRoom };

      if (res?.evaluacion) {
        set({ groupEvalResult: res.evaluacion });
      }
      if (res?.room) {
        get().setRoom(res.room);
      } else {
        await get().fetchRoomState(roomCode);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al enviar dictamen grupal';
      alert(msg);
    } finally {
      set({ submittingGroup: false });
    }
  },

  resetRoom: () => {
    set({
      room: null,
      loading: true,
      error: null,
      studentAnswer: '',
      submitting: false,
      submittedEval: null,
      connectionStatus: 'DISCONNECTED',
      connectedCount: 0,
      collaborativeText: '',
      activeTypers: [],
      groupEvalResult: null,
      submittingGroup: false,
    });
  },
}));

export default useAteneoRoomStore;
