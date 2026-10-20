import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent;
    appinstalled: Event;
  }
}

// Almacenamiento global para capturar el evento en el milisegundo cero, antes de que React se monte
let globalDeferredPrompt: BeforeInstallPromptEvent | null = null;

if (typeof window !== 'undefined') {
  window.addEventListener('beforeinstallprompt', (e: BeforeInstallPromptEvent) => {
    e.preventDefault();
    globalDeferredPrompt = e;
  });

  window.addEventListener('appinstalled', () => {
    globalDeferredPrompt = null;
  });
}

export type PWAInstallOutcome = 'accepted' | 'dismissed' | 'guide_shown';

/**
 * usePWAInstall — Hook integral para gestión de instalación de Ateneo+ PWA.
 * Compatible con Chromium (Chrome, Edge, Android, Brave, Opera) y Safari iOS / Desktop.
 */
export function usePWAInstall() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(() => globalDeferredPrompt);
  const [isInstalled, setIsInstalled] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as unknown as { standalone?: boolean }).standalone === true
    );
  });
  const [showInstallModal, setShowInstallModal] = useState<boolean>(false);

  const isIOS = typeof navigator !== 'undefined' && 
    /iPad|iPhone|iPod/.test(navigator.userAgent) && 
    !(window as unknown as { MSStream?: unknown }).MSStream;

  const isInstallable = !isInstalled;

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      globalDeferredPrompt = e;
      setDeferredPrompt(e);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      globalDeferredPrompt = null;
      setDeferredPrompt(null);
      setShowInstallModal(false);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Detección reactiva de cambios de display-mode
    const mediaQuery = window.matchMedia('(display-mode: standalone)');
    const handleDisplayModeChange = (e: MediaQueryListEvent) => {
      if (e.matches) {
        setIsInstalled(true);
        setShowInstallModal(false);
      }
    };
    mediaQuery.addEventListener('change', handleDisplayModeChange);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      mediaQuery.removeEventListener('change', handleDisplayModeChange);
    };
  }, []);

  const promptInstall = useCallback(async (): Promise<PWAInstallOutcome> => {
    if (isInstalled) return 'accepted';

    // En iOS siempre se requiere la guía asistida de Safari (no soporta beforeinstallprompt)
    if (isIOS) {
      setShowInstallModal(true);
      return 'guide_shown';
    }

    const promptEvent = deferredPrompt || globalDeferredPrompt;
    
    // Si el navegador aún no emitió beforeinstallprompt o no lo soporta en este contexto,
    // mostramos de inmediato la guía institucional sin dejar al usuario sin respuesta.
    if (!promptEvent) {
      setShowInstallModal(true);
      return 'guide_shown';
    }

    try {
      await promptEvent.prompt();
      const choice = await promptEvent.userChoice;
      if (choice.outcome === 'accepted') {
        setIsInstalled(true);
        globalDeferredPrompt = null;
        setDeferredPrompt(null);
        setShowInstallModal(false);
        return 'accepted';
      }
      return 'dismissed';
    } catch (err) {
      console.warn('Aviso: el prompt nativo de PWA no pudo desplegarse, mostrando guía asistida:', err);
      setShowInstallModal(true);
      return 'guide_shown';
    }
  }, [deferredPrompt, isIOS, isInstalled]);

  return {
    isInstallable,
    isInstalled,
    isIOS,
    showIOSModal: showInstallModal, // Alias para compatibilidad hacia atrás
    setShowIOSModal: setShowInstallModal,
    showInstallModal,
    setShowInstallModal,
    promptInstall
  };
}

export default usePWAInstall;
