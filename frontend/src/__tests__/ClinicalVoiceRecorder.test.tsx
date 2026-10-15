import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import ClinicalVoiceRecorder from '../modules/evaluation/components/ClinicalVoiceRecorder';

describe('Componente ClinicalVoiceRecorder (Grabación de Nota de Voz Clínica)', () => {
  let mockStream: any;

  beforeEach(() => {
    mockStream = {
      getTracks: vi.fn().mockReturnValue([
        { stop: vi.fn() }
      ])
    };

    class FakeMediaRecorder {
      state = 'inactive';
      mimeType = 'audio/webm';
      ondataavailable: ((e: any) => void) | null = null;
      onstop: (() => void) | null = null;

      start() {
        this.state = 'recording';
      }

      stop() {
        this.state = 'inactive';
        if (this.ondataavailable) {
          this.ondataavailable({ data: new Blob(['fake_audio'], { type: 'audio/webm' }) });
        }
        if (this.onstop) {
          this.onstop();
        }
      }

      static isTypeSupported() {
        return true;
      }
    }

    // @ts-expect-error Mock global de MediaRecorder
    window.MediaRecorder = FakeMediaRecorder;

    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: vi.fn().mockResolvedValue(mockStream)
      },
      writable: true,
      configurable: true
    });

    // Mock global de URL.createObjectURL y revokeObjectURL
    window.URL.createObjectURL = vi.fn().mockReturnValue('blob:http://localhost/fake-audio-uuid');
    window.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('debe renderizar inicialmente el botón con texto "Nota de voz"', () => {
    render(<ClinicalVoiceRecorder onAudioChange={vi.fn()} />);
    const button = screen.getByRole('button', { name: /nota de voz/i });
    expect(button).toBeInTheDocument();
  });

  it('debe iniciar la grabación y mostrar "Detener" al hacer clic', async () => {
    render(<ClinicalVoiceRecorder onAudioChange={vi.fn()} />);
    const button = screen.getByRole('button', { name: /nota de voz/i });

    await act(async () => {
      fireEvent.click(button);
    });

    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true });
    expect(screen.getByText(/detener/i)).toBeInTheDocument();
  });

  it('debe detener la grabación, invocar onAudioChange con el Blob y mostrar el reproductor', async () => {
    const handleAudioChange = vi.fn();
    render(<ClinicalVoiceRecorder onAudioChange={handleAudioChange} />);
    
    // Iniciar grabación
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /nota de voz/i }));
    });

    // Detener grabación
    const stopButton = screen.getByText(/detener/i);
    await act(async () => {
      fireEvent.click(stopButton);
    });

    expect(handleAudioChange).toHaveBeenCalledWith(expect.any(Blob));
    expect(screen.getByText(/nota de voz \(/i)).toBeInTheDocument();
    expect(screen.getByTitle(/descartar nota de voz/i)).toBeInTheDocument();
  });

  it('debe descartar el audio al pulsar el botón de descarte y llamar onAudioChange(null)', async () => {
    const handleAudioChange = vi.fn();
    render(<ClinicalVoiceRecorder onAudioChange={handleAudioChange} />);

    // Iniciar y detener grabación para tener audio
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /nota de voz/i }));
    });
    await act(async () => {
      fireEvent.click(screen.getByText(/detener/i));
    });

    // Descartar audio
    const discardButton = screen.getByTitle(/descartar nota de voz/i);
    await act(async () => {
      fireEvent.click(discardButton);
    });

    expect(handleAudioChange).toHaveBeenLastCalledWith(null);
    expect(window.URL.revokeObjectURL).toHaveBeenCalledWith('blob:http://localhost/fake-audio-uuid');
    expect(screen.getByRole('button', { name: /nota de voz/i })).toBeInTheDocument();
  });

  it('debe mostrar mensaje de error si no se conceden permisos de micrófono', async () => {
    navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(new Error('Permission denied'));

    render(<ClinicalVoiceRecorder onAudioChange={vi.fn()} />);
    const button = screen.getByRole('button', { name: /nota de voz/i });

    await act(async () => {
      fireEvent.click(button);
    });

    await waitFor(() => {
      expect(screen.getByText(/no se pudo acceder al micrófono/i)).toBeInTheDocument();
    });
  });
});
