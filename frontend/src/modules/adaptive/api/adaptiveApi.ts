import httpClient from '../../../core/http/httpClient';
import type { ZDPRecommendation, KnowledgeStateResponse, KSTTopology } from '../../../types';

/**
 * Servicio de Red del Currículo Adaptativo (KST & BKT)
 */
export const adaptiveApi = {
  async getNextCase(studentId?: string): Promise<ZDPRecommendation> {
    const query = studentId ? `?student_id=${encodeURIComponent(studentId)}` : '';
    const res = await httpClient.get<ZDPRecommendation>(`/api/adaptive/next-case${query}`);
    return res.data;
  },

  async getKnowledgeState(studentId?: string): Promise<KnowledgeStateResponse> {
    const query = studentId ? `?student_id=${encodeURIComponent(studentId)}` : '';
    const res = await httpClient.get<KnowledgeStateResponse>(`/api/adaptive/knowledge-state${query}`);
    return res.data;
  },

  async getLearningPath(studentId?: string): Promise<unknown> {
    const query = studentId ? `?student_id=${encodeURIComponent(studentId)}` : '';
    const res = await httpClient.get<unknown>(`/api/adaptive/learning-path${query}`);
    return res.data;
  },

  async getTopology(): Promise<KSTTopology> {
    const res = await httpClient.get<KSTTopology>('/api/adaptive/topology');
    return res.data;
  }
};

export default adaptiveApi;
