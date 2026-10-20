import { useState, useRef, useCallback, useEffect } from "react";

export interface UseVoiceRecognitionOptions {
  lang?: string;
}

export interface UseVoiceRecognitionReturn {
  isRecording: boolean;
  interimText: string;
  startRecording: (onFinalCallback: (text: string) => void) => void;
  stopRecording: () => void;
  error: string | null;
  isSupported: boolean;
}

// Declaraciones de tipo para Web Speech API en navegadores
interface ISpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface ISpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  lang: string;
  onstart: (() => void) | null;
  onresult: ((event: ISpeechRecognitionEvent) => void) | null;
  onerror: ((event: ISpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => ISpeechRecognition;
    webkitSpeechRecognition?: new () => ISpeechRecognition;
  }
}

/**
 * useVoiceRecognition — Hook robusto de dictado continuo y transcripción clínica
 *
 * Características:
 * 1. Grabación continua real (continuous=true): no se corta por pausas breves al hablar.
 * 2. Cero duplicación: itera estrictamente desde event.resultIndex (estándar W3C).
 * 3. Ciclo de vida estricto: limpia listeners y aborta cualquier sesión anterior antes de arrancar.
 * 4. Permite detener y volver a transcribir inmediatamente sin bloqueos de canal en Chromium.
 */
export function useVoiceRecognition({ lang = "es-EC" }: UseVoiceRecognitionOptions = {}): UseVoiceRecognitionReturn {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [interimText, setInterimText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  // Bandera de intención activa del usuario
  const activeRef = useRef<boolean>(false);
  const recognitionRef = useRef<ISpeechRecognition | null>(null);
  const onFinalRef = useRef<((text: string) => void) | null>(null);
  const restartTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const maxSessionTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const consecutiveRetriesRef = useRef<number>(0);

  const isSupported =
    typeof window !== "undefined" &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  /**
   * Limpia y desasocia completamente la instancia de SpeechRecognition activa.
   */
  const cleanupRecognition = useCallback(() => {
    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current);
      restartTimerRef.current = null;
    }
    if (maxSessionTimeoutRef.current) {
      clearTimeout(maxSessionTimeoutRef.current);
      maxSessionTimeoutRef.current = null;
    }

    if (recognitionRef.current) {
      const rec = recognitionRef.current;
      // Desasociar listeners para evitar callbacks zombi tras abortar
      rec.onstart = null;
      rec.onresult = null;
      rec.onerror = null;
      rec.onend = null;
      try {
        rec.abort();
      } catch {
        // Ignorar si ya estaba inactivo
      }
      recognitionRef.current = null;
    }
  }, []);

  /**
   * Inicia o reinicia una sesión de reconocimiento continua.
   */
  const startSession = useCallback(() => {
    if (!isSupported || !activeRef.current) return;

    // Si ya existe una instancia previa, limpiarla antes de crear la nueva
    cleanupRecognition();

    const SpeechRecognitionClass =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionClass) return;

    try {
      const recognition = new SpeechRecognitionClass();

      // Modo continuo para que no se corte en pausas de habla
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.lang = lang;

      recognition.onstart = () => {
        if (activeRef.current) {
          consecutiveRetriesRef.current = 0; // Reinicio exitoso: reset de contador de fallos
          setIsRecording(true);
          setError(null);
        }
      };

      recognition.onresult = (event: ISpeechRecognitionEvent) => {
        let interimTranscript = "";
        let finalTranscript = "";

        // W3C: iterar únicamente desde resultIndex previene duplicar resultados acumulados
        const startIndex = typeof event.resultIndex === "number" ? event.resultIndex : 0;

        for (let i = startIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result && result[0]) {
            if (result.isFinal) {
              finalTranscript += result[0].transcript;
            } else {
              interimTranscript += result[0].transcript;
            }
          }
        }

        // Si hay texto final, despacharlo
        if (finalTranscript.trim() && onFinalRef.current) {
          onFinalRef.current(finalTranscript.trim());
        }

        // Mantener el texto interino si aún hay habla en progreso, o vaciarlo si solo hubo final
        setInterimText(interimTranscript);
      };

      recognition.onerror = (event: ISpeechRecognitionErrorEvent) => {
        // Silencio o pausa prolongada: no es un error fatal, si el usuario sigue activo reiniciamos suavemente
        if (event.error === "no-speech") {
          if (activeRef.current && consecutiveRetriesRef.current < 4) {
            consecutiveRetriesRef.current += 1;
            restartTimerRef.current = setTimeout(() => {
              if (activeRef.current) startSession();
            }, 100);
          }
          return;
        }

        // Si fue abortado intencionalmente, no mostrar error
        if (event.error === "aborted") {
          return;
        }

        const errorMessages: Record<string, string> = {
          "not-allowed": "Permiso de micrófono denegado. Actívalo en la configuración del navegador.",
          "network": "Error de red en el reconocimiento de voz. Verifica tu conexión.",
          "audio-capture": "No se detectó micrófono. Verifica que esté conectado y habilitado.",
          "service-not-allowed": "Servicio de dictado no disponible en este contexto.",
        };

        const msg = errorMessages[event.error] || `Error de reconocimiento: ${event.error}`;
        setError(msg);
        activeRef.current = false;
        setIsRecording(false);
        setInterimText("");
      };

      recognition.onend = () => {
        // En navegadores como Chrome, continuous=true puede emitir onend tras ~60s de inactividad de red.
        // Si el usuario aún tiene activo el botón de dictado, reconectamos automáticamente de forma imperceptible.
        if (activeRef.current && consecutiveRetriesRef.current < 5) {
          consecutiveRetriesRef.current += 1;
          restartTimerRef.current = setTimeout(() => {
            if (activeRef.current) startSession();
          }, 80);
        } else {
          setIsRecording(false);
          setInterimText("");
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: unknown) {
      console.warn("Fallo al iniciar sesión de reconocimiento, reintentando...", err);
      if (activeRef.current && consecutiveRetriesRef.current < 3) {
        consecutiveRetriesRef.current += 1;
        restartTimerRef.current = setTimeout(() => {
          if (activeRef.current) startSession();
        }, 150);
      } else {
        setError("No fue posible acceder al motor de dictado.");
        activeRef.current = false;
        setIsRecording(false);
      }
    }
  }, [cleanupRecognition, isSupported, lang]);

  const stopRecording = useCallback(() => {
    activeRef.current = false;
    cleanupRecognition();
    setIsRecording(false);
    setInterimText("");
  }, [cleanupRecognition]);

  const startRecording = useCallback((onFinalCallback: (text: string) => void) => {
    if (!isSupported) {
      setError("Tu navegador no soporta dictado por voz. Usa Chrome o Edge.");
      return;
    }

    onFinalRef.current = onFinalCallback;
    activeRef.current = true;
    setError(null);
    setInterimText("");

    // Iniciar con micro-delay de 50ms para asegurar liberación del bus de audio si acababa de pararse
    cleanupRecognition();
    restartTimerRef.current = setTimeout(() => {
      if (activeRef.current) {
        startSession();
      }
    }, 50);

    // Límite de seguridad: 10 minutos continuos
    maxSessionTimeoutRef.current = setTimeout(() => {
      stopRecording();
    }, 600_000);
  }, [cleanupRecognition, isSupported, startSession, stopRecording]);

  useEffect(() => {
    return () => {
      activeRef.current = false;
      cleanupRecognition();
    };
  }, [cleanupRecognition]);

  return {
    isRecording,
    interimText,
    startRecording,
    stopRecording,
    error,
    isSupported,
  };
}

export default useVoiceRecognition;
