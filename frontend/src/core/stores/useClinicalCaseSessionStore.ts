import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { EvaluationResult, PhaseEvaluationResult } from '../../types';

export interface DraftEntry {
  respuesta: string;
  timestamp: number;
}

export interface ClinicalCaseSession {
  caseId: string;
  currentPhase: number;
  totalPhases: number;
  activeDraft: string;
  phaseAnswers: Record<number, string>;
  phaseResults: Record<number, PhaseEvaluationResult>;
  phaseScores: Record<number, number>;
  completedPhases: number[];
  isCompleted: boolean;
  finalResult?: EvaluationResult | null;
  updatedAt: number;
}

export interface CaseProgressSummary {
  status: 'completed' | 'in_progress' | 'not_started';
  score?: number;
  currentPhase?: number;
  totalPhases?: number;
}

export interface ClinicalCaseSessionState {
  sessions: Record<string, ClinicalCaseSession>;
  drafts: Record<string, DraftEntry>;

  getSession: (caseId: string) => ClinicalCaseSession | undefined;
  savePhaseDraft: (caseId: string, phaseNum: number, text: string) => void;
  savePhaseEvaluation: (caseId: string, phaseNum: number, answer: string, result: PhaseEvaluationResult) => void;
  advancePhase: (caseId: string, nextPhase: number) => void;
  completeCaseSession: (caseId: string, finalResult: EvaluationResult) => void;
  resetCaseSession: (caseId: string) => void;

  getCaseProgress: (caseId: string) => CaseProgressSummary;
  getAllProgressMap: () => Record<string, CaseProgressSummary>;

  saveDraft: (caseId: string, respuesta: string) => void;
  getDraft: (caseId: string) => string;
  clearDraft: (caseId: string) => void;
}

const fallbackStorage = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {},
};

