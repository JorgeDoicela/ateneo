import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, Square, Play, Pause, Trash2, AlertCircle } from 'lucide-react';

interface ClinicalVoiceRecorderProps {
  onAudioChange: (blob: Blob | null) => void;
  disabled?: boolean;
  onRecordingStateChange?: (isRecording: boolean) => void;
}

export default function ClinicalVoiceRecorder({
  onAudioChange,
  disabled = false,
  onRecordingStateChange,
}: ClinicalVoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const recordedDurationRef = useRef<number>(0);

  useEffect(() => {
    onRecordingStateChange?.(isRecording);
  }, [isRecording, onRecordingStateChange]);

  // Formato mm:ss con validación defensiva contra Infinity y NaN (bug nativo de WebM en navegadores)
  const formatTime = (seconds: number) => {
    if (!Number.isFinite(seconds) || isNaN(seconds) || seconds < 0) {
      return '00:00';
    }
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * Libera activamente las pistas del micrófono para no bloquear el hardware
   */
  const releaseStream = useCallback(() => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Ignorar si ya estaba cerrado
        }
      });
      mediaStreamRef.current = null;
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (err) {
        console.warn('Error al detener MediaRecorder:', err);
      }
    }

    const finalDur = Math.max(1, recordedDurationRef.current);
    setAudioDuration(finalDur);
    setIsRecording(false);
  }, []);

  const startRecording = async () => {
    setPermissionError(null);
    try {
      // Liberar cualquier stream previo antes de solicitar uno nuevo
      releaseStream();

      // Solicitar acceso al micrófono
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaStreamRef.current = stream;

      // Detectar formato compatible de mayor fidelidad
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : MediaRecorder.isTypeSupported('audio/mp4')
        ? 'audio/mp4'
        : '';

      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];
      recordedDurationRef.current = 0;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onerror = (event: Event) => {
        console.error('Error en MediaRecorder:', event);
        setPermissionError('Ocurrió un error en la captura de audio.');
        stopRecording();
      };

      recorder.onstop = () => {
        const type = recorder.mimeType || mimeType || 'audio/webm';
        const blob = new Blob(audioChunksRef.current, { type });

        // Prevenir envío de audios vacíos (0 bytes de audio capturados)
        if (!blob || blob.size === 0) {
          releaseStream();
          setPermissionError('Nota de voz demasiado breve o sin audio detectado.');
          return;
        }

        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        onAudioChange(blob);

        // Liberar pistas del micrófono una vez finalizado el guardado
        releaseStream();
      };

      // Escuchar si el usuario desconecta el micro para no congelar la UI (compatible con getAudioTracks y getTracks)
      const tracks = typeof stream.getAudioTracks === 'function'
        ? stream.getAudioTracks()
        : typeof stream.getTracks === 'function'
        ? stream.getTracks()
        : [];

      tracks.forEach((track) => {
        if (track && typeof track.addEventListener === 'function') {
          track.addEventListener('ended', () => {
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
              stopRecording();
            }
          });
        }
      });

      // Intervalo de chunks a 1000ms para estabilidad óptima de memoria
      recorder.start(1000);
      setIsRecording(true);
      setRecordingTime(0);

      timerIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          const nextVal = prev + 1;
          recordedDurationRef.current = nextVal;
          // Límite de 10 minutos (600s)
          if (nextVal >= 600) {
            stopRecording();
            return 600;
          }
          return nextVal;
        });
      }, 1000);
    } catch (err: unknown) {
      console.error('Error al acceder al micrófono:', err);
      setPermissionError('No se pudo acceder al micrófono. Verifica los permisos.');
      releaseStream();
    }
  };

  const discardAudio = () => {
    if (isRecording) {
      stopRecording();
    }
    releaseStream();
    if (audioElementRef.current) {
      try {
        audioElementRef.current.pause();
        audioElementRef.current.currentTime = 0;
      } catch {
        // Ignorar si el reproductor ya no estaba activo
      }
    }
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    recordedDurationRef.current = 0;
    setAudioUrl(null);
    setIsPlaying(false);
    setPlaybackTime(0);
    setAudioDuration(0);
    setRecordingTime(0);
    onAudioChange(null);
  };

  const togglePlayback = () => {
    if (!audioElementRef.current) return;
    if (isPlaying) {
      audioElementRef.current.pause();
      setIsPlaying(false);
    } else {
      audioElementRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
  };

  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
      releaseStream();
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl, releaseStream]);

  return (
    <div className="inline-flex items-center">
      {audioUrl && (
        <audio
          ref={audioElementRef}
          src={audioUrl}
          onLoadedMetadata={(e) => {
            const dur = e.currentTarget.duration;
            if (Number.isFinite(dur) && dur > 0) {
              setAudioDuration(Math.round(dur));
            } else if (recordedDurationRef.current > 0) {
              setAudioDuration(recordedDurationRef.current);
            }
          }}
          onTimeUpdate={(e) => {
            const cur = e.currentTarget.currentTime;
            if (Number.isFinite(cur)) {
              setPlaybackTime(cur);
            }
          }}
          onEnded={() => {
            setIsPlaying(false);
            setPlaybackTime(0);
          }}
          className="hidden"
        />
      )}

      {permissionError && (
        <span className="mr-2 text-xs text-rose-600 font-medium inline-flex items-center gap-1">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{permissionError}</span>
        </span>
      )}

      {/* Estado 1: Botón interactivo para grabar nota de voz */}
      {!isRecording && !audioUrl && (
        <button
          type="button"
          onClick={startRecording}
          disabled={disabled}
          title="Graba tu nota de voz clínica."
          className="relative flex items-center gap-2 px-3.5 py-2 rounded-full border border-slate-200 bg-[#f0f4f9] hover:bg-white hover:border-slate-300 hover:shadow-xs text-[#444746] hover:text-[#1f1f1f] text-xs font-medium transition-all duration-200 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 shrink-0"
        >
          <Mic className="w-3.5 h-3.5 text-[#0b57d0]" />
          <span>Nota de voz</span>
        </button>
      )}

      {/* Estado 2: Grabando con contador y botón para detener */}
      {isRecording && (
        <button
          type="button"
          onClick={stopRecording}
          className="relative flex items-center gap-2 px-3.5 py-2 rounded-full border border-rose-300 bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-medium transition-all duration-200 cursor-pointer shadow-xs shrink-0 animate-fadeIn"
          title="Detener grabación de nota de voz"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-600"></span>
          </span>
          <Square className="w-3.5 h-3.5 fill-rose-600 text-rose-600" />
          <span className="font-mono">Detener ({formatTime(recordingTime)})</span>
        </button>
      )}

      {/* Estado 3: Audio Grabado listo para evaluación */}
      {audioUrl && (
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-200 bg-blue-50/70 text-xs text-[#1f1f1f] shadow-2xs shrink-0 animate-fadeIn">
          <button
            type="button"
            onClick={togglePlayback}
            disabled={disabled}
            className="p-1 rounded-full bg-[#0b57d0] hover:bg-[#0842a0] text-white transition-all cursor-pointer shrink-0 disabled:opacity-50"
            aria-label={isPlaying ? 'Pausar audio' : 'Reproducir audio'}
            title={isPlaying ? 'Pausar' : 'Reproducir'}
          >
            {isPlaying ? <Pause className="w-3 h-3 fill-current" /> : <Play className="w-3 h-3 fill-current" />}
          </button>
          <span className="text-[11px] font-medium text-[#0b57d0]">
            Nota de voz ({formatTime(playbackTime)} / {formatTime(audioDuration || recordingTime)})
          </span>
          <button
            type="button"
            onClick={discardAudio}
            disabled={disabled}
            className="p-1 text-rose-600 hover:text-rose-800 hover:bg-rose-100/60 rounded-full transition-colors cursor-pointer"
            title="Descartar nota de voz"
            aria-label="Descartar nota de voz"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  );
}
