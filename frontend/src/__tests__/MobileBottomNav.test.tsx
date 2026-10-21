import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MobileBottomNav from '../core/layouts/components/MobileBottomNav';
import { ThemeProvider } from '../core/theme/ThemeProvider';

// Mock de AuthContext
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: {
      id: 1,
      nombre: 'Estudiante Prueba',
      email: 'estudiante@ateneo.edu.ec',
      rol: 'alumno'
    }
  })
}));

describe('Componente MobileBottomNav (Navegación Móvil Inferior)', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false, gcTime: 0 },
      },
    });
  });

  const renderComponent = (initialRoute: string) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <MemoryRouter initialEntries={[initialRoute]}>
            <MobileBottomNav onOpenJoinRoom={vi.fn()} />
          </MemoryRouter>
        </ThemeProvider>
      </QueryClientProvider>
    );
  };

  it('debe renderizarse en rutas generales como /cases', () => {
    renderComponent('/cases');

    expect(screen.getByText('Desempeño')).toBeInTheDocument();
    expect(screen.getByText('Hitos')).toBeInTheDocument();
    expect(screen.getByText('Unirse a Sala')).toBeInTheDocument();
  });

  it('NO debe renderizarse cuando la ruta es /analytics', () => {
    renderComponent('/analytics');

    expect(screen.queryByText('Desempeño')).not.toBeInTheDocument();
    expect(screen.queryByText('Hitos')).not.toBeInTheDocument();
    expect(screen.queryByText('Unirse a Sala')).not.toBeInTheDocument();
  });

  it('NO debe renderizarse en resolución de casos /cases/123', () => {
    renderComponent('/cases/123');

    expect(screen.queryByText('Desempeño')).not.toBeInTheDocument();
    expect(screen.queryByText('Hitos')).not.toBeInTheDocument();
  });

  it('debe cumplir con la regla de oro: CERO EMOJIS', () => {
    const { container } = renderComponent('/cases');

    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    expect(emojiRegex.test(container.textContent || '')).toBe(false);
  });
});
