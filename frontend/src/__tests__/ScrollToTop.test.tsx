import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ScrollToTop from '../core/router/ScrollToTop';

describe('Controlador de Restauración de Scroll (ScrollToTop)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.scrollTo = vi.fn();
    Object.defineProperty(window.history, 'scrollRestoration', {
      writable: true,
      value: 'auto',
      configurable: true,
    });
  });

  it('debe configurar window.history.scrollRestoration en manual', () => {
    render(
      <MemoryRouter initialEntries={['/cases']}>
        <ScrollToTop />
      </MemoryRouter>
    );

    expect(window.history.scrollRestoration).toBe('manual');
  });

  it('debe desplazar la ventana a (0, 0) al montar la ruta inicial', () => {
    render(
      <MemoryRouter initialEntries={['/cases/case_preeclampsia_01']}>
        <ScrollToTop />
      </MemoryRouter>
    );

    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      left: 0,
      behavior: 'instant',
    });
  });
});
