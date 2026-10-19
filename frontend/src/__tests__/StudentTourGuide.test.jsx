import React from 'react';
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import useTourStore from '../core/tour/useTourStore';
import TourHelpButton from '../core/tour/TourHelpButton';
import StudentTourGuide from '../core/tour/StudentTourGuide';
import { CATALOG_TOUR_STEPS } from '../core/tour/tourSteps';

describe('Sistema de Tour Guiado Formativo (Ateneo+)', () => {
  beforeEach(() => {
    useTourStore.getState().closeTour();
  });

  it('no debe renderizar nada en StudentTourGuide cuando isOpen es falso', () => {
    const { container } = render(<StudentTourGuide />);
    expect(container.firstChild).toBeNull();
  });

  it('debe abrir el tour al pulsar TourHelpButton en la ruta de catálogo', () => {
    render(
      <MemoryRouter initialEntries={['/cases']}>
        <TourHelpButton />
      </MemoryRouter>
    );

    const helpBtn = screen.getByRole('button', { name: /Abrir guía interactiva del simulador/i });
    expect(helpBtn).toBeInTheDocument();

    fireEvent.click(helpBtn);
    expect(useTourStore.getState().isOpen).toBe(true);
    expect(useTourStore.getState().currentStepIndex).toBe(0);
  });

  it('debe renderizar el primer paso con título, descripción y contador de pasos', () => {
    useTourStore.getState().startTour();

    render(<StudentTourGuide />);

    const firstStep = CATALOG_TOUR_STEPS[0];
    expect(screen.getByText(firstStep.title)).toBeInTheDocument();
    expect(screen.getByText(firstStep.description)).toBeInTheDocument();
    expect(screen.getByText(new RegExp(`Paso 1 de ${CATALOG_TOUR_STEPS.length}`, 'i'))).toBeInTheDocument();
  });

  it('debe avanzar al siguiente paso al pulsar el botón Siguiente', () => {
    useTourStore.getState().startTour();

    render(<StudentTourGuide />);

    const nextBtn = screen.getByRole('button', { name: /Siguiente/i });
    fireEvent.click(nextBtn);

    expect(useTourStore.getState().currentStepIndex).toBe(1);
    const secondStep = CATALOG_TOUR_STEPS[1];
    expect(screen.getByText(secondStep.title)).toBeInTheDocument();
  });

  it('debe cerrar el tour al pulsar el botón de cerrar o Saltar guía', () => {
    useTourStore.getState().startTour();

    render(<StudentTourGuide />);

    const skipBtn = screen.getByRole('button', { name: /Saltar guía/i });
    fireEvent.click(skipBtn);

    expect(useTourStore.getState().isOpen).toBe(false);
  });
});
