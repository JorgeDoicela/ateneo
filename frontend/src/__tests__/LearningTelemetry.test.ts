import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import useLearningTelemetry from '../modules/analytics/hooks/useLearningTelemetry';
import analyticsApi from '../modules/analytics/api/analyticsApi';

describe('Custom Hook useLearningTelemetry (Ateneo+)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('debe despachar eventos granulares mediante analyticsApi.recordEvent', async () => {
    const recordSpy = vi.spyOn(analyticsApi, 'recordEvent').mockResolvedValue({
      id: 1,
      user_id: 'usr_01',
      tenant_id: 'tenant_uce',
      case_id: 'case_preeclampsia_01',
      event_type: 'case_opened',
      metadata: { titulo: 'Preeclampsia' },
      timestamp: '2026-10-12T16:00:00'
    });

    const { result } = renderHook(() => useLearningTelemetry());

    await act(async () => {
      await result.current.trackCaseOpened('case_preeclampsia_01', { titulo: 'Preeclampsia' });
    });

    expect(recordSpy).toHaveBeenCalledTimes(1);
    expect(recordSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        case_id: 'case_preeclampsia_01',
        event_type: 'case_opened',
        metadata: expect.objectContaining({ titulo: 'Preeclampsia' })
      })
    );
  });

  it('debe registrar eventos de inspección paraclínica con nombre de estudio', async () => {
    const recordSpy = vi.spyOn(analyticsApi, 'recordEvent').mockResolvedValue({
      id: 2,
      user_id: 'usr_01',
      tenant_id: 'tenant_uce',
      case_id: 'case_dengue_01',
      event_type: 'paraclinical_inspected',
      metadata: { study_name: 'ecg_derivaciones' },
      timestamp: '2026-10-12T16:00:00'
    });

    const { result } = renderHook(() => useLearningTelemetry());

    await act(async () => {
      await result.current.trackParaclinicalInspected('case_dengue_01', 'ecg_derivaciones', { zoom: 2 });
    });

    expect(recordSpy).toHaveBeenCalledTimes(1);
    expect(recordSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        case_id: 'case_dengue_01',
        event_type: 'paraclinical_inspected',
        metadata: expect.objectContaining({ study_name: 'ecg_derivaciones', zoom: 2 })
      })
    );
  });

  it('debe aplicar debounce defensivo para evitar spam de eventos idénticos en menos de 1 segundo', async () => {
    const recordSpy = vi.spyOn(analyticsApi, 'recordEvent').mockResolvedValue({
      id: 3,
      user_id: 'usr_01',
      tenant_id: 'tenant_uce',
      case_id: 'case_shock_01',
      event_type: 'case_opened',
      metadata: {},
      timestamp: '2026-10-12T16:00:00'
    });

    const { result } = renderHook(() => useLearningTelemetry());

    await act(async () => {
      // Disparar 3 veces consecutivas en ráfaga
      await result.current.trackCaseOpened('case_shock_01');
      await result.current.trackCaseOpened('case_shock_01');
      await result.current.trackCaseOpened('case_shock_01');
    });

    // Solo debe haber sido invocado una vez debido al debounce de 1000ms
    expect(recordSpy).toHaveBeenCalledTimes(1);
  });
});
