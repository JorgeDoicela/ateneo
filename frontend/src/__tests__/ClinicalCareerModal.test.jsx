import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ClinicalCareerModal from '../modules/gamification/components/ClinicalCareerModal';
import { gamificationApi } from '../modules/gamification/api/gamificationApi';

describe('Componente ClinicalCareerModal (Carrera Formativa e Hitos)', () => {
  const mockProfile = {
    user_id: 'usr_alumno_001',
    puntos_xp: 350,
    nivel_actual: 2,
    titulo_rango: 'Externo de Medicina',
    casos_resueltos: 3,
    racha_dias: 2,
    xp_actual_en_nivel: 50,
    xp_requerido_siguiente_nivel: 400,
    porcentaje_avance_nivel: 12.5,
    siguiente_rango: 'Interno Rotativo',
    total_logros_desbloqueados: 2,
    total_logros_disponibles: 8
  };

  const mockAchievements = [
    {
      achievement_id: 'iniciacion_clinica',
      codigo: 'ACH_INIT_01',
      titulo: 'Iniciación Clínica',
      descripcion: 'Completar la primera simulación diagnóstica.',
      categoria: 'diagnostico',
      icono: 'Stethoscope',
      puntos_xp: 50,
      desbloqueado: true,
      desbloqueado_en: '2026-10-15T10:00:00Z',
      progreso_actual: 1.0,
      meta: 1.0,
      porcentaje: 100.0
    },
    {
      achievement_id: 'apego_gpc_excelente',
      codigo: 'ACH_GPC_02',
      titulo: 'Apego Normativo Estricto',
      descripcion: 'Obtener calificación >= 9.0.',
      categoria: 'excelencia',
      icono: 'Award',
      puntos_xp: 100,
      desbloqueado: false,
      desbloqueado_en: null,
      progreso_actual: 0.0,
      meta: 9.0,
      porcentaje: 0.0
    }
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('no debe renderizar nada si isOpen es false', () => {
    const { container } = render(<ClinicalCareerModal isOpen={false} onClose={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it('debe renderizar el rango, nivel, XP y los hitos clínicos cuando isOpen es true', async () => {
    vi.spyOn(gamificationApi, 'getProfile').mockResolvedValue(mockProfile);
    vi.spyOn(gamificationApi, 'getAchievements').mockResolvedValue(mockAchievements);

    render(<ClinicalCareerModal isOpen={true} onClose={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText('Externo de Medicina')).toBeInTheDocument();
      expect(screen.getByText('Nivel 2')).toBeInTheDocument();
      expect(screen.getByText(/350/)).toBeInTheDocument();
    });

    expect(screen.getByText('Iniciación Clínica')).toBeInTheDocument();
    expect(screen.getByText('Apego Normativo Estricto')).toBeInTheDocument();
    expect(screen.getByText('Desbloqueado')).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('debe invocar onClose al pulsar el botón de cierre', async () => {
    vi.spyOn(gamificationApi, 'getProfile').mockResolvedValue(mockProfile);
    vi.spyOn(gamificationApi, 'getAchievements').mockResolvedValue(mockAchievements);
    const mockClose = vi.fn();

    render(<ClinicalCareerModal isOpen={true} onClose={mockClose} />);

    await waitFor(() => {
      expect(screen.getByText('Externo de Medicina')).toBeInTheDocument();
    });

    const closeBtn = screen.getByTitle('Cerrar modal');
    fireEvent.click(closeBtn);
    expect(mockClose).toHaveBeenCalledTimes(1);
  });
});
