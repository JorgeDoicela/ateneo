import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Register from '../modules/auth/pages/Register';
import { authApi } from '../modules/auth/api/authApi';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Página de Registro Institucional (Multi-Tenant - Ateneo+)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    mockNavigate.mockReset();
  });

  it('debe renderizar los elementos principales del formulario institucional', () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    expect(screen.getByText(/Crea tu cuenta institucional/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Nombres y apellidos completos/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Correo electrónico institucional/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Contraseña$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirmar contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Registrarse/i })).toBeInTheDocument();
  });

  it('debe detectar la Universidad Central del Ecuador (UCE) reactivamente al escribir su dominio', () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/Correo electrónico institucional/i);
    fireEvent.change(emailInput, { target: { value: 'medico.residente@uce.edu.ec' } });

    expect(screen.getByText(/Universidad Central del Ecuador/i)).toBeInTheDocument();
    expect(screen.getByText('UCE')).toBeInTheDocument();
  });

  it('debe detectar la Universidad San Francisco de Quito (USFQ) reactivamente', () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/Correo electrónico institucional/i);
    fireEvent.change(emailInput, { target: { value: 'interno.rotativo@usfq.edu.ec' } });

    expect(screen.getByText(/Universidad San Francisco de Quito/i)).toBeInTheDocument();
    expect(screen.getByText('USFQ')).toBeInTheDocument();
  });

  it('debe alertar si las contraseñas no coinciden', async () => {
    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Nombres y apellidos completos/i), {
      target: { value: 'Dra. Ana Ramos' }
    });
    fireEvent.change(screen.getByLabelText(/Correo electrónico institucional/i), {
      target: { value: 'ana.ramos@uce.edu.ec' }
    });
    fireEvent.change(screen.getByLabelText(/^Contraseña$/i), {
      target: { value: 'PasswordSeguro123!' }
    });
    fireEvent.change(screen.getByLabelText(/Confirmar contraseña/i), {
      target: { value: 'OtraPasswordDistinta456!' }
    });

    const submitBtn = screen.getByRole('button', { name: /Registrarse/i });
    fireEvent.click(submitBtn);

    expect(screen.getByText(/Las contraseñas ingresadas no coinciden/i)).toBeInTheDocument();
  });

  it('debe invocar authApi.register y presentar el estado de éxito institucional', async () => {
    const spyRegister = vi.spyOn(authApi, 'register').mockResolvedValue({
      id: 'usr_new_123',
      email: 'juan.medico@uce.edu.ec',
      nombre: 'Dr. Juan Médico',
      rol: 'alumno',
      tenant_id: 'tenant_uce',
      mensaje: 'Usuario registrado exitosamente en Universidad Central del Ecuador.'
    });

    render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Nombres y apellidos completos/i), {
      target: { value: 'Dr. Juan Médico' }
    });
    fireEvent.change(screen.getByLabelText(/Correo electrónico institucional/i), {
      target: { value: 'juan.medico@uce.edu.ec' }
    });
    fireEvent.change(screen.getByLabelText(/^Contraseña$/i), {
      target: { value: 'PasswordSeguro123!' }
    });
    fireEvent.change(screen.getByLabelText(/Confirmar contraseña/i), {
      target: { value: 'PasswordSeguro123!' }
    });

    const submitBtn = screen.getByRole('button', { name: /Registrarse/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(spyRegister).toHaveBeenCalledWith({
        nombre: 'Dr. Juan Médico',
        email: 'juan.medico@uce.edu.ec',
        password: 'PasswordSeguro123!',
        rol: 'alumno'
      });
      expect(screen.getByText(/Registro completado/i)).toBeInTheDocument();
      expect(screen.getByText(/Usuario registrado exitosamente en Universidad Central del Ecuador/i)).toBeInTheDocument();
    });
  });
});
