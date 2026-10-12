import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAuthStore } from '../core/stores/useAuthStore';
import { authApi } from '../modules/auth/api/authApi';
import type { LoginResponse } from '../types';

vi.mock('../modules/auth/api/authApi', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    getMe: vi.fn(),
  },
}));

describe('useAuthStore - Ciclo de Vida y Revocación de Sesión', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    useAuthStore.setState({ user: null, token: null, loading: false });
  });

  it('debe almacenar token y usuario tras login exitoso', async () => {
    const mockResponse: LoginResponse = {
      access_token: 'jwt_token_simulado_test',
      token_type: 'bearer',
      user: {
        id: 'usr_001',
        email: 'alumno@ateneo.edu.ec',
        nombre: 'Estudiante Test',
        rol: 'alumno' as any,
        tenant_id: 'tenant_default',
      },
    };

    vi.mocked(authApi.login).mockResolvedValueOnce(mockResponse);

    const user = await useAuthStore.getState().login('alumno@ateneo.edu.ec', 'Password123!');
    expect(user.email).toBe('alumno@ateneo.edu.ec');
    expect(useAuthStore.getState().token).toBe('jwt_token_simulado_test');
    expect(localStorage.getItem('ateneo_token')).toBe('jwt_token_simulado_test');
  });

  it('debe invocar authApi.logout() y purgar almacenamiento local al cerrar sesión', async () => {
    useAuthStore.setState({
      token: 'jwt_activo_test',
      user: {
        id: 'usr_001',
        email: 'alumno@ateneo.edu.ec',
        nombre: 'Estudiante Test',
        rol: 'alumno' as any,
      },
    });
    localStorage.setItem('ateneo_token', 'jwt_activo_test');

    vi.mocked(authApi.logout).mockResolvedValueOnce({ mensaje: 'Sesión cerrada y token revocado exitosamente' });

    await useAuthStore.getState().logout();

    expect(authApi.logout).toHaveBeenCalledTimes(1);
    expect(useAuthStore.getState().token).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
    expect(localStorage.getItem('ateneo_token')).toBeNull();
  });
});
