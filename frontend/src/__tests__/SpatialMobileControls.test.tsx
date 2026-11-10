import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { useSpatialStore } from '../modules/spatial/store/useSpatialStore';
import { MobileTouchControls } from '../modules/spatial/components/MobileTouchControls';
import { LandscapeOrientationNotice } from '../modules/spatial/components/LandscapeOrientationNotice';

// Mock de react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate
}));

describe('Suite de Pruebas: Controles Móviles y Orientación Horizontal 3D (Ateneo+)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useSpatialStore.setState({
      hoveredBedId: null,
      isTabletOpen: false,
      touchInput: {
        moveX: 0,
        moveY: 0,
        isSprinting: false,
        lookDeltaX: 0,
        lookDeltaY: 0
      }
    });
  });

  it('debe renderizar los controles táctiles móviles en pantalla (joystick y botones)', () => {
    render(<MobileTouchControls />);

    // Botones de rotación rápida
    expect(screen.getByTitle('Girar 45° a la izquierda')).toBeInTheDocument();
    expect(screen.getByTitle('Girar 45° a la derecha')).toBeInTheDocument();

    // Botón de sprint
    const sprintBtn = screen.getByTitle(/Caminar/i);
    expect(sprintBtn).toBeInTheDocument();

    // Al pulsar el botón de sprint, debe alternar el estado en el store
    fireEvent.click(sprintBtn);
    expect(useSpatialStore.getState().touchInput.isSprinting).toBe(true);
  });

  it('debe mostrar el botón contextual de examinar cama cuando el médico está en rango', () => {
    useSpatialStore.setState({ hoveredBedId: 'bed_01' });

    render(<MobileTouchControls />);

    const examBtn = screen.getByRole('button', { name: /Examinar Cama 1/i });
    expect(examBtn).toBeInTheDocument();

    fireEvent.click(examBtn);
    expect(useSpatialStore.getState().isTabletOpen).toBe(true);
    expect(useSpatialStore.getState().activeBedId).toBe('bed_01');
  });

  it('debe renderizar el aviso institucional de orientación horizontal con botones de acción', () => {
    const mockRequestFullscreen = vi.fn();
    render(<LandscapeOrientationNotice onRequestFullscreen={mockRequestFullscreen} />);

    expect(screen.getByText('Orientación Horizontal Requerida')).toBeInTheDocument();
    expect(
      screen.getByText(/Para una experiencia de simulación clínica inmersiva/i)
    ).toBeInTheDocument();

    // Botón de pantalla completa
    const fsBtn = screen.getByRole('button', { name: /Pantalla Completa/i });
    fireEvent.click(fsBtn);
    expect(mockRequestFullscreen).toHaveBeenCalledTimes(1);

    // Botón de retorno al catálogo
    const catalogBtn = screen.getByRole('button', { name: /Volver al Catálogo/i });
    fireEvent.click(catalogBtn);
    expect(mockNavigate).toHaveBeenCalledWith('/cases');
  });

  it('debe registrar el movimiento táctil en el store', () => {
    useSpatialStore.getState().setTouchMove(0.75, 0.5);
    const touch = useSpatialStore.getState().touchInput;
    expect(touch.moveX).toBe(0.75);
    expect(touch.moveY).toBe(0.5);

    // Acumulación y consumo de rotación táctil
    useSpatialStore.getState().addTouchLookDelta(15, -10);
    const delta = useSpatialStore.getState().consumeTouchLookDelta();
    expect(delta.dx).toBe(15);
    expect(delta.dy).toBe(-10);

    // Debe haberse reseteado a 0 tras consumir
    const emptyDelta = useSpatialStore.getState().consumeTouchLookDelta();
    expect(emptyDelta.dx).toBe(0);
    expect(emptyDelta.dy).toBe(0);
  });
});
