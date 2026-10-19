import React from 'react';
import { useLocation } from 'react-router-dom';
import { HelpCircle } from 'lucide-react';
import { useTourStore } from './useTourStore';

/**
 * TourHelpButton — Botón flotante estilizado en Liquid Glassmorphism (Ateneo+ Design System).
 * En dispositivos móviles se ubica exactamente arriba del acceso de 'Perfil' de la barra inferior.
 * En escritorio se ubica en el margen inferior derecho del catálogo de casos.
 */
export const TourHelpButton: React.FC = () => {
  const location = useLocation();
  const { isOpen, startTour } = useTourStore();

  // Exclusivo del catálogo de casos clínicos
  const isCatalogRoute = location.pathname === '/' || location.pathname === '/cases';
  if (!isCatalogRoute || isOpen) return null;

  return (
    <button
      type="button"
      onClick={startTour}
      aria-label="Abrir guía interactiva del simulador"
      title="Guía interactiva del simulador"
      className="fixed bottom-24 right-5 md:bottom-6 md:right-6 z-40 w-11 h-11 rounded-full bg-white/90 backdrop-blur-md border border-slate-200/90 shadow-[0_4px_20px_rgba(15,23,42,0.12),0_2px_8px_rgba(6,182,212,0.15)] text-[#0b57d0] hover:text-blue-700 hover:bg-white active:scale-95 transition-all flex items-center justify-center cursor-pointer select-none group"
    >
      <HelpCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
      <span className="sr-only">Ayuda y Guía del Simulador</span>
    </button>
  );
};

export default TourHelpButton;
