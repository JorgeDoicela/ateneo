import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, X } from 'lucide-react';
import ClinicalButton from '../../../core/ui/ClinicalButton';

export interface JoinRoomModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * JoinRoomModal — Modal autónomo para ingresar a una Sala de Ateneo Colaborativa por código
 */
export default function JoinRoomModal({ isOpen, onClose }: JoinRoomModalProps) {
  const navigate = useNavigate();
  const [roomInput, setRoomInput] = useState('');
  const [joinError, setJoinError] = useState<string | null>(null);

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

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-white rounded-[28px] shadow-xl border-0 max-w-md w-full p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center gap-2.5">
            <Users className="w-5 h-5 text-[#0b57d0]" />
            <h3 className="text-lg font-normal text-[#1f1f1f] font-heading">
              Unirse a Sala de Ateneo
            </h3>
          </div>
          <button
            onClick={handleClose}
            className="p-1.5 rounded-full hover:bg-slate-100 text-[#747775] cursor-pointer transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleJoinRoom} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[#444746] mb-1.5">
              Código de Sala (6 u 8 caracteres)
            </label>
            <input
              type="text"
              placeholder="ej. ATENEO-8Q8Y"
              value={roomInput}
              onChange={(e) => setRoomInput(e.target.value.toUpperCase())}
              required
              autoFocus
              className="w-full px-4 py-3 bg-[#f0f4f9] rounded-[16px] text-sm font-mono uppercase text-[#1f1f1f] border border-slate-200/80 focus:outline-none focus:border-[#0b57d0]"
            />
          </div>

          {joinError && (
            <p className="text-xs text-rose-600 font-medium">{joinError}</p>
          )}

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-xs font-medium text-[#444746] hover:text-[#1f1f1f] cursor-pointer"
            >
              Cancelar
            </button>
            <ClinicalButton type="submit" variant="primary" size="md">
              Ingresar a la Sala
            </ClinicalButton>
          </div>
        </form>
      </div>
    </div>
  );
}
