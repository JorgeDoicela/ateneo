import httpClient from '../../../core/http/httpClient';
import type { GamificationProfile, UserAchievementProgress, CareerLevelInfo } from '../types';

export const gamificationApi = {
  async getProfile(): Promise<GamificationProfile> {
    const res = await httpClient.get<GamificationProfile>('/api/gamification/profile');
    return res.data;
  },

  async getAchievements(): Promise<UserAchievementProgress[]> {
    const res = await httpClient.get<UserAchievementProgress[]>('/api/gamification/achievements');
    return res.data;
  },

  async getLevels(): Promise<{ levels: CareerLevelInfo[] }> {
    const res = await httpClient.get<{ levels: CareerLevelInfo[] }>('/api/gamification/levels');
    return res.data;
  }
};

export default gamificationApi;
