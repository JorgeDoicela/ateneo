import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';

describe('Hook useVoiceRecognition (Ciclo de Vida y Recuperación de Sesiones)', () => {
  let createdInstances: any[] = [];

  class MockSpeechRecognition {
    continuous = false;
    interimResults = false;
    maxAlternatives = 1;
    lang = '';
    onstart: (() => void) | null = null;
    onresult: ((e: any) => void) | null = null;
    onerror: ((e: any) => void) | null = null;
    onend: (() => void) | null = null;

    start = vi.fn().mockImplementation(() => {
      setTimeout(() => {
        if (this.onstart) this.onstart();
      }, 0);
    });

    stop = vi.fn().mockImplementation(() => {
      setTimeout(() => {
        if (this.onend) this.onend();
      }, 0);
    });

    abort = vi.fn();

    constructor() {
      createdInstances.push(this);
    }
  }

  beforeEach(() => {
    vi.useFakeTimers();
    createdInstances = [];
    // @ts-expect-error Mock global Web Speech API
    window.webkitSpeechRecognition = MockSpeechRecognition;
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
    delete (window as any).webkitSpeechRecognition;
  });

  it('debe detectar que la API está soportada', () => {
    const { result } = renderHook(() => useVoiceRecognition());
    expect(result.current.isSupported).toBe(true);
    expect(result.current.isRecording).toBe(false);
  });

  it('debe permitir iniciar, cortar y volver a transcribir inmediatamente sin quedar bloqueado', async () => {
    const { result } = renderHook(() => useVoiceRecognition());
    const onFinal = vi.fn();

    // 1. Iniciar primera sesión
    act(() => {
      result.current.startRecording(onFinal);
    });

    // Avanzar micro-timer de inicio seguro (50ms)
    act(() => {
      vi.advanceTimersByTime(60);
    });

    expect(createdInstances.length).toBe(1);
    expect(createdInstances[0].start).toHaveBeenCalled();
    expect(result.current.isRecording).toBe(true);

    // 2. Cortar (detener)
    act(() => {
      result.current.stopRecording();
    });

    expect(createdInstances[0].abort).toHaveBeenCalled();
    expect(result.current.isRecording).toBe(false);

    // 3. Volver a transcribir inmediatamente (caso que reportó el usuario)
    act(() => {
      result.current.startRecording(onFinal);
    });

    // Avanzar micro-timer para la nueva sesión
    act(() => {
      vi.advanceTimersByTime(60);
    });

    expect(createdInstances.length).toBe(2);
    expect(createdInstances[1].start).toHaveBeenCalled();
    expect(result.current.isRecording).toBe(true);
  });

  it('debe acumular fragmentos finales usando resultIndex sin duplicar texto', () => {
    const { result } = renderHook(() => useVoiceRecognition());
    const onFinal = vi.fn();

    act(() => {
      result.current.startRecording(onFinal);
      vi.advanceTimersByTime(60);
    });

    const activeRec = createdInstances[0];

    // Simular primer evento de reconocimiento
    act(() => {
      if (activeRec.onresult) {
        activeRec.onresult({
          resultIndex: 0,
          results: [
            [{ transcript: 'paciente femenino' }],
          ],
        });
        // Marcar como final
        activeRec.results = [{ isFinal: true, 0: { transcript: 'paciente femenino' } }];
        activeRec.onresult({
          resultIndex: 0,
          results: activeRec.results,
        });
      }
    });

    expect(onFinal).toHaveBeenCalledWith('paciente femenino');
  });
});
