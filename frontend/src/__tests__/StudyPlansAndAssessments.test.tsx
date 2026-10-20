import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

import { HakeGainBadge } from '../modules/assessments/components/HakeGainBadge';
import { PrescriptivePlanCard } from '../modules/study_plans/components/PrescriptivePlanCard';
import type { PrescriptiveStudyPlan } from '../modules/study_plans/types';
import httpClient from '../core/http/httpClient';
import { assessmentApi } from '../modules/assessments/api/assessmentApi';
import { studyPlanApi } from '../modules/study_plans/api/studyPlanApi';

// Mock del cliente HTTP core
vi.mock('../core/http/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('Componente HakeGainBadge (Psicometría y Ganancia de Hake)', () => {
  it('renderiza correctamente Ganancia Alta (g >= 0.70)', () => {
    render(<HakeGainBadge gain={0.82} category="Ganancia Alta (g >= 0.70)" />);
    expect(screen.getByText(/g = 0.82/i)).toBeInTheDocument();
    expect(screen.getByText(/Ganancia Alta/i)).toBeInTheDocument();
  });

  it('renderiza correctamente Ganancia Media (0.30 <= g < 0.70)', () => {
    render(<HakeGainBadge gain={0.45} />);
    expect(screen.getByText(/g = 0.45/i)).toBeInTheDocument();
    expect(screen.getByText(/Ganancia Media/i)).toBeInTheDocument();
  });

  it('renderiza correctamente Ganancia Baja (g < 0.30)', () => {
    render(<HakeGainBadge gain={0.15} />);
    expect(screen.getByText(/g = 0.15/i)).toBeInTheDocument();
    expect(screen.getByText(/Ganancia Baja/i)).toBeInTheDocument();
  });

  it('renderiza Regresión Clínica cuando g es negativo', () => {
    render(<HakeGainBadge gain={-0.12} />);
    expect(screen.getByText(/g = -0.12/i)).toBeInTheDocument();
    expect(screen.getByText(/Regresión Clínica/i)).toBeInTheDocument();
  });

  it('renderiza mensaje neutro cuando no hay post-test vinculado', () => {
    render(<HakeGainBadge gain={null} />);
    expect(screen.getByText(/Sin Post-Test vinculado/i)).toBeInTheDocument();
  });
});

