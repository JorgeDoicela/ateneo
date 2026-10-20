import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ReasoningTrends from '../modules/analytics/components/ReasoningTrends';

describe('Componente ReasoningTrends (Progresión Longitudinal y Filtro GPC Ateneo+)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockTrendsData = {
    total_evaluaciones: 4,
    promedio_general: 8.2,
    punto_debil_principal: 'Dosificación exacta de antibióticos y fluidoterapia pediátrica.',
    progreso_por_gpc: {
      'GPC_EHIRN2019': { guia: 'GPC_EHIRN2019', evaluaciones: 2, scores: [7.5, 8.5], promedio: 8.0 },
      'HIPERTENSION': { guia: 'HIPERTENSION', evaluaciones: 2, scores: [8.0, 9.0], promedio: 8.5 }
    },
    puntuaciones_tiempo: [
      { id: 1, timestamp: '2026-08-01T10:00:00', fecha_formateada: '01/08', score: 7.5, guia_asociada: 'GPC_EHIRN2019', case_title: 'EHIRN Caso 1' },
      { id: 2, timestamp: '2026-08-03T14:30:00', fecha_formateada: '03/08', score: 8.0, guia_asociada: 'HIPERTENSION', case_title: 'Crisis Hipertensiva' },
      { id: 3, timestamp: '2026-08-05T09:15:00', fecha_formateada: '05/08', score: 8.5, guia_asociada: 'GPC_EHIRN2019', case_title: 'EHIRN Caso 2' },
      { id: 4, timestamp: '2026-08-07T11:20:00', fecha_formateada: '07/08', score: 9.0, guia_asociada: 'HIPERTENSION', case_title: 'Hipertensión Control' }
    ],
    omisiones_mas_frecuentes: [
      { patron: 'Monitoreo horario de presión arterial', frecuencia: 2 }
    ],
    radar_competencias: [
      { eje: 'diagnóstico', label: 'Diagnóstico', score: 85, brechas: 1 },
      { eje: 'tratamiento', label: 'Tratamiento', score: 70, brechas: 2 }
    ]
  };

  it('debe renderizar el selector desplegable con diseño Ateneo+ y permitir seleccionar una GPC', async () => {
    globalThis.fetch = vi.fn().mockImplementation((url: string | URL | Request) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('trends')) {
        return Promise.resolve(new Response(JSON.stringify(mockTrendsData), { status: 200 }));
      }
      return Promise.resolve(new Response(null, { status: 404 }));
    });

    render(<ReasoningTrends />);

    // Esperar a que se carguen los datos
    await waitFor(() => {
      expect(screen.getByText(/Evolución de Calificaciones por GPC/i)).toBeInTheDocument();
    });

    // El botón del filtro debe mostrar "Todas las GPCs" por defecto
    const filterButton = screen.getByRole('button', { name: /Filtrar:\s*Todas las GPCs/i });
    expect(filterButton).toBeInTheDocument();

    // Al hacer clic, debe abrirse el menú flotante con las opciones
    fireEvent.click(filterButton);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /^GPC_EHIRN2019$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^HIPERTENSION$/i })).toBeInTheDocument();
    });

    // Seleccionar una GPC específica
    const gpcOption = screen.getByRole('button', { name: /^GPC_EHIRN2019$/i });
    fireEvent.click(gpcOption);

    // El botón debe actualizar su etiqueta al valor seleccionado y el menú cerrarse
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Filtrar:\s*GPC_EHIRN2019/i })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /^HIPERTENSION$/i })).not.toBeInTheDocument();
    });
  });

  it('debe cumplir con la regla de oro: CERO EMOJIS en la vista analítica', async () => {
    globalThis.fetch = vi.fn().mockImplementation((url: string | URL | Request) => {
      const urlStr = typeof url === 'string' ? url : url.toString();
      if (urlStr.includes('trends')) {
        return Promise.resolve(new Response(JSON.stringify(mockTrendsData), { status: 200 }));
      }
      return Promise.resolve(new Response(null, { status: 404 }));
    });

    const { container } = render(<ReasoningTrends />);

    await waitFor(() => {
      expect(screen.getByText(/Evolución de Calificaciones por GPC/i)).toBeInTheDocument();
    });

    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    expect(emojiRegex.test(container.textContent || '')).toBe(false);
  });
});
