import httpClient from '../../../core/http/httpClient';
import type {
  PrescriptiveStudyPlan,
  CompleteTaskResponse,
} from '../types';

export const studyPlanApi = {
  /**
   * Consulta el Plan de Estudio Prescriptivo activo para el estudiante autenticado.
   */
  async getMyActivePlan(): Promise<PrescriptiveStudyPlan | null> {
    try {
      const res = await httpClient.get<PrescriptiveStudyPlan | null>('/api/study-plans/me');
      return res.data;
    } catch (err: unknown) {
      // 404 o sin plan activo
      return null;
    }
  },

  /**
   * Consulta los detalles de un plan específico por ID.
   */
  async getPlanById(planId: string): Promise<PrescriptiveStudyPlan> {
    const res = await httpClient.get<PrescriptiveStudyPlan>(`/api/study-plans/${encodeURIComponent(planId)}`);
    return res.data;
  },

  /**
   * Marca una tarea pedagógica como completada y actualiza el progreso porcentual del plan.
   */
  async completeTask(taskId: number): Promise<CompleteTaskResponse> {
    const res = await httpClient.post<CompleteTaskResponse>(`/api/study-plans/tasks/${encodeURIComponent(taskId)}/complete`);
    return res.data;
  },
};
