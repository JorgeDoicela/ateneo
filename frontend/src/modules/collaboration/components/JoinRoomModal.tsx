import { useState, useEffect, FormEvent } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { Users, X } from 'lucide-react';
import ClinicalButton from '../../../core/ui/ClinicalButton';

export interface JoinRoomModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * JoinRoomModal — Modal autónomo para ingresar a una Sala de Ateneo Colaborativa por código.
 * Renderizado vía React Portal hacia document.body para desacoplar el posicionamiento
 * de cualquier stacking context o backdrop-filter del Navbar.
 */
export default function JoinRoomModal({ isOpen, onClose }: JoinRoomModalProps) {
  const navigate = useNavigate();
  const [roomInput, setRoomInput] = useState('');
  const [joinError, setJoinError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleJoinRoom = (e: FormEvent) => {
    e.preventDefault();
    const cleanCode = roomInput.trim().toUpperCase();
    if (!cleanCode) {
      setJoinError('Por favor ingresa un código válido');
      return;
    }
    setJoinError(null);
    setRoomInput('');
    onClose();
    navigate(`/ateneo/${cleanCode}`);
  };

  const handleClose = () => {
    setJoinError(null);
    setRoomInput('');
    onClose();
  };

  return createPortal(
    <div 
      className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
      onClick={handleClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="join-room-title"
    >
      <div 
        className="bg-white rounded-[28px] shadow-2xl border border-slate-200/60 max-w-lg w-full p-6 sm:p-8 space-y-6 animate-scaleUp relative overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Halos difusos sutiles de fondo para refracción Glassmorphism confinados en el modal */}
        <div 
          className="pointer-events-none absolute -top-12 -right-12 w-52 h-52 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />
        <div 
          className="pointer-events-none absolute -bottom-10 -left-10 w-52 h-52 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />

        {/* Cabecera del Diálogo */}
        <div className="flex items-center justify-between border-b border-slate-100/90 pb-4 relative z-10">
          <div className="flex items-center gap-2.5">
            <Users className="w-5 h-5 text-blue-600 shrink-0" />
            <div>
              <h3 id="join-room-title" className="text-lg font-heading font-normal text-slate-900 tracking-tight">
                Unirse a Sala de Ateneo
              </h3>
              <p className="text-xs text-slate-500">
                Discusión clínica sincrónica y análisis de casos en tiempo real
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer transition-colors"
            aria-label="Cerrar modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={handleJoinRoom} className="space-y-5 relative z-10">
          <div>
            <label htmlFor="room-code-input" className="block text-xs font-medium text-slate-700 mb-1.5">
              Código de Sala (6 u 8 caracteres)
            </label>
            <div className="relative">
              <input
                id="room-code-input"
                type="text"
                placeholder="ej. ATENEO-8Q8Y"
                value={roomInput}
                onChange={(e) => setRoomInput(e.target.value.toUpperCase())}
                required
                autoFocus
                maxLength={16}
                className="w-full px-4 py-3 bg-[#f0f4f9] rounded-[16px] text-sm font-mono uppercase tracking-wider text-slate-900 border border-slate-200/90 focus:outline-none focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100/60 transition-all placeholder:text-slate-400"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1.5">
              Solicita el código al docente facilitador o al creador de la sesión clínica.
            </p>
          </div>

          {joinError && (
            <div className="p-3 bg-rose-50/90 border border-rose-200/80 rounded-[14px] text-xs text-rose-700 font-medium animate-fadeIn">
              {joinError}
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2.5 text-xs sm:text-sm font-medium text-slate-700 hover:text-slate-900 bg-white/70 hover:bg-slate-100/80 border border-slate-200/60 rounded-full transition-all cursor-pointer shadow-2xs"
            >
              Cancelar
            </button>
            <ClinicalButton type="submit" variant="primary" size="md">
              Ingresar a la Sala
            </ClinicalButton>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
}
