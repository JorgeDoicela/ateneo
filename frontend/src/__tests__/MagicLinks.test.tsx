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
    verifyMagicLink: vi.fn(),
    consumeMagicLink: vi.fn(),
    createMagicLink: vi.fn(),
    createMagicLinksBatch: vi.fn(),
    listMagicLinks: vi.fn(),
    revokeMagicLink: vi.fn(),
    purgeMagicLink: vi.fn(),
    purgeRevokedLinks: vi.fn(),
  },
  authApi: {
    verifyMagicLink: vi.fn(),
    consumeMagicLink: vi.fn(),
    createMagicLink: vi.fn(),
    createMagicLinksBatch: vi.fn(),
    listMagicLinks: vi.fn(),
    revokeMagicLink: vi.fn(),
    purgeMagicLink: vi.fn(),
    purgeRevokedLinks: vi.fn(),
  },
}));

describe('Suite de Pruebas: Magic Links e Invitaciones Configurables (Ateneo+)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({ user: null, token: null, loading: false });
  });

  it('debe verificar el enlace, mostrar tarjeta de confirmación del rol y canjear tras pulsar confirmar', async () => {
    const mockUser = {
      id: 'usr_docente_01',
      email: 'docente.evaluador@ateneo.edu.ec',
      nombre: 'Dr. Evaluador Externo',
      rol: 'docente' as const,
      tenant_id: 'tenant_default',
    };

    vi.mocked(authApi.verifyMagicLink).mockResolvedValueOnce({
      is_valid: true,
      rol: 'docente',
      recipient_name: 'Dr. Evaluador Externo',
      target_path: '/cases/case_preeclampsia_01',
      requires_identity: false,
      expires_at: new Date(Date.now() + 86400000).toISOString(),
      tenant_name: 'Facultad de Ciencias Médicas',
    });

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

    // 1. Debe verificar el enlace con el backend
    await waitFor(() => {
      expect(authApi.verifyMagicLink).toHaveBeenCalledWith('valid_token_abc');
    });

    // 2. Debe renderizar la tarjeta con los detalles del rol y el destinatario
    await waitFor(() => {
      expect(screen.getByText(/Invitación de Acceso Institucional/i)).toBeInTheDocument();
      expect(screen.getByText(/Dr. Evaluador Externo/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Confirmar e Ingresar a Ateneo\+/i })).toBeInTheDocument();
    });

    // 3. El usuario pulsa el botón de confirmación interno
    const confirmBtn = screen.getByRole('button', { name: /Confirmar e Ingresar a Ateneo\+/i });
    fireEvent.click(confirmBtn);

    // 4. Debe canjear el enlace en backend
    await waitFor(() => {
      expect(authApi.consumeMagicLink).toHaveBeenCalledWith({
        token: 'valid_token_abc',
        email: undefined,
        nombre: 'Dr. Evaluador Externo',
      });
    });

    // 5. Debe haber autenticado en el store global y navegado al destino
    await waitFor(() => {
      const state = useAuthStore.getState();
      expect(Boolean(state.token && state.user)).toBe(true);
      expect(state.token).toBe('mock_jwt_token_123');
      expect(state.user?.email).toBe('docente.evaluador@ateneo.edu.ec');
      expect(screen.getByText('Destino: Preeclampsia')).toBeInTheDocument();
    });
  });

  it('debe solicitar correo institucional e identidad si el enlace es de cohorte grupal', async () => {
    vi.mocked(authApi.verifyMagicLink).mockResolvedValueOnce({
      is_valid: true,
      rol: 'alumno',
      target_path: '/cases',
      requires_identity: true,
      expires_at: new Date(Date.now() + 86400000).toISOString(),
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

    const submitBtn = screen.getByRole('button', { name: /Confirmar e Ingresar a Ateneo\+/i });
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
    vi.mocked(authApi.verifyMagicLink).mockRejectedValueOnce({
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

  it('debe permitir conmutar a lote, configurar inicio en 1 y emitir el lote atómicamente', async () => {
    vi.mocked(authApi.listMagicLinks).mockResolvedValue([]);
    vi.mocked(authApi.createMagicLinksBatch).mockResolvedValueOnce([
      {
        id: 'ml_b1',
        magic_link_url: 'http://localhost:5174/auth/magic-login?token=tok1',
        email: 'estudiante1@ateneo.edu.ec',
        recipient_name: 'Estudiante 1',
        rol: 'alumno',
        tenant_id: 'tenant_default',
        target_path: '/cases',
        cohorte_id: 'general',
        restrict_domain: false,
        expires_at: new Date(Date.now() + 86400000).toISOString(),
        max_uses: 100,
        used_count: 0,
        is_revoked: false,
        created_at: new Date().toISOString(),
      },
      {
        id: 'ml_b2',
        magic_link_url: 'http://localhost:5174/auth/magic-login?token=tok2',
        email: 'estudiante2@ateneo.edu.ec',
        recipient_name: 'Estudiante 2',
        rol: 'alumno',
        tenant_id: 'tenant_default',
        target_path: '/cases',
        cohorte_id: 'general',
        restrict_domain: false,
        expires_at: new Date(Date.now() + 86400000).toISOString(),
        max_uses: 100,
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

    // Conmutar a modalidad de Lote
    const batchModeBtn = screen.getByRole('button', { name: /Generación en Lote/i });
    fireEvent.click(batchModeBtn);

    // Debe mostrar los controles de prefijo, inicio en 1 y cantidad
    expect(screen.getByLabelText(/Prefijo o Etiqueta Base/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Iniciar en 1/i })).toBeInTheDocument();

    // El botón principal de submit debe reflejar el lote
    const submitBatchBtn = screen.getByRole('button', { name: /Generar Lote de 3 \(Estudiante 1 a 3\)/i });
    expect(submitBatchBtn).toBeInTheDocument();

    // Simular clic en submit de lote
    fireEvent.click(submitBatchBtn);

    await waitFor(() => {
      expect(authApi.createMagicLinksBatch).toHaveBeenCalledWith(
        expect.objectContaining({
          rol: 'alumno',
          base_name: 'Estudiante',
          start_index: 1,
          count: 3,
          es_reutilizable: true,
        })
      );
    });
  });
});

