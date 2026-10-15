import { create } from 'zustand';
import type { SocraticDebriefState, SocraticDialogTurn } from '../../../types';
import { streamSocraticTurn } from '../../../core/http/eventStreamClient';

interface SocraticDebriefActions {
  openDebrief: (caseId: string, caseTitle: string, omisiones: string[] | string) => void;
  closeDebrief: () => void;
  sendReplica: (replicaText: string) => Promise<void>;
  resetDialog: () => void;
}

export type SocraticDebriefStore = SocraticDebriefState & SocraticDebriefActions;

let activeAbortController: AbortController | null = null;

export const useSocraticDebriefStore = create<SocraticDebriefStore>((set, get) => ({
  isOpen: false,
  caseId: '',
  caseTitle: '',
  omisionActiva: '',
  omisiones: [],
  historial: [],
  currentStreamText: '',
  isStreaming: false,
  error: null,

  openDebrief: (caseId: string, caseTitle: string, omisionesInput: string[] | string) => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }

    const normalizedOmisiones = Array.isArray(omisionesInput)
      ? omisionesInput.filter(Boolean)
      : (omisionesInput ? [omisionesInput] : []);

    const primaryOmision = normalizedOmisiones.length > 0 ? normalizedOmisiones[0] : '';

    set({
      isOpen: true,
      caseId,
      caseTitle,
      omisionActiva: primaryOmision,
      omisiones: normalizedOmisiones,
      historial: [],
      currentStreamText: '',
      isStreaming: false,
      error: null,
    });
  },

  closeDebrief: () => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
    set({ isOpen: false, isStreaming: false, currentStreamText: '' });
  },

  resetDialog: () => {
    if (activeAbortController) {
      activeAbortController.abort();
      activeAbortController = null;
    }
    set({
      historial: [],
      currentStreamText: '',
      isStreaming: false,
      error: null,
    });
  },

  sendReplica: async (replicaText: string) => {
    const { caseId, omisionActiva, omisiones, historial, isStreaming } = get();
    const cleanReplica = replicaText.trim();
    if (!cleanReplica || isStreaming) return;

    if (activeAbortController) {
      activeAbortController.abort();
    }
    activeAbortController = new AbortController();

    const turnEstudiante: SocraticDialogTurn = {
      role: 'estudiante',
      text: cleanReplica,
    };

    set({
      historial: [...historial, turnEstudiante],
      currentStreamText: '',
      isStreaming: true,
      error: null,
    });

    const payload = {
      case_id: caseId,
      omision_clinica: omisionActiva,
      omisiones_clinicas: omisiones.length > 0 ? omisiones : [omisionActiva],
      estudiante_replica: cleanReplica,
      historial: historial.map((h) => ({ role: h.role, text: h.text })),
    };

    await streamSocraticTurn(
      '/api/evaluate/socratic-turn',
      payload,
      {
        onToken: (token: string) => {
          set((state) => ({
            currentStreamText: state.currentStreamText + token,
          }));
        },
        onComplete: (fullText: string, metadata) => {
          const turnTutor: SocraticDialogTurn = {
            role: 'tutor',
            text: fullText,
            cita_normativa: metadata?.cita_normativa,
          };
          set((state) => ({
            historial: [...state.historial, turnTutor],
            currentStreamText: '',
            isStreaming: false,
          }));
          activeAbortController = null;
        },
        onError: (err: Error) => {
          set({
            error: err.message || 'Error durante la sesión socrática.',
            isStreaming: false,
          });
          activeAbortController = null;
        },
      },
      activeAbortController.signal
    );
  },
}));

export default useSocraticDebriefStore;
