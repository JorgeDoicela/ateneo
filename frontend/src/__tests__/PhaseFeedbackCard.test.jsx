import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PhaseFeedbackCard from '../modules/evaluation/components/PhaseFeedbackCard';

describe('Componente PhaseFeedbackCard (Resolución por Fases)', () => {
  const mockPhaseResult = {
    score_fase: 8.5,
    aciertos: ['Sospecha diagnóstica acertada'],
    omisiones: ['No solicitó dímero D'],
    cita_normativa: {
      guia: 'GPC Tromboembolismo',
      seccion: 'Diagnóstico',
      pagina: 10,
      texto_relevante: 'Dímero D indicado en probabilidad baja/intermedia.'
    },
    retroalimentacion_fase: 'Buen abordaje inicial.',
    datos_fase_siguiente: 'El paciente presenta ahora hipotensión.'
  };

  it('no debe renderizar nada si phaseResult es nulo', () => {
    const { container } = render(<PhaseFeedbackCard phaseResult={null} currentPhase={1} onProceedNextPhase={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it('debe renderizar el título del hito y el puntaje de la fase', () => {
    render(<PhaseFeedbackCard phaseResult={mockPhaseResult} currentPhase={1} onProceedNextPhase={() => {}} />);
    expect(screen.getByText(/Dictamen Formativo — Fase 1/i)).toBeInTheDocument();
    expect(screen.getByText('8.5')).toBeInTheDocument();
    expect(screen.getByText(/Hito Clínico Aprobado/i)).toBeInTheDocument();
  });

  it('debe invocar onProceedNextPhase cuando se pulsa el botón de avanzar', () => {
    const mockProceed = vi.fn();
    render(<PhaseFeedbackCard phaseResult={mockPhaseResult} currentPhase={1} onProceedNextPhase={mockProceed} isLastPhase={false} />);
    const button = screen.getByText(/Continuar a Fase 2/i);
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    expect(mockProceed).toHaveBeenCalledTimes(1);
  });

  it('debe renderizar retroalimentacion_fase con soporte de Markdown estructural', () => {
    const mdPhaseResult = {
      ...mockPhaseResult,
      retroalimentacion_fase: '### Conducta Inmediata\nAdministrar **Heparina de bajo peso molecular**.'
    };
    render(<PhaseFeedbackCard phaseResult={mdPhaseResult} currentPhase={1} onProceedNextPhase={() => {}} />);
    expect(screen.getByRole('heading', { level: 3, name: /Conducta Inmediata/i })).toBeInTheDocument();
    expect(screen.getByText('Heparina de bajo peso molecular').tagName.toLowerCase()).toBe('strong');
  });
});
