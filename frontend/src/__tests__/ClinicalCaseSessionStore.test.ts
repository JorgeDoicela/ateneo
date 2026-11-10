import { describe, it, expect, beforeEach } from 'vitest';
import { useClinicalCaseSessionStore } from '../core/stores/useClinicalCaseSessionStore';
import type { PhaseEvaluationResult, EvaluationResult } from '../types';

describe('useClinicalCaseSessionStore - Persistencia de Progreso y Sesión Clínica', () => {
  beforeEach(() => {
    // Limpiar estado entre pruebas
    useClinicalCaseSessionStore.setState({
      sessions: {},
      drafts: {},
    });
    localStorage.clear();
  });

  it('guarda y recupera borradores por fase correctamente', () => {
    const caseId = 'caso_hta_crisis';
    useClinicalCaseSessionStore.getState().savePhaseDraft(caseId, 1, 'Sospecha de emergencia hipertensiva con daño de órgano diana.');

    const session = useClinicalCaseSessionStore.getState().getSession(caseId);
    expect(session).toBeDefined();
    expect(session?.currentPhase).toBe(1);
    expect(session?.phaseAnswers[1]).toBe('Sospecha de emergencia hipertensiva con daño de órgano diana.');
    expect(session?.activeDraft).toBe('Sospecha de emergencia hipertensiva con daño de órgano diana.');

    // Verificar progreso
    const progress = useClinicalCaseSessionStore.getState().getCaseProgress(caseId);
    expect(progress.status).toBe('in_progress');
    expect(progress.currentPhase).toBe(1);
  });

  it('registra la evaluación de una fase y actualiza fases completadas sin perder respuestas anteriores', () => {
    const caseId = 'caso_neumonia_severa';
    const mockPhaseResult: PhaseEvaluationResult = {
      fase_numero: 1,
      score_fase: 8.5,
      aciertos: ['Identificación de taquipnea'],
      omisiones: [],
      retroalimentacion_fase: 'Excelente enfoque sindrómico.',
    };

    useClinicalCaseSessionStore.getState().savePhaseDraft(caseId, 1, 'Neumonía adquirida en la comunidad grave.');
    useClinicalCaseSessionStore.getState().savePhaseEvaluation(caseId, 1, 'Neumonía adquirida en la comunidad grave.', mockPhaseResult);

    const session = useClinicalCaseSessionStore.getState().getSession(caseId);
    expect(session?.completedPhases).toContain(1);
    expect(session?.phaseScores[1]).toBe(8.5);
    expect(session?.phaseResults[1]).toEqual(mockPhaseResult);

    // Avanzar a fase 2
    useClinicalCaseSessionStore.getState().advancePhase(caseId, 2);
    const sessionFase2 = useClinicalCaseSessionStore.getState().getSession(caseId);
    expect(sessionFase2?.currentPhase).toBe(2);
    expect(sessionFase2?.phaseAnswers[1]).toBe('Neumonía adquirida en la comunidad grave.');
    expect(sessionFase2?.activeDraft).toBe('');
  });

  it('completa la sesión multifase y actualiza estado a completed', () => {
    const caseId = 'caso_sepsis_urgencias';
    const mockFinalOutcome: EvaluationResult = {
      score: 9.2,
      score_max: 10,
      aciertos: ['Código sepsis precoz', 'Reanimación con cristaloides'],
      omisiones: [],
      case_id: caseId,
      retroalimentacion_general: 'Excelente desempeño clínico.',
    };

    useClinicalCaseSessionStore.getState().savePhaseDraft(caseId, 1, 'Fase 1');
    useClinicalCaseSessionStore.getState().savePhaseDraft(caseId, 2, 'Fase 2');
    useClinicalCaseSessionStore.getState().savePhaseDraft(caseId, 3, 'Fase 3');
    useClinicalCaseSessionStore.getState().completeCaseSession(caseId, mockFinalOutcome);

    const session = useClinicalCaseSessionStore.getState().getSession(caseId);
    expect(session?.isCompleted).toBe(true);
    expect(session?.finalResult).toEqual(mockFinalOutcome);

    const progress = useClinicalCaseSessionStore.getState().getCaseProgress(caseId);
    expect(progress.status).toBe('completed');
    expect(progress.score).toBe(9.2);
  });

  it('permite reiniciar la sesión de un caso limpiando su progreso local', () => {
    const caseId = 'caso_cetoacidosis_diabetica';
    useClinicalCaseSessionStore.getState().savePhaseDraft(caseId, 1, 'Respuesta temporal');
    expect(useClinicalCaseSessionStore.getState().getSession(caseId)).toBeDefined();

    useClinicalCaseSessionStore.getState().resetCaseSession(caseId);
    expect(useClinicalCaseSessionStore.getState().getSession(caseId)).toBeUndefined();
    expect(useClinicalCaseSessionStore.getState().getCaseProgress(caseId).status).toBe('not_started');
  });
});
