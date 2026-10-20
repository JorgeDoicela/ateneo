import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePWAInstall } from '../core/pwa/usePWAInstall';

describe('Hook usePWAInstall (Gestión Inmediata de Instalación PWA)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('debe mostrar la guía asistida inmediatamente si el navegador no tiene el prompt nativo en memoria (cero clics al vacío)', async () => {
    const { result } = renderHook(() => usePWAInstall());

    expect(result.current.isInstalled).toBe(false);
    expect(result.current.showInstallModal).toBe(false);

    let outcome: string = '';
    await act(async () => {
      outcome = await result.current.promptInstall();
    });

    // Debe mostrar la guía institucional de inmediato al primer clic
    expect(outcome).toBe('guide_shown');
    expect(result.current.showInstallModal).toBe(true);
  });

  it('debe ejecutar el prompt nativo y marcar isInstalled si el evento beforeinstallprompt fue capturado', async () => {
    const fakePromptEvent = {
      preventDefault: vi.fn(),
      prompt: vi.fn().mockResolvedValue(undefined),
      userChoice: Promise.resolve({ outcome: 'accepted', platform: 'web' }),
    };

    const { result } = renderHook(() => usePWAInstall());

    // Simular que el navegador emite beforeinstallprompt
    act(() => {
      window.dispatchEvent(
        Object.assign(new Event('beforeinstallprompt'), fakePromptEvent)
      );
    });

    let outcome: string = '';
    await act(async () => {
      outcome = await result.current.promptInstall();
    });

    expect(outcome).toBe('accepted');
    expect(result.current.isInstalled).toBe(true);
  });
});
