import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ResearchConsentModal from '../modules/auth/components/ResearchConsentModal';
import { useAuthStore } from '../core/stores/useAuthStore';

describe('Modal de Consentimiento Informado y Marco Legal (ResearchConsentModal)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.setState({
      user: {
        id: 'usr_test',
        email: 'alumno@ateneo.edu.ec',
        nombre: 'Estudiante Prueba',
        rol: 'alumno'
      },
      token: 'jwt_mock_token',
      sessionConsentAcknowledged: false
    });
  });

  it('debe renderizar el título, advertencia de versión experimental y cláusulas LOPDP', () => {
    render(<ResearchConsentModal />);

    expect(screen.getByText(/Consentimiento Informado y Descargo Legal/i)).toBeInTheDocument();
    expect(screen.getByText(/Versión Experimental y Prototipo Académico/i)).toBeInTheDocument();
    expect(screen.getByText(/Finalidad Exclusivamente Educativa y de Investigación/i)).toBeInTheDocument();
    expect(screen.getByText(/Protección y Tratamiento de Datos Personales \(LOPDP\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Participación Voluntaria en Prueba Piloto/i)).toBeInTheDocument();
  });

  it('el botón de confirmar debe estar deshabilitado hasta marcar ambas casillas obligatorias', () => {
    render(<ResearchConsentModal />);

    const confirmButton = screen.getByRole('button', { name: /Confirmar Consentimiento e Ingresar/i });
    expect(confirmButton).toBeDisabled();

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBe(2);

    // Marcar solo una
    fireEvent.click(checkboxes[0]);
    expect(confirmButton).toBeDisabled();

    // Marcar la segunda
    fireEvent.click(checkboxes[1]);
    expect(confirmButton).not.toBeDisabled();
  });

  it('debe ejecutar acceptTermsAndUnlockSession y llamar a onSuccess al confirmar', async () => {
    const onSuccessMock = vi.fn();
    const acceptTermsMock = vi.fn().mockResolvedValue({
      id: 'usr_test',
      email: 'alumno@ateneo.edu.ec',
      nombre: 'Estudiante Prueba',
      rol: 'alumno',
      terminos_aceptados: true
    });

    useAuthStore.setState({
      acceptTermsAndUnlockSession: acceptTermsMock
    });

    render(<ResearchConsentModal onSuccess={onSuccessMock} />);

    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);
    fireEvent.click(checkboxes[1]);

    const confirmButton = screen.getByRole('button', { name: /Confirmar Consentimiento e Ingresar/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(acceptTermsMock).toHaveBeenCalledWith('v1.0-investigacion-2026');
      expect(onSuccessMock).toHaveBeenCalledTimes(1);
    });
  });

  it('debe invocar logout al pulsar rechazar y cerrar sesión', async () => {
    const logoutMock = vi.fn().mockResolvedValue(undefined);
    useAuthStore.setState({ logout: logoutMock });

    render(<ResearchConsentModal />);

    const rejectButton = screen.getByRole('button', { name: /Rechazar y Cerrar Sesión/i });
    fireEvent.click(rejectButton);

    await waitFor(() => {
      expect(logoutMock).toHaveBeenCalledTimes(1);
    });
  });
});
