import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import MagicLogin from '../modules/auth/pages/MagicLogin';
import MagicLinkGeneratorCard from '../modules/admin/components/MagicLinkGeneratorCard';
import authApi from '../modules/auth/api/authApi';
import useAuthStore from '../core/stores/useAuthStore';

// Mocks de red y stores
vi.mock('../modules/auth/api/authApi', () => ({
  default: {
    consumeMagicLink: vi.fn(),
    createMagicLink: vi.fn(),
    listMagicLinks: vi.fn(),
    revokeMagicLink: vi.fn(),
  },
  authApi: {
    consumeMagicLink: vi.fn(),
    createMagicLink: vi.fn(),
    listMagicLinks: vi.fn(),
    revokeMagicLink: vi.fn(),
  },
}));

describe('Suite de Pruebas: Magic Links e Invitaciones Configurables (Ateneo+)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({ user: null, token: null, loading: false });
  });

  it('debe canjear automáticamente un Magic Link nominativo y redirigir al target_path', async () => {
    const mockUser = {
      id: 'usr_docente_01',
      email: 'docente.evaluador@ateneo.edu.ec',
      nombre: 'Dr. Evaluador Externo',
      rol: 'docente' as const,
      tenant_id: 'tenant_default',
    };

    vi.mocked(authApi.consumeMagicLink).mockResolvedValueOnce({
      access_token: 'mock_jwt_token_123',
      token_type: 'bearer',
      target_path: '/cases/case_preeclampsia_01',
      user: mockUser,
    });

    render(
      <MemoryRouter initialEntries={['/auth/magic-login?token=valid_token_abc']}>
        <Routes>
          <Route path="/auth/magic-login" element={<MagicLogin />} />
          <Route path="/cases/case_preeclampsia_01" element={<div>Destino: Preeclampsia</div>} />
        </Routes>
      </MemoryRouter>
    );

    // Debe mostrar inicialmente el indicador de verificación
    expect(screen.getByText(/Verificando credenciales de acceso/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(authApi.consumeMagicLink).toHaveBeenCalledWith({ token: 'valid_token_abc' });
    });

    // Debe haber autenticado en useAuthStore
    await waitFor(() => {
      const state = useAuthStore.getState();
      expect(Boolean(state.token && state.user)).toBe(true);
      expect(state.token).toBe('mock_jwt_token_123');
      expect(state.user?.email).toBe('docente.evaluador@ateneo.edu.ec');
    });

    // Debe haber redirigido a la ruta de destino clínico
    await waitFor(() => {
      expect(screen.getByText('Destino: Preeclampsia')).toBeInTheDocument();
    });
  });

  it('debe solicitar correo institucional e identidad si el enlace es de cohorte grupal', async () => {
    // Simular error 400 del backend solicitando email
    vi.mocked(authApi.consumeMagicLink).mockRejectedValueOnce({
      response: {
        status: 400,
        data: { detail: 'Este enlace de cohorte requiere ingresar su correo electrónico.' },
      },
    });

    render(
      <MemoryRouter initialEntries={['/auth/magic-login?token=group_token_xyz']}>
        <Routes>
          <Route path="/auth/magic-login" element={<MagicLogin />} />
        </Routes>
      </MemoryRouter>
    );

    // Debe renderizar el formulario de identificación de cohorte
    await waitFor(() => {
      expect(screen.getByText(/Invitación de Cohorte Médica/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Correo Institucional/i)).toBeInTheDocument();
    });

    // Simular canje manual exitoso con datos del alumno
    const mockAlumno = {
      id: 'usr_alumno_invitado',
      email: 'alumno.nuevo@ateneo.edu.ec',
      nombre: 'Carlos Estudiante',
      rol: 'alumno' as const,
      tenant_id: 'tenant_default',
    };

    vi.mocked(authApi.consumeMagicLink).mockResolvedValueOnce({
      access_token: 'mock_jwt_alumno_456',
      token_type: 'bearer',
      target_path: '/cases',
      user: mockAlumno,
    });

    const emailInput = screen.getByLabelText(/Correo Institucional/i);
    fireEvent.change(emailInput, { target: { value: 'alumno.nuevo@ateneo.edu.ec' } });

    const submitBtn = screen.getByRole('button', { name: /Ingresar a la Plataforma/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(authApi.consumeMagicLink).toHaveBeenCalledWith({
        token: 'group_token_xyz',
        email: 'alumno.nuevo@ateneo.edu.ec',
        nombre: undefined,
      });
    });
  });

  it('debe mostrar mensaje descriptivo y opción de login si el token ha expirado o fue revocado', async () => {
    vi.mocked(authApi.consumeMagicLink).mockRejectedValueOnce({
      response: {
        status: 403,
        data: { detail: 'Este enlace de acceso ha sido revocado por un administrador.' },
      },
    });

    render(
      <MemoryRouter initialEntries={['/auth/magic-login?token=revoked_token']}>
        <Routes>
          <Route path="/auth/magic-login" element={<MagicLogin />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Enlace no disponible/i)).toBeInTheDocument();
      expect(screen.getByText(/Este enlace de acceso ha sido revocado/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /Ir al inicio de sesión regular/i })).toBeInTheDocument();
    });
  });

  it('debe renderizar el generador de Magic Links en la consola de administración con controles configurables', async () => {
    vi.mocked(authApi.listMagicLinks).mockResolvedValueOnce([
      {
        id: 'ml_test_01',
        magic_link_url: 'http://localhost:5174/auth/magic-login?token=xyz',
        email: 'profesor@ateneo.edu.ec',
        recipient_name: 'Dr. Martínez',
        rol: 'docente',
        tenant_id: 'tenant_default',
        target_path: '/cases',
        cohorte_id: 'general',
        restrict_domain: false,
        expires_at: new Date(Date.now() + 86400000).toISOString(),
        max_uses: 1,
        used_count: 0,
        is_revoked: false,
        created_at: new Date().toISOString(),
      },
    ]);

    render(
      <MemoryRouter>
        <MagicLinkGeneratorCard />
      </MemoryRouter>
    );

    // Encabezado del generador
    expect(screen.getByText(/Emisión de Magic Links e Invitaciones Configurables/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generar Magic Link Seguro/i })).toBeInTheDocument();

    // Selectores de roles configurables
    expect(screen.getByRole('button', { name: /^alumno$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^docente$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^administrador$/i })).toBeInTheDocument();

    // Tabla de auditoría con el link listado
    await waitFor(() => {
      expect(screen.getByText('Dr. Martínez')).toBeInTheDocument();
      expect(screen.getByText('0 / 1')).toBeInTheDocument();
      expect(screen.getByText('Activo')).toBeInTheDocument();
      expect(screen.getByText('Revocar')).toBeInTheDocument();
    });
  });
});