export const useClinicalCaseSessionStore = create<ClinicalCaseSessionState>()(
  persist(
    (set, get) => ({
      sessions: {},
      drafts: {},

      getSession: (caseId: string) => {
        if (!caseId) return undefined;
        return get().sessions[caseId];
      },

      savePhaseDraft: (caseId: string, phaseNum: number, text: string) => {
        if (!caseId) return;
        const now = Date.now();
        set((state) => {
          const currentSession = state.sessions[caseId] || {
            caseId,
            currentPhase: phaseNum || 1,
            totalPhases: 3,
            activeDraft: text,
            phaseAnswers: {},
            phaseResults: {},
            phaseScores: {},
            completedPhases: [],
            isCompleted: false,
            updatedAt: now,
          };

          const updatedPhaseAnswers = {
            ...currentSession.phaseAnswers,
            [phaseNum]: text,
          };

          return {
            sessions: {
              ...state.sessions,
              [caseId]: {
                ...currentSession,
                currentPhase: phaseNum || currentSession.currentPhase,
                activeDraft: text,
                phaseAnswers: updatedPhaseAnswers,
                updatedAt: now,
              },
            },
            drafts: {
              ...state.drafts,
              [caseId]: {
                respuesta: text,
                timestamp: now,
              },
            },
          };
        });
      },

      savePhaseEvaluation: (caseId: string, phaseNum: number, answer: string, result: PhaseEvaluationResult) => {
        if (!caseId) return;
        const now = Date.now();
        set((state) => {
          const currentSession = state.sessions[caseId] || {
            caseId,
            currentPhase: phaseNum,
            totalPhases: 3,
            activeDraft: answer,
            phaseAnswers: {},
            phaseResults: {},
            phaseScores: {},
            completedPhases: [],
            isCompleted: false,
            updatedAt: now,
          };

          const completed = currentSession.completedPhases.includes(phaseNum)
            ? currentSession.completedPhases
            : [...currentSession.completedPhases, phaseNum].sort((a, b) => a - b);

          return {
            sessions: {
              ...state.sessions,
              [caseId]: {
                ...currentSession,
                phaseAnswers: {
                  ...currentSession.phaseAnswers,
                  [phaseNum]: answer,
                },
                phaseResults: {
                  ...currentSession.phaseResults,
                  [phaseNum]: result,
                },
                phaseScores: {
                  ...currentSession.phaseScores,
                  [phaseNum]: result.score_fase ?? (result as any).puntaje_fase ?? 0,
                },
                completedPhases: completed,
                updatedAt: now,
              },
            },
          };
        });
      },

      advancePhase: (caseId: string, nextPhase: number) => {
        if (!caseId) return;
        const now = Date.now();
        set((state) => {
          const currentSession = state.sessions[caseId];
          if (!currentSession) return state;

          const nextDraft = currentSession.phaseAnswers[nextPhase] || '';
          return {
            sessions: {
              ...state.sessions,
              [caseId]: {
                ...currentSession,
                currentPhase: nextPhase,
                activeDraft: nextDraft,
                updatedAt: now,
              },
            },
            drafts: {
              ...state.drafts,
              [caseId]: {
                respuesta: nextDraft,
                timestamp: now,
              },
            },
          };
        });
      },

      completeCaseSession: (caseId: string, finalResult: EvaluationResult) => {
        if (!caseId) return;
        const now = Date.now();
        set((state) => {
          const currentSession = state.sessions[caseId] || {
            caseId,
            currentPhase: 3,
            totalPhases: 3,
            activeDraft: '',
            phaseAnswers: {},
            phaseResults: {},
            phaseScores: {},
            completedPhases: [1, 2, 3],
            isCompleted: true,
            updatedAt: now,
          };

          return {
            sessions: {
              ...state.sessions,
              [caseId]: {
                ...currentSession,
                isCompleted: true,
                finalResult,
                activeDraft: '',
                updatedAt: now,
              },
            },
            drafts: {
              ...state.drafts,
              [caseId]: {
                respuesta: '',
                timestamp: now,
              },
            },
          };
        });
      },

      resetCaseSession: (caseId: string) => {
        if (!caseId) return;
        set((state) => {
          const newSessions = { ...state.sessions };
          delete newSessions[caseId];

          const newDrafts = { ...state.drafts };
          delete newDrafts[caseId];

          return {
            sessions: newSessions,
            drafts: newDrafts,
          };
        });
      },

      getCaseProgress: (caseId: string): CaseProgressSummary => {
        if (!caseId) return { status: 'not_started' };
        const s = get().sessions[caseId];
        if (!s) return { status: 'not_started' };

        if (s.isCompleted && s.finalResult) {
          return {
            status: 'completed',
            score: s.finalResult.score ?? (s.finalResult as any).puntaje_global,
            totalPhases: s.totalPhases,
          };
        }

        if (s.completedPhases.length > 0 || (s.activeDraft && s.activeDraft.trim().length > 0)) {
          return {
            status: 'in_progress',
            currentPhase: s.currentPhase,
            totalPhases: s.totalPhases,
          };
        }

        return { status: 'not_started' };
      },

      getAllProgressMap: (): Record<string, CaseProgressSummary> => {
        const result: Record<string, CaseProgressSummary> = {};
        const sessions = get().sessions;
        for (const [id, s] of Object.entries(sessions)) {
          if (s.isCompleted && s.finalResult) {
            result[id] = {
              status: 'completed',
              score: s.finalResult.score ?? (s.finalResult as any).puntaje_global,
              totalPhases: s.totalPhases,
            };
          } else if (s.completedPhases.length > 0 || (s.activeDraft && s.activeDraft.trim().length > 0)) {
            result[id] = {
              status: 'in_progress',
              currentPhase: s.currentPhase,
              totalPhases: s.totalPhases,
            };
          }
        }
        return result;
      },

      saveDraft: (caseId: string, respuesta: string) => {
        if (!caseId) return;
        const currentPhase = get().sessions[caseId]?.currentPhase || 1;
        get().savePhaseDraft(caseId, currentPhase, respuesta);
      },

      getDraft: (caseId: string) => {
        if (!caseId) return '';
        const session = get().sessions[caseId];
        if (session) {
          return session.activeDraft || session.phaseAnswers[session.currentPhase] || '';
        }
        const draft = get().drafts[caseId];
        return draft ? draft.respuesta : '';
      },

      clearDraft: (caseId: string) => {
        if (!caseId) return;
        get().resetCaseSession(caseId);
      },
    }),
    {
      name: 'ateneo_clinical_case_sessions_v1',
      storage: createJSONStorage(() => (typeof window !== 'undefined' ? localStorage : fallbackStorage)),
    }
  )
);

export default useClinicalCaseSessionStore;
