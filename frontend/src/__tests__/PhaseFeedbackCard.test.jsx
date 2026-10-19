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

  it('debe renderizar datos_fase_siguiente cuando viene como objeto estructurado sin romper React', () => {
    const objectPhaseResult = {
      ...mockPhaseResult,
      datos_fase_siguiente: {
        fase_numero: 2,
        titulo: 'Fase 2: Pruebas Complementarias',
        descripcion: 'Evolución a las 2 horas de ingreso.',
        datos_revelados: 'Plaquetas: 85.000 /uL'
      }
    };
    render(<PhaseFeedbackCard phaseResult={objectPhaseResult} currentPhase={1} onProceedNextPhase={() => {}} />);
    expect(screen.getByText(/Nuevos Hallazgos Clínicos Desbloqueados/i)).toBeInTheDocument();
    expect(screen.getByText('Fase 2: Pruebas Complementarias')).toBeInTheDocument();
    expect(screen.getByText('Evolución a las 2 horas de ingreso.')).toBeInTheDocument();
    expect(screen.getByText(/Plaquetas: 85.000/i)).toBeInTheDocument();
  });

  it('debe renderizar el botón de Debate Socrático cuando existen omisiones y abrir el debriefing al pulsar', async () => {
    const { useSocraticDebriefStore } = await import('../modules/evaluation/store/useSocraticDebriefStore');
    useSocraticDebriefStore.getState().closeDebrief();

    render(
      <PhaseFeedbackCard
        phaseResult={mockPhaseResult}
        currentPhase={1}
        caseId="case_trombo_01"
        caseTitle="Tromboembolismo Pulmonar"
        onProceedNextPhase={() => {}}
      />
    );

    const debateButton = screen.getByRole('button', { name: /Debate Socrático/i });
    expect(debateButton).toBeInTheDocument();

    fireEvent.click(debateButton);
    const storeState = useSocraticDebriefStore.getState();
    expect(storeState.isOpen).toBe(true);
    expect(storeState.caseId).toBe('case_trombo_01');
    expect(storeState.caseTitle).toBe('Tromboembolismo Pulmonar (Fase 1)');
    expect(storeState.omisiones).toEqual(['No solicitó dímero D']);
  });

  it('no debe mostrar el botón de Debate Socrático si no hay omisiones en la fase', () => {
    const cleanPhaseResult = {
      ...mockPhaseResult,
      omisiones: []
    };
    render(<PhaseFeedbackCard phaseResult={cleanPhaseResult} currentPhase={1} onProceedNextPhase={() => {}} />);
    expect(screen.queryByRole('button', { name: /Debate Socrático/i })).not.toBeInTheDocument();
  });
});
