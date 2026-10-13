import { useCallback, useRef } from 'react';
import analyticsApi from '../api/analyticsApi';
import type { LearningEventType, LearningActivityEvent } from '../../../types';

/**
 * Custom Hook para Observabilidad y Telemetría de Actividad de Aprendizaje (Ateneo+)
 * Despacha eventos granulares sin bloquear la navegación ni la experiencia pedagógica.
 */
export function useLearningTelemetry() {
  const debounceMap = useRef<Record<string, number>>({});

  const trackEvent = useCallback(
    async (
      event_type: LearningEventType,
      case_id: string,
      metadata: Record<string, unknown> = {}
    ) => {
      // Prevención defensiva de eventos repetitivos en ráfaga (debounce 1s)
      const debounceKey = `${event_type}_${case_id}`;
      const now = Date.now();
      if (debounceMap.current[debounceKey] && now - debounceMap.current[debounceKey] < 1000) {
        return;
      }
      debounceMap.current[debounceKey] = now;

      const eventPayload: LearningActivityEvent = {
        case_id,
        event_type,
        metadata: {
          ...metadata,
          user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
          screen_width: typeof window !== 'undefined' ? window.innerWidth : 0,
        },
      };

      try {
        await analyticsApi.recordEvent(eventPayload);
      } catch (err) {
        // En observabilidad de cliente, las excepciones de red no interrumpen la interacción
        if (import.meta.env?.DEV) {
          console.debug('[Telemetry] Evento no entregado (modo offline o fallback):', err);
        }
      }
    },
    []
  );

  const trackCaseOpened = useCallback(
    (case_id: string, metadata?: Record<string, unknown>) => {
      return trackEvent('case_opened', case_id, metadata);
    },
    [trackEvent]
  );

  const trackParaclinicalInspected = useCallback(
    (case_id: string, study_name: string, metadata?: Record<string, unknown>) => {
      return trackEvent('paraclinical_inspected', case_id, {
        study_name,
        ...metadata,
      });
    },
    [trackEvent]
  );

  const trackSocraticDebriefOpened = useCallback(
    (case_id: string, omision: string, metadata?: Record<string, unknown>) => {
      return trackEvent('socratic_debrief_opened', case_id, {
        omision_discutida: omision,
        ...metadata,
      });
    },
    [trackEvent]
  );

  return {
    trackEvent,
    trackCaseOpened,
    trackParaclinicalInspected,
    trackSocraticDebriefOpened,
  };
}

export default useLearningTelemetry;
