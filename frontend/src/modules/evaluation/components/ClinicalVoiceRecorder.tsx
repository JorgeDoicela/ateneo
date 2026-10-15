import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, Square, Play, Pause, Trash2, AlertCircle } from 'lucide-react';

interface ClinicalVoiceRecorderProps {
  onAudioChange: (blob: Blob | null) => void;
  disabled?: boolean;
}

export default function ClinicalVoiceRecorder({ onAudioChange, disabled = false }: ClinicalVoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackTime, setPlaybackTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<number | null>(null);
  const audioElementRef = useRef<HTMLAudioElement | null>(null);
  const recordedDurationRef = useRef<number>(0);

  // Formato mm:ss con validación defensiva contra Infinity y NaN (bug nativo de WebM en navegadores)
  const formatTime = (seconds: number) => {
    if (!Number.isFinite(seconds) || isNaN(seconds) || seconds < 0) {
      return '00:00';
    }
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    setPermissionError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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

      recorder.onstop = () => {
        const type = recorder.mimeType || 'audio/webm';
        const blob = new Blob(audioChunksRef.current, { type });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        onAudioChange(blob);

        // Detener pistas del microfono
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start(250);
      setIsRecording(true);
      setRecordingTime(0);

      timerIntervalRef.current = window.setInterval(() => {
        setRecordingTime((prev) => {
          const nextVal = prev + 1;
          recordedDurationRef.current = nextVal;
          if (nextVal >= 300) {
            // Limite de 5 minutos
            stopRecording();
            return 300;
          }
          return nextVal;
        });
      }, 1000);
    } catch (err: unknown) {
      console.error('Error al acceder al micrófono:', err);
      setPermissionError('No se pudo acceder al micrófono.');
    }
  };

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
    const finalDur = Math.max(1, recordedDurationRef.current || recordingTime);
    setAudioDuration(finalDur);
    setIsRecording(false);
  }, [recordingTime]);

  const discardAudio = () => {
    if (isRecording) {
      stopRecording();
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
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

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

      {/* Estado 1: Todo el div funciona como botón interactivo para grabar nota de voz */}
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
