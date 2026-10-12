import httpClient from '../../../core/http/httpClient';
import type { CoordinatorAnalyticsData, IbfCohortData, ScientificBenchmarkPayload } from '../../../types';

/**
 * Servicio de Red para Analítica Institucional, IBF y Benchmarking
 */
export const analyticsApi = {
  async getTrends(): Promise<unknown> {
    const res = await httpClient.get<unknown>('/api/history/trends');
    return res.data;
  },

  async getCoordinatorAnalytics(): Promise<CoordinatorAnalyticsData> {
    const res = await httpClient.get<CoordinatorAnalyticsData>('/api/history/coordinator-analytics');
    return res.data;
  },

  async getIbfCohort(): Promise<IbfCohortData> {
    const res = await httpClient.get<IbfCohortData>('/api/history/ibf-cohort');
    return res.data;
  },

  async getScientificBenchmark(): Promise<ScientificBenchmarkPayload> {
    const res = await httpClient.get<ScientificBenchmarkPayload>('/api/evaluate/benchmark-scientific');
    return res.data;
  },

  async getFaithfulnessBenchmark(): Promise<unknown> {
    const res = await httpClient.get<unknown>('/api/history/faithfulness-benchmark');
    return res.data;
  },

  async getHistory(): Promise<unknown> {
    const res = await httpClient.get<unknown>('/api/history');
    return res.data;
  },

  async recordEvent(event: import('../../../types').LearningActivityEvent): Promise<import('../../../types').LearningActivityEventRecord> {
    const res = await httpClient.post<import('../../../types').LearningActivityEventRecord>('/api/analytics/events', event);
    return res.data;
  },

  async getEvents(params?: { user_id?: string; case_id?: string; limit?: number }): Promise<import('../../../types').LearningActivityEventRecord[]> {
    const query = new URLSearchParams();
    if (params?.user_id) query.append('user_id', params.user_id);
    if (params?.case_id) query.append('case_id', params.case_id);
    if (params?.limit) query.append('limit', String(params.limit));
    const url = `/api/analytics/events${query.toString() ? `?${query.toString()}` : ''}`;
    const res = await httpClient.get<import('../../../types').LearningActivityEventRecord[]>(url);
    return res.data;
  }
};

export default analyticsApi;
