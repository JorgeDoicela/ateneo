import { useState, useEffect } from 'react';
import { GraduationCap } from 'lucide-react';
import { gamificationApi } from '../api/gamificationApi';
import ClinicalCareerModal from './ClinicalCareerModal';
import type { GamificationProfile } from '../types';

export default function CareerBadgeButton() {
  const [profile, setProfile] = useState<GamificationProfile | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const fetchProfile = () => {
      gamificationApi
        .getProfile()
        .then((data) => {
          if (isMounted) setProfile(data);
        })
        .catch((err) => {
          console.warn('Aviso: no se pudo cargar el perfil de carrera médica:', err);
        });
    };

    fetchProfile();

    const handleUpdate = () => {
      fetchProfile();
    };

    window.addEventListener('ateneo:gamification-updated', handleUpdate);

    return () => {
      isMounted = false;
      window.removeEventListener('ateneo:gamification-updated', handleUpdate);
    };
  }, []);

  return (
    <>
      <button
        type="button"
        onClick={() => setShowModal(true)}
        title="Carrera Formativa e Hitos Clínicos"
        className="hidden md:flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-full text-xs font-medium transition-all duration-200 select-none bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-[#0b57d0] border border-blue-200/60 hover:border-blue-300/90 shadow-xs hover:shadow-sm cursor-pointer"
      >
        <GraduationCap className="w-4 h-4 text-[#0b57d0]" />
        <span className="hidden sm:inline font-semibold">
          {profile ? `Nivel ${profile.nivel_actual}` : 'Carrera'}
        </span>
        {profile && (
          <span className="hidden lg:inline text-[11px] text-slate-500 font-mono">
            • {profile.puntos_xp} XP
          </span>
        )}
      </button>

      <ClinicalCareerModal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          // Refrescar perfil tras cerrar en caso de avances
          gamificationApi.getProfile().then(setProfile).catch(() => {});
        }}
      />
    </>
  );
}
