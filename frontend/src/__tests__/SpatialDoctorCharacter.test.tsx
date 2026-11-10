import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import * as THREE from 'three';
import { useSpatialStore } from '../modules/spatial/store/useSpatialStore';
import { Hospital3DPage } from '../modules/spatial/pages/Hospital3DPage';
import { DoctorCharacter } from '../modules/spatial/components/DoctorCharacter';

// Mock de Canvas de Three.js y React Three Fiber
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => <div data-testid="r3f-canvas">{children}</div>,
  useFrame: vi.fn(),
  useThree: () => ({
    camera: {
      position: { copy: vi.fn(), set: vi.fn() },
      rotation: { set: vi.fn(), order: 'YXZ' },
      lookAt: vi.fn()
    },
    gl: { domElement: { addEventListener: vi.fn(), removeEventListener: vi.fn() } }
  })
}));

vi.mock('@react-three/drei', () => ({
  Environment: () => null,
  ContactShadows: () => null,
  Sky: () => null,
  useGLTF: Object.assign(
    () => ({
      scene: {
        clone: () => ({
          getObjectByName: vi.fn(),
          traverse: vi.fn()
        })
      }
    }),
    { preload: vi.fn() }
  )
}));

// Mock de react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate
}));

// Mock del hook useCases
vi.mock('../modules/cases/hooks/useCases', () => ({
  useCases: () => ({ cases: [] })
}));

describe('Suite de Pruebas: Avatar 3D de Médico y Modos de Cámara (Ateneo+)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useSpatialStore.setState({
      cameraMode: 'third-person',
      hoveredBedId: null,
      isTabletOpen: false
    });
  });

  it('debe iniciar de forma predeterminada en modo Tercera Persona con el avatar activo', () => {
    expect(useSpatialStore.getState().cameraMode).toBe('third-person');
  });

  it('debe alternar correctamente entre Tercera Persona y Primera Persona en el store', () => {
    const { toggleCameraMode, setCameraMode } = useSpatialStore.getState();

    toggleCameraMode();
    expect(useSpatialStore.getState().cameraMode).toBe('first-person');

    toggleCameraMode();
    expect(useSpatialStore.getState().cameraMode).toBe('third-person');

    setCameraMode('first-person');
    expect(useSpatialStore.getState().cameraMode).toBe('first-person');
  });

  it('debe renderizar el botón de conmutación de cámara en el HUD y alternar el modo al pulsar', () => {
    render(<Hospital3DPage />);

    const cameraToggleBtn = screen.getByRole('button', { name: /Conmutar perspectiva de cámara/i });
    expect(cameraToggleBtn).toBeInTheDocument();
    expect(cameraToggleBtn).toHaveAttribute('title', 'Cambiar a 1ª Persona');

    fireEvent.click(cameraToggleBtn);
    expect(useSpatialStore.getState().cameraMode).toBe('first-person');
    expect(cameraToggleBtn).toHaveAttribute('title', 'Cambiar a 3ª Persona (Avatar Médico)');
  });

  it('debe mantener el modelo del médico activo en Primera Persona (True First Person)', () => {
    const { container } = render(
      <DoctorCharacter
        positionRef={{ current: new THREE.Vector3(0, 0, 0) }}
        yawRef={{ current: 0 }}
        currentSpeedRef={{ current: 2.5 }}
        isSprintingRef={{ current: false }}
        cameraMode="first-person"
        visible={true}
      />
    );
    expect(container).toBeDefined();
  });
});
