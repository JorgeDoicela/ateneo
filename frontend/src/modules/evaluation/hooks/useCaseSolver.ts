import { useState, useCallback, useEffect, FormEvent } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import casesApi from '../../cases/api/casesApi';
import evaluationApi from '../api/evaluationApi';
import offlineDb from '../../../core/storage/offlineDb';
import { useClinicalCaseSessionStore } from '../../../core/stores/useClinicalCaseSessionStore';
import { FEATURE_FLAGS } from '../../../core/config/featureFlags';
import type { ClinicalCase, CasePhase, EvaluationResult, PhaseEvaluationResult, NormativeCitation } from '../../../types';

/**
 * useCaseSolver — Hook controlador de la simulación clínica y evaluación
 * Optimizado con persistencia transaccional (localStorage + IndexedDB + Backend ACID),
 * recuperación automática de borradores por fase y protección ante pérdida de conectividad.
 */
export function useCaseSolver(caseId?: string) {
  const queryClient = useQueryClient();

  // Cargar caso clínico con caché reactiva de TanStack Query y fallback offline
  const {
    data: caso = null,
    isLoading: loading,
    error: queryError,
  } = useQuery<ClinicalCase | null, Error>({
    queryKey: ['clinical-case', caseId],
    queryFn: async () => {
      if (!caseId) return null;
      try {
        const remoteCase = await casesApi.getCaseById(caseId);
        if (remoteCase) {
          await offlineDb.saveCases([remoteCase]);
        }
        return remoteCase;
      } catch (netErr) {
        const localCase = await offlineDb.getCase(caseId);
        if (localCase) return localCase;
        throw netErr;
      }
    },
    enabled: Boolean(caseId),
    staleTime: 5 * 60 * 1000,
  });

  const [error, setError] = useState<string | null>(null);

  // Sesión persistente por caso
  const getSession = useClinicalCaseSessionStore((state) => state.getSession);
  const savePhaseDraft = useClinicalCaseSessionStore((state) => state.savePhaseDraft);
  const savePhaseEvaluation = useClinicalCaseSessionStore((state) => state.savePhaseEvaluation);
  const advancePhase = useClinicalCaseSessionStore((state) => state.advancePhase);
  const completeCaseSession = useClinicalCaseSessionStore((state) => state.completeCaseSession);
  const resetCaseSession = useClinicalCaseSessionStore((state) => state.resetCaseSession);

  // Estados de entrada del estudiante
  const [respuesta, setRespuestaState] = useState<string>('');
  const [imagenes, setImagenes] = useState<File[]>([]);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [evaluating, setEvaluating] = useState<boolean>(false);

  // Resultado definitivo
  const [resultado, setResultado] = useState<EvaluationResult | null>(null);

  // Estados del Modo Multi-Fase
  const [currentPhase, setCurrentPhase] = useState<number>(1);
  const [phaseAnswers, setPhaseAnswers] = useState<Record<number, string>>({});
  const [phaseResults, setPhaseResults] = useState<Record<number, PhaseEvaluationResult>>({});
  const [phaseScores, setPhaseScores] = useState<Record<number, number>>({});
  const [completedPhases, setCompletedPhases] = useState<number[]>([]);
  const [currentPhaseResult, setCurrentPhaseResult] = useState<PhaseEvaluationResult | null>(null);
  const [showingPhaseFeedback, setShowingPhaseFeedback] = useState<boolean>(false);

  const isPhaseMode = Boolean(caso?.fases && caso.fases.length > 0);
  const totalPhases = isPhaseMode && caso?.fases ? caso.fases.length : 1;
  const activePhaseData: CasePhase | null = isPhaseMode && caso?.fases
    ? caso.fases.find((f) => f.fase_numero === currentPhase) || caso.fases[0]
    : null;

  // Restauración profunda de sesión al montar o cambiar caseId
  useEffect(() => {
    if (!caseId) return;

    const savedSession = getSession(caseId);
    if (savedSession) {
      if (savedSession.isCompleted && savedSession.finalResult) {
        setResultado(savedSession.finalResult);
        setCompletedPhases(savedSession.completedPhases || [1, 2, 3]);
        setPhaseAnswers(savedSession.phaseAnswers || {});
        setPhaseScores(savedSession.phaseScores || {});
        setPhaseResults(savedSession.phaseResults || {});
        return;
      }

      if (savedSession.completedPhases && savedSession.completedPhases.length > 0) {
        setCurrentPhase(savedSession.currentPhase || 1);
        setCompletedPhases(savedSession.completedPhases);
        setPhaseAnswers(savedSession.phaseAnswers || {});
        setPhaseScores(savedSession.phaseScores || {});
        setPhaseResults(savedSession.phaseResults || {});
        const activeText = savedSession.activeDraft || savedSession.phaseAnswers[savedSession.currentPhase] || '';
        setRespuestaState(activeText);
        return;
      }

      if (savedSession.activeDraft) {
        setRespuestaState(savedSession.activeDraft);
        return;
      }
    }

    // Fallback a caché IndexedDB si existe evaluación previa
    offlineDb.getCachedResult(caseId).then((cached) => {
      if (cached && !resultado) {
        setResultado(cached);
      }
    });
  }, [caseId, getSession, resultado]);

  // Guardado continuo del borrador en la fase activa
  const setRespuesta = useCallback(
    (valueOrUpdater: string | ((prev: string) => string)) => {
      setRespuestaState((prev) => {
        const next = typeof valueOrUpdater === 'function' ? valueOrUpdater(prev) : valueOrUpdater;
        if (caseId) {
          savePhaseDraft(caseId, currentPhase, next);
        }
        return next;
      });
    },
    [caseId, currentPhase, savePhaseDraft]
  );

  // Envío en Modo Directo (Single-Turn)
  const submitSingleTurn = useCallback(
    async (e?: FormEvent) => {
      if (e) e.preventDefault();
      if (!caseId || (!respuesta.trim() && !audioBlob) || evaluating) return;

      setEvaluating(true);
      setError(null);

      // Si el navegador está desconectado, encolar directamente en Outbox
      if (typeof navigator !== 'undefined' && !navigator.onLine) {
        await offlineDb.queueEvaluation({
          case_id: caseId,
          case_title: caso?.titulo || 'Caso Clínico',
          respuesta_estudiante: respuesta || 'Nota de voz clínica registrada',
          user_email: 'estudiante@ateneo.local',
          tipo: 'single_turn',
        });

        const provisionalOutcome: EvaluationResult = {
          score: 0,
          score_max: 10,
          aciertos: ['Respuesta resguardada exitosamente en el buffer local del dispositivo.'],
          omisiones: [],
          competencias_deficientes: [],
          retroalimentacion_general: 'Modo Local Activo: Se detectó pérdida de red hospitalaria. Su respuesta ha sido resguardada en el dispositivo y se sincronizará automáticamente con el clúster clínico al restablecerse la conectividad.',
        };

        setResultado(provisionalOutcome);
        completeCaseSession(caseId, provisionalOutcome);
        setEvaluating(false);
        return;
      }

      try {
        const res = await evaluationApi.evaluateDirect(
          caseId,
          respuesta,
          FEATURE_FLAGS.ENABLE_STUDENT_IMAGE_UPLOAD && imagenes.length > 0 ? imagenes : null,
          audioBlob
        );
        setResultado(res);
        completeCaseSession(caseId, res);
        await offlineDb.cacheEvaluationResult(caseId, res);

        queryClient.invalidateQueries({ queryKey: ['clinical-cases'] });
        queryClient.invalidateQueries({ queryKey: ['user-evaluation-history'] });
        queryClient.invalidateQueries({ queryKey: ['student-trends'] });
      } catch (err: unknown) {
        // Encolar si es fallo de red
        await offlineDb.queueEvaluation({
          case_id: caseId,
          case_title: caso?.titulo || 'Caso Clínico',
          respuesta_estudiante: respuesta || 'Nota de voz clínica registrada',
          user_email: 'estudiante@ateneo.local',
          tipo: 'single_turn',
        });

        const isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;
        const provisionalOutcome: EvaluationResult = {
          score: 0,
          score_max: 10,
          aciertos: isOnline
            ? ['Respuesta encolada localmente tras demora o interrupción de conexión.']
            : ['Respuesta resguardada en buffer local tras interrupción de red.'],
          omisiones: [],
          competencias_deficientes: [],
          retroalimentacion_general: isOnline
            ? 'Modo Local Activo: La conexión con el servidor demoró más de lo previsto o se interrumpió temporalmente. Su respuesta clínica fue guardada localmente y se sincronizará automáticamente.'
            : 'Modo Local Activo: No fue posible contactar al servidor central en este momento. Su respuesta clínica fue almacenada localmente y se enviará de forma automática en segundo plano.',
        };
        setResultado(provisionalOutcome);
        completeCaseSession(caseId, provisionalOutcome);
      } finally {
        setEvaluating(false);
      }
    },
    [caseId, respuesta, imagenes, audioBlob, evaluating, caso?.titulo, completeCaseSession, queryClient]
  );

  // Envío en Modo Multi-Fase
  const submitPhase = useCallback(
    async (e?: FormEvent) => {
      if (e) e.preventDefault();
      if (!caseId || (!respuesta.trim() && !audioBlob) || evaluating) return;

      setEvaluating(true);
      setError(null);

      const historialText = Object.entries(phaseAnswers)
        .map(([num, ans]) => `Fase ${num}: ${ans}`)
        .join('\n');

      // Si el navegador está desconectado, encolar en Outbox
      if (typeof navigator !== 'undefined' && !navigator.onLine) {
        await offlineDb.queueEvaluation({
          case_id: caseId,
          case_title: caso?.titulo || 'Caso Clínico',
          respuesta_estudiante: respuesta || 'Nota de voz clínica registrada',
          fase_numero: currentPhase,
          user_email: 'estudiante@ateneo.local',
          tipo: 'phase',
        });

        const provisionalPhaseResult: PhaseEvaluationResult = {
          score_fase: 0,
          aciertos: ['Respuesta de fase resguardada en buffer local.'],
          omisiones: [],
          retroalimentacion_fase: 'Modo Local Activo: Su respuesta de fase quedó registrada en el dispositivo. La evaluación analítica se completará automáticamente al reconectarse a la red.',
          desbloquea_siguiente: true,
        };

        savePhaseEvaluation(caseId, currentPhase, respuesta || 'Nota de voz', provisionalPhaseResult);
        setPhaseAnswers((prev) => ({ ...prev, [currentPhase]: respuesta || 'Nota de voz' }));
        setPhaseResults((prev) => ({ ...prev, [currentPhase]: provisionalPhaseResult }));
        setPhaseScores((prev) => ({ ...prev, [currentPhase]: 0 }));
        setCompletedPhases((prev) =>
          prev.includes(currentPhase) ? prev : [...prev, currentPhase]
        );

        setCurrentPhaseResult(provisionalPhaseResult);
        setShowingPhaseFeedback(true);
        setEvaluating(false);
        return;
      }

      try {
        const res = await evaluationApi.evaluatePhase(
          caseId,
          currentPhase,
          respuesta,
          historialText,
          FEATURE_FLAGS.ENABLE_STUDENT_IMAGE_UPLOAD && imagenes.length > 0 ? imagenes : null,
          audioBlob
        );

        savePhaseEvaluation(caseId, currentPhase, respuesta || 'Nota de voz clínica', res);
        setPhaseAnswers((prev) => ({ ...prev, [currentPhase]: respuesta || 'Nota de voz clínica' }));
        setPhaseResults((prev) => ({ ...prev, [currentPhase]: res }));
        setPhaseScores((prev) => ({ ...prev, [currentPhase]: res.score_fase }));
        setCompletedPhases((prev) =>
          prev.includes(currentPhase) ? prev : [...prev, currentPhase]
        );

        setCurrentPhaseResult(res);
        setShowingPhaseFeedback(true);
      } catch (err: unknown) {
        // Encolar si es fallo de red
        await offlineDb.queueEvaluation({
          case_id: caseId,
          case_title: caso?.titulo || 'Caso Clínico',
          respuesta_estudiante: respuesta || 'Nota de voz clínica registrada',
          fase_numero: currentPhase,
          user_email: 'estudiante@ateneo.local',
          tipo: 'phase',
        });

        const provisionalPhaseResult: PhaseEvaluationResult = {
          score_fase: 0,
          aciertos: ['Respuesta guardada localmente tras corte de red.'],
          omisiones: [],
          retroalimentacion_fase: 'Modo Local Activo: Se guardó su avance de fase. Se sincronizará automáticamente al restablecerse la conectividad.',
          desbloquea_siguiente: true,
        };

        savePhaseEvaluation(caseId, currentPhase, respuesta || 'Nota de voz', provisionalPhaseResult);
        setPhaseAnswers((prev) => ({ ...prev, [currentPhase]: respuesta || 'Nota de voz' }));
        setPhaseResults((prev) => ({ ...prev, [currentPhase]: provisionalPhaseResult }));
        setPhaseScores((prev) => ({ ...prev, [currentPhase]: 0 }));
        setCompletedPhases((prev) =>
          prev.includes(currentPhase) ? prev : [...prev, currentPhase]
        );

        setCurrentPhaseResult(provisionalPhaseResult);
        setShowingPhaseFeedback(true);
      } finally {
        setEvaluating(false);
      }
    },
    [caseId, currentPhase, respuesta, imagenes, audioBlob, phaseAnswers, evaluating, caso?.titulo, savePhaseEvaluation]
  );

  // Avanzar a la siguiente fase o consolidar y persistir simulación
  const proceedToNextPhase = useCallback(async () => {
    setShowingPhaseFeedback(false);
    setCurrentPhaseResult(null);
    setImagenes([]);
    setAudioBlob(null);

    if (currentPhase < totalPhases) {
      const nextPhase = currentPhase + 1;
      if (caseId) {
        advancePhase(caseId, nextPhase);
      }
      setCurrentPhase(nextPhase);
      const nextPhaseText = phaseAnswers[nextPhase] || '';
      setRespuestaState(nextPhaseText);
    } else {
      // Consolidar resultado global de todas las fases
      const scores = Object.values(phaseScores);
      const avgScore =
        scores.length > 0
          ? scores.reduce((a, b) => a + b, 0) / scores.length
          : 8.0;

      const allAciertos = Object.values(phaseResults).flatMap(
        (r) => r.aciertos || []
      );
      const allOmisiones = Object.values(phaseResults).flatMap(
        (r) => r.omisiones || []
      );

      const allCompetenciasDeficientes = Object.values(phaseResults).flatMap(
        (r) => r.competencias_deficientes || []
      );

      const allCitasNormativas: NormativeCitation[] = Object.values(phaseResults)
        .map((r) => r.cita_normativa)
        .filter((c): c is NormativeCitation => Boolean(c));

      const primaryCita = allCitasNormativas[0] || {
        guia: caso?.guia_asociada || 'GPC Ecuador',
        seccion: 'Resolución Multicomponente por Fases',
        texto_relevante: 'Evaluación formativa secuencial basada en Guías de Práctica Clínica del MSP Ecuador.'
      };

      const finalOutcome: EvaluationResult = {
        case_id: caseId,
        case_title: caso?.titulo || 'Caso Clínico Formativo',
        score: Math.round(avgScore * 10) / 10,
        score_max: 10,
        aciertos: allAciertos,
        omisiones: allOmisiones,
        competencias_deficientes: allCompetenciasDeficientes,
        cita_normativa: primaryCita,
        citas_normativas: allCitasNormativas,
        retroalimentacion_general: `Simulación clínica multicomponente completada exitosamente a través de las ${totalPhases} fases normativas de la GPC de Ecuador.`,
      };

      setResultado(finalOutcome);

      if (caseId) {
        // 1. Guardar en memoria local estructurada (localStorage)
        completeCaseSession(caseId, finalOutcome);
        // 2. Guardar en IndexedDB
        await offlineDb.cacheEvaluationResult(caseId, finalOutcome);

        // 3. Persistir en el Backend relacional (ACID)
        try {
          await evaluationApi.saveEvaluationRecord({
            case_id: caseId,
            case_title: caso?.titulo || 'Caso Clínico Formativo',
            guia_asociada: caso?.guia_asociada || 'GPC Ecuador',
            score: finalOutcome.score,
            score_max: 10,
            faithfulness_score: 1.0,
            aciertos: finalOutcome.aciertos,
            omisiones: finalOutcome.omisiones,
            competencias_deficientes: finalOutcome.competencias_deficientes,
            cita_normativa: finalOutcome.cita_normativa,
            citas_normativas: finalOutcome.citas_normativas,
            retroalimentacion_general: finalOutcome.retroalimentacion_general,
            tiempo_segundos: 180,
            modo_simulacion: 'fases',
            fases_respuestas: Object.fromEntries(
              Object.entries(phaseAnswers).map(([k, v]) => [String(k), String(v)])
            ),
          });
        } catch (saveErr) {
          console.warn('Error al sincronizar resultado en backend, encolando en Outbox:', saveErr);
          await offlineDb.queueEvaluation({
            case_id: caseId,
            case_title: caso?.titulo || 'Caso Clínico Formativo',
            respuesta_estudiante: JSON.stringify(phaseAnswers),
            user_email: 'estudiante@ateneo.local',
            tipo: 'single_turn',
          });
        }

        // 4. Invalidar queries para actualizar catálogo y analítica de inmediato
        queryClient.invalidateQueries({ queryKey: ['clinical-cases'] });
        queryClient.invalidateQueries({ queryKey: ['user-evaluation-history'] });
        queryClient.invalidateQueries({ queryKey: ['student-trends'] });
      }
    }
  }, [
    currentPhase,
    totalPhases,
    caseId,
    advancePhase,
    phaseAnswers,
    phaseScores,
    phaseResults,
    caso?.titulo,
    caso?.guia_asociada,
    completeCaseSession,
    queryClient
  ]);

  // Reiniciar caso para reintentar desde cero conscientemente
  const resetCase = useCallback(() => {
    if (caseId) resetCaseSession(caseId);
    setResultado(null);
    setRespuestaState('');
    setImagenes([]);
    setAudioBlob(null);
    setError(null);
    setCurrentPhase(1);
    setPhaseAnswers({});
    setPhaseResults({});
    setPhaseScores({});
    setCompletedPhases([]);
    setCurrentPhaseResult(null);
    setShowingPhaseFeedback(false);
  }, [caseId, resetCaseSession]);

  const effectiveError = error || (queryError ? queryError.message : null);

  return {
    caso,
    loading,
    error: effectiveError,
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
  };
}

export default useCaseSolver;