describe('Componente PrescriptivePlanCard (Plan de Estudio Heurístico)', () => {
  const mockPlan: PrescriptiveStudyPlan = {
    id: 'plan_test_123',
    user_id: 'usr_alumno_001',
    source_assessment_id: 'eval_pre_999',
    title: 'Plan de Refuerzo Clínico Prioritario',
    diagnosis_summary: 'Brecha detectada en manejo de Preeclampsia severa y esquema Zuspan.',
    target_duration_days: 7,
    progress_percentage: 33.3,
    status: 'active',
    created_at: '2026-10-20T12:00:00Z',
    tasks: [
      {
        id: 101,
        plan_id: 'plan_test_123',
        task_type: 'gpc_reading',
        title: 'Lectura Normativa GPC: Trastornos Hipertensivos',
        description: 'Estudio de impregnación con Sulfato de Magnesio.',
        resource_reference: 'GPC Trastornos Hipertensivos',
        competency_id: 'plan_terapeutico_msp',
        estimated_minutes: 15,
        is_completed: true,
      },
      {
        id: 102,
        plan_id: 'plan_test_123',
        task_type: 'case_simulation',
        title: 'Simulación Práctica: Preeclampsia con Criterios de Severidad',
        description: 'Resolución de caso en ZDP.',
        resource_reference: 'case_preeclampsia_01',
        competency_id: 'plan_terapeutico_msp',
        estimated_minutes: 20,
        is_completed: false,
      },
      {
        id: 103,
        plan_id: 'plan_test_123',
        task_type: 'socratic_review',
        title: 'Debriefing Socrático: Justificación Zuspan',
        description: 'Preguntas reflexivas sobre dosis de carga.',
        resource_reference: 'case_preeclampsia_01',
        competency_id: 'plan_terapeutico_msp',
        estimated_minutes: 10,
        is_completed: false,
      },
    ],
  };

  it('renderiza título, resumen y tareas dosificadas', () => {
    render(<PrescriptivePlanCard plan={mockPlan} />);
    expect(screen.getByText('Plan de Refuerzo Clínico Prioritario')).toBeInTheDocument();
    expect(screen.getByText(/Brecha detectada en manejo de Preeclampsia/i)).toBeInTheDocument();
    expect(screen.getByText('1 de 3 completadas')).toBeInTheDocument();
    expect(screen.getByText('33%')).toBeInTheDocument();
    expect(screen.getByText('Lectura Normativa GPC: Trastornos Hipertensivos')).toBeInTheDocument();
    expect(screen.getByText('Simulación Práctica: Preeclampsia con Criterios de Severidad')).toBeInTheDocument();
  });

  it('permite marcar una tarea pendiente como completada al hacer clic', () => {
    const handleComplete = vi.fn();
    render(<PrescriptivePlanCard plan={mockPlan} onCompleteTask={handleComplete} />);

    // Buscar los botones de checklist (hay 3 tareas)
    const taskButtons = screen.getAllByRole('button', { name: /Marcar como completada/i });
    expect(taskButtons.length).toBe(2);

    fireEvent.click(taskButtons[0]);
    expect(handleComplete).toHaveBeenCalledWith(102);
  });

  it('dispara onStartPostTest con el ID del Pre-Test al presionar el botón de Post-Test', () => {
    const handleStartPostTest = vi.fn();
    render(<PrescriptivePlanCard plan={mockPlan} onStartPostTest={handleStartPostTest} />);

    const postTestBtn = screen.getByRole('button', { name: /Iniciar Post-Test Isomórfico/i });
    expect(postTestBtn).toBeInTheDocument();

    fireEvent.click(postTestBtn);
    expect(handleStartPostTest).toHaveBeenCalledWith('eval_pre_999');
  });
});

describe('Servicios de Red API (assessmentApi y studyPlanApi)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('assessmentApi.startPreTest invoca el endpoint POST correspondiente', async () => {
    const mockData = { id: 'eval_pre_1', assessment_type: 'pre_test' };
    vi.mocked(httpClient.post).mockResolvedValueOnce({ data: mockData, status: 201, ok: true });

    const res = await assessmentApi.startPreTest('Obstetricia', 2);
    expect(httpClient.post).toHaveBeenCalledWith('/api/assessments/pre-test/start', {
      specialty_scope: 'Obstetricia',
      num_cases: 2,
    });
    expect(res).toEqual(mockData);
  });

  it('assessmentApi.startPostTest invoca el endpoint POST con pre_test_id', async () => {
    const mockData = { id: 'eval_post_1', assessment_type: 'post_test', related_assessment_id: 'eval_pre_1' };
    vi.mocked(httpClient.post).mockResolvedValueOnce({ data: mockData, status: 201, ok: true });

    const res = await assessmentApi.startPostTest('eval_pre_1');
    expect(httpClient.post).toHaveBeenCalledWith('/api/assessments/post-test/start', {
      pre_test_id: 'eval_pre_1',
    });
    expect(res).toEqual(mockData);
  });

  it('studyPlanApi.completeTask invoca el endpoint POST con task_id', async () => {
    const mockData = { task_id: 102, is_completed: true, progress_percentage: 66.7 };
    vi.mocked(httpClient.post).mockResolvedValueOnce({ data: mockData, status: 200, ok: true });

    const res = await studyPlanApi.completeTask(102);
    expect(httpClient.post).toHaveBeenCalledWith('/api/study-plans/tasks/102/complete');
    expect(res).toEqual(mockData);
  });
});
