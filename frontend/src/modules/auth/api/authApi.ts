import httpClient from '../../../core/http/httpClient';
import { 
  LoginResponseSchema, 
  UserSchema, 
  RegisterResponseSchema 
} from '../../../core/validation/schemas';
import type { 
  LoginResponse, 
  User, 
  RegisterRequest, 
  RegisterResponse,
  MagicLinkCreatePayload,
  MagicLinkBatchCreatePayload,
  MagicLinkRecord,
  MagicLinkConsumePayload,
  MagicLinkConsumeResult,
  MagicLinkVerifyResult
} from '../../../types';

/**
 * Servicio de Red de Autenticación y RBAC con Validación Zod
 */
export const authApi = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const res = await httpClient.post<unknown>('/api/auth/login', { email, password });
    const parsed = LoginResponseSchema.safeParse(res.data);
    if (!parsed.success) {
      console.warn('Discrepancia en contrato de login:', parsed.error.issues);
      return res.data as LoginResponse;
    }
    return parsed.data as LoginResponse;
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const res = await httpClient.post<unknown>('/api/auth/register', data);
    const parsed = RegisterResponseSchema.safeParse(res.data);
    if (!parsed.success) {
      console.warn('Discrepancia en contrato de registro:', parsed.error.issues);
      return res.data as RegisterResponse;
    }
    return parsed.data as RegisterResponse;
  },

  async getMe(): Promise<User> {
    const res = await httpClient.get<unknown>('/api/auth/me');
    const parsed = UserSchema.safeParse(res.data);
    if (!parsed.success) {
      console.warn('Discrepancia en contrato de usuario actual:', parsed.error.issues);
      return res.data as User;
    }
    return parsed.data as User;
  },

  async getUsers(): Promise<User[]> {
    const res = await httpClient.get<User[]>('/api/auth/users');
    return res.data;
  },

  async logout(): Promise<{ mensaje: string }> {
    const res = await httpClient.post<{ mensaje: string }>('/api/auth/logout');
    return res.data;
  },

  async createMagicLink(data: MagicLinkCreatePayload): Promise<MagicLinkRecord> {
    const res = await httpClient.post<MagicLinkRecord>('/api/auth/magic-links', data);
    return res.data;
  },

  async createMagicLinksBatch(data: MagicLinkBatchCreatePayload): Promise<MagicLinkRecord[]> {
    const res = await httpClient.post<MagicLinkRecord[]>('/api/auth/magic-links/batch', data);
    return res.data;
  },

  async listMagicLinks(): Promise<MagicLinkRecord[]> {
    const res = await httpClient.get<MagicLinkRecord[]>('/api/auth/magic-links');
    return res.data;
  },

  async revokeMagicLink(linkId: string): Promise<{ mensaje: string }> {
    const res = await httpClient.delete<{ mensaje: string }>(`/api/auth/magic-links/${linkId}`);
    return res.data;
  },

  async purgeMagicLink(linkId: string): Promise<{ mensaje: string }> {
    const res = await httpClient.delete<{ mensaje: string }>(`/api/auth/magic-links/${linkId}/purge`);
    return res.data;
  },

  async purgeRevokedLinks(): Promise<{ mensaje: string; eliminados: number }> {
    const res = await httpClient.post<{ mensaje: string; eliminados: number }>('/api/auth/magic-links/purge-revoked');
    return res.data;
  },

  async verifyMagicLink(token: string): Promise<MagicLinkVerifyResult> {
    const res = await httpClient.get<MagicLinkVerifyResult>(`/api/auth/magic-links/verify?token=${encodeURIComponent(token)}`);
    return res.data;
  },

  async consumeMagicLink(data: MagicLinkConsumePayload): Promise<MagicLinkConsumeResult> {
    const res = await httpClient.post<MagicLinkConsumeResult>('/api/auth/magic-links/consume', data);
    return res.data;
  }
};


export default authApi;
