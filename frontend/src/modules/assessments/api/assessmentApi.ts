import httpClient from '../../../core/http/httpClient';
import type {
  DiagnosticAssessment,
  AssessmentSummaryReport,
} from '../types';

export interface SubmitAnswerPayload {
  item_id: number;
  student_answer: string;
}

export const assessmentApi = {
  /**
   * Inicia una sesión de Pre-Test diagnóstico seleccionando casos basales.
   * Por defecto aplica la Batería Troncal CACES balanceada (4 troncales formativas).
   */
  async startPreTest(
    specialtyScope: string = 'Batería Troncal CACES (Multidisciplinar)',
    numCases: number = 4
  ): Promise<DiagnosticAssessment> {
    const res = await httpClient.post<DiagnosticAssessment>('/api/assessments/pre-test/start', {
      specialty_scope: specialtyScope,
      num_cases: numCases,
    });
    return res.data;
  },

  /**
   * Inicia una sesión de Post-Test isomórfica a partir de un Pre-Test previo completado.
   */
  async startPostTest(preTestId: string): Promise<DiagnosticAssessment> {
    const res = await httpClient.post<DiagnosticAssessment>('/api/assessments/post-test/start', {
      pre_test_id: preTestId,
    });
    return res.data;
  },

  /**
   * Envía las respuestas del estudiante para calificar la evaluación y obtener el reporte formativo.
   * Si es Pre-Test: sintetiza el plan prescriptivo.
   * Si es Post-Test: calcula la Ganancia de Hake (g).
   */
  async submitAssessment(assessmentId: string, answers: SubmitAnswerPayload[]): Promise<AssessmentSummaryReport> {
    const res = await httpClient.post<AssessmentSummaryReport>(`/api/assessments/${encodeURIComponent(assessmentId)}/submit`, {
      assessment_id: assessmentId,
      answers,
    });
    return res.data;
  },

  /**
   * Consulta los detalles y reactivos de una evaluación diagnóstica específica.
   */
  async getAssessment(assessmentId: string): Promise<DiagnosticAssessment> {
    const res = await httpClient.get<DiagnosticAssessment>(`/api/assessments/${encodeURIComponent(assessmentId)}`);
    return res.data;
  },

  /**
   * Consulta el historial longitudinal de evaluaciones del estudiante autenticado.
   */
  async getMyHistory(): Promise<DiagnosticAssessment[]> {
    const res = await httpClient.get<DiagnosticAssessment[]>('/api/assessments/history/me');
    return res.data;
  },
};
