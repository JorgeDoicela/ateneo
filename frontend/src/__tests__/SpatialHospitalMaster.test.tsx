import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { useSpatialStore } from '../modules/spatial/store/useSpatialStore';
import { BedInteractionBadge } from '../modules/spatial/components/BedInteractionBadge';
import { ClinicalBedsideTablet } from '../modules/spatial/components/ClinicalBedsideTablet';

// Mock de react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate
}));

// Mock de useCases
vi.mock('../modules/cases/hooks/useCases', () => ({
  useCases: () => ({
    cases: [
      {
        id: 'case_preeclampsia_01',
        titulo: 'Preeclampsia con Criterios de Severidad',
        enunciado: 'Paciente primigesta de 34 semanas con PA 165/110 mmHg y proteinuria.',
        pregunta: '¿Cuál es el esquema de neuroprotección con sulfato de magnesio según la GPC?',
        signos_alarma: true,
        dificultad: 'Avanzado'
      }
    ]
  })
}));

// Mock de @react-three/drei Html
vi.mock('@react-three/drei', () => ({
  Html: ({ children }: { children: React.ReactNode }) => <div data-testid="drei-html">{children}</div>,
  useGLTF: () => ({ scene: { clone: () => ({}) } }),
  Sky: () => null
}));

describe('Suite de Pruebas: Simulador Hospitalario 3D Master (Ateneo+)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useSpatialStore.setState({
      playerPosition: [0, 1.68, 4],
      playerRotation: 0,
      hoveredBedId: null,
      activeBedId: null,
      isTabletOpen: false,
      beds: useSpatialStore.getState().beds.map((b) => ({
        ...b,
        isSolved: false,
        score: undefined,
        urgency: b.id === 'bed_01' || b.id === 'bed_02' ? 'codigo_rojo' : b.urgency,
        label: b.id === 'bed_01' ? 'Box de Choque 1 — Obstetricia' : b.label
      }))
    });
  });

  it('debe inicializar el pabellón con 6 camas reglamentarias y Códigos Rojos activos', () => {
    const beds = useSpatialStore.getState().beds;
    expect(beds).toHaveLength(6);
    expect(beds[0].urgency).toBe('codigo_rojo');
    expect(beds[1].urgency).toBe('codigo_rojo');
    expect(beds[0].vitals.hr).toBe(88);
  });

  it('debe sincronizar los títulos y urgencias de los casos clínicos normados', () => {
    const mockCases = [
      {
        id: 'case_preeclampsia_01',
        titulo: 'Preeclampsia Severa GPC',
        pregunta: 'Tratamiento',
        signos_alarma: true,
        dificultad: 'Avanzado' as const
      }
    ];

    useSpatialStore.getState().syncCasesWithBeds(mockCases as any);
    const bed1 = useSpatialStore.getState().beds.find((b) => b.id === 'bed_01');
    expect(bed1?.label).toBe('Preeclampsia Severa GPC');
    expect(bed1?.urgency).toBe('codigo_rojo');
  });

  it('debe registrar la resolución formativa de una cama con su puntaje', () => {
    useSpatialStore.getState().markBedAsSolved('case_preeclampsia_01', 9.5);
    const bed1 = useSpatialStore.getState().beds.find((b) => b.id === 'bed_01');
    expect(bed1?.isSolved).toBe(true);
    expect(bed1?.score).toBe(9.5);
  });

  it('debe renderizar la micro-tarjeta diegética HTML sobre la cama', () => {
    const bed = useSpatialStore.getState().beds[0];
    const handleClick = vi.fn();

    render(<BedInteractionBadge bed={bed} onClick={handleClick} />);

    expect(screen.getByText(/Cama 1/)).toBeInTheDocument();
    expect(screen.getByText(/CÓDIGO ROJO/)).toBeInTheDocument();

    const button = screen.getByRole('button', { name: /Examinar Cama 1/i });
    fireEvent.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('debe abrir la tableta de telemetría y mostrar signos vitales de la cama inspeccionada', () => {
    useSpatialStore.getState().openBedInspection('bed_01');
    expect(useSpatialStore.getState().isTabletOpen).toBe(true);
    expect(useSpatialStore.getState().activeBedId).toBe('bed_01');

    render(<ClinicalBedsideTablet />);

    expect(screen.getByText(/Cama 1:/)).toBeInTheDocument();
    expect(screen.getByText('88')).toBeInTheDocument(); // FC
    expect(screen.getByText('165/110')).toBeInTheDocument(); // PA
    expect(screen.getByText(/Paciente primigesta de 34 semanas/)).toBeInTheDocument();

    // Botón de resolución
    const solveBtn = screen.getByRole('button', { name: /Iniciar Resolución Diagnóstica/i });
    fireEvent.click(solveBtn);
    expect(mockNavigate).toHaveBeenCalledWith('/cases/case_preeclampsia_01');
    expect(useSpatialStore.getState().isTabletOpen).toBe(false);
  });
});
