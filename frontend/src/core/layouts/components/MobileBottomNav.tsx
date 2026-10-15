import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { TrendingUp, Users, GraduationCap } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import UserProfileDropdown from './UserProfileDropdown';
import NotificationsDropdown from './NotificationsDropdown';
import ClinicalCareerModal from '../../../modules/gamification/components/ClinicalCareerModal';

export interface MobileBottomNavProps {
  onOpenSearch?: () => void;
  onOpenJoinRoom: () => void;
}

/**
 * MobileBottomNav — Barra de navegación inferior móvil estilo PWA / App moderna (Liquid Glassmorphism).
 * Se renderiza exclusivamente en la vista de catálogo principal ('/' o '/cases') en dispositivos móviles (< md).
 * Aloja los accesos clave de navegación, notificaciones clínicas y perfil con menús flotantes superiores (dropUp).
 */
export default function MobileBottomNav({ onOpenJoinRoom }: MobileBottomNavProps) {
  const { user } = useAuth();
  const location = useLocation();
  const [showCareerModal, setShowCareerModal] = useState<boolean>(false);

  if (!user) return null;

  // Ocultar en la resolución activa de casos clínicos para maximizar el área de simulación
  const isCaseSolveRoute = location.pathname.startsWith('/cases/') && location.pathname !== '/cases';
  if (isCaseSolveRoute) return null;

  return (
    <>
      {createPortal(
    <nav 
      aria-label="Navegación móvil inferior"
      className="md:hidden fixed bottom-4 inset-x-4 z-40 flex justify-center pointer-events-none select-none animate-fadeIn"
    >
      <div className="w-full max-w-md bg-white/85 backdrop-blur-xl border border-white/90 shadow-[0_8px_32px_rgba(15,23,42,0.12),0_2px_8px_rgba(6,182,212,0.08)] rounded-[28px] px-2 py-2 flex items-center justify-around gap-0.5 pointer-events-auto">
        {/* 1. Enlace Mi Desempeño */}
        <Link
          to="/analytics"
          className="flex-1 flex flex-col items-center justify-center py-1 px-1 text-slate-700 hover:text-[#0b57d0] active:scale-95 transition-all cursor-pointer group"
          title="Mi Desempeño y Tendencias Clínicas"
        >
          <TrendingUp className="w-5 h-5 text-slate-700 group-hover:text-[#0b57d0] transition-colors" />
          <span className="text-[10px] sm:text-[11px] font-medium text-slate-600 group-hover:text-[#0b57d0] transition-colors mt-1 leading-none">
            Desempeño
          </span>
        </Link>

        {/* 2. Botón Carrera Formativa e Hitos */}
        <button
          type="button"
          onClick={() => setShowCareerModal(true)}
          className="flex-1 flex flex-col items-center justify-center py-1 px-1 text-slate-700 hover:text-[#0b57d0] active:scale-95 transition-all cursor-pointer group"
          title="Carrera Formativa e Hitos Clínicos"
        >
          <GraduationCap className="w-5 h-5 text-slate-700 group-hover:text-[#0b57d0] transition-colors" />
          <span className="text-[10px] sm:text-[11px] font-medium text-slate-600 group-hover:text-[#0b57d0] transition-colors mt-1 leading-none">
            Hitos
          </span>
        </button>

        {/* 3. Botón Unirse a Sala */}
        <button
          type="button"
          onClick={onOpenJoinRoom}
          className="flex-1 flex flex-col items-center justify-center py-1 px-1 text-slate-700 hover:text-[#0b57d0] active:scale-95 transition-all cursor-pointer group"
          title="Unirse a Sala de Ateneo"
        >
          <Users className="w-5 h-5 text-slate-700 group-hover:text-[#0b57d0] transition-colors" />
          <span className="text-[10px] sm:text-[11px] font-medium text-slate-600 group-hover:text-[#0b57d0] transition-colors mt-1 leading-none">
            Unirse a Sala
          </span>
        </button>

        {/* 3. Menú Flotante de Notificaciones Clínicas (DropUp) */}
        <div className="flex-1 flex items-center justify-center">
          <NotificationsDropdown dropUp showLabel />
        </div>

        {/* 4. Menú Flotante de Perfil e Identidad (DropUp) */}
        <div className="flex-1 flex items-center justify-center">
          <UserProfileDropdown dropUp showLabel />
        </div>
      </div>
    </nav>,
    document.body
  )}

  <ClinicalCareerModal
    isOpen={showCareerModal}
    onClose={() => setShowCareerModal(false)}
  />
  </>
  );
}
