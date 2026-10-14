import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * ScrollToTop — Controlador institucional de restauración de scroll para SPA (Ateneo+).
 * 
 * Causa Raíz:
 * En navegaciones de cliente (Single Page Application), el navegador mantiene la coordenada Y
 * del scroll de la vista previa al no producirse recarga de página. Esto causaba que al seleccionar
 * un caso clínico o navegar entre secciones, el usuario aterrizara en la mitad o fondo de la página.
 *
 * Solución Arquitectónica:
 * 1. Desactiva la restauración automática del historial del navegador (`scrollRestoration = 'manual'`).
 * 2. Ante cada cambio de ruta (`pathname`) o parámetros (`search`), restablece la vista al tope absoluto (0, 0).
 * 3. Respeta enlaces de anclaje interno (#hash) si existieran.
 */
export default function ScrollToTop() {
  const { pathname, search } = useLocation();

  useEffect(() => {
    if (typeof window !== 'undefined' && 'scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual';
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (!window.location.hash) {
        window.scrollTo({ top: 0, left: 0, behavior: 'instant' as ScrollBehavior });
      }
    }
  }, [pathname, search]);

  return null;
}
