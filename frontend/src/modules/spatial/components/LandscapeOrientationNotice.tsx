import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Smartphone, ArrowLeft, Maximize2 } from 'lucide-react';

interface LandscapeOrientationNoticeProps {
  onRequestFullscreen?: () => void;
}

export const LandscapeOrientationNotice: React.FC<LandscapeOrientationNoticeProps> = ({
  onRequestFullscreen
}) => {
  const navigate = useNavigate();

  const handleRotateAndFullscreen = async () => {
    if (onRequestFullscreen) {
      onRequestFullscreen();
    }

    if (screen.orientation && 'lock' in screen.orientation) {
      try {
        await (screen.orientation as any).lock('landscape');
      } catch {
        // Silencioso si el navegador del dispositivo no permite bloqueo de orientación por software
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/95 backdrop-blur-xl flex flex-col items-center justify-center p-6 text-center select-none text-white animate-fadeIn">
      {/* Contenedor central con tarjeta de vidrio esmerilado */}
      <div className="max-w-md w-full bg-white/10 border border-white/20 rounded-[28px] p-8 shadow-2xl backdrop-blur-md flex flex-col items-center">
        {/* Rótulo superior de identidad */}
        <div className="flex items-center space-x-2 text-cyan-300 text-xs font-semibold uppercase tracking-wider mb-6">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>Simulador Hospitalario 3D • Ateneo+</span>
        </div>

        {/* Animación del Smartphone rotando a Horizontal */}
        <div className="relative w-28 h-28 flex items-center justify-center mb-6">
          {/* Anillo de órbita decorativo */}
          <div className="absolute inset-0 rounded-full border border-cyan-400/30 border-dashed animate-spin [animation-duration:12s]" />

          {/* Teléfono rotando de vertical a horizontal mediante CSS */}
          <div className="relative animate-bounce [animation-duration:3s]">
            <Smartphone className="w-16 h-16 text-cyan-300 transition-transform duration-700 ease-in-out transform -rotate-90" />
          </div>
        </div>

        {/* Título y Mensaje Explicativo */}
        <h2 className="text-xl sm:text-2xl font-bold text-white mb-3">
          Orientación Horizontal Requerida
        </h2>
        <p className="text-sm text-slate-300 leading-relaxed mb-8">
          Para una experiencia de simulación clínica inmersiva y recorrer el hospital con ergonomía táctil completa, por favor gira tu teléfono a <strong className="text-white font-semibold">modo horizontal</strong>.
        </p>

        {/* Botonera de Acción */}
        <div className="w-full flex flex-col sm:flex-row items-center gap-3">
          <button
            type="button"
            onClick={handleRotateAndFullscreen}
            className="w-full py-3.5 px-5 bg-[#0b57d0] hover:bg-blue-600 text-white rounded-full font-semibold text-sm shadow-lg shadow-blue-500/25 transition-all flex items-center justify-center space-x-2 cursor-pointer"
          >
            <Maximize2 className="w-4 h-4" />
            <span>Pantalla Completa</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/cases')}
            className="w-full py-3.5 px-5 bg-white/15 hover:bg-white/25 text-slate-200 hover:text-white rounded-full font-medium text-sm border border-white/20 transition-all flex items-center justify-center space-x-2 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Volver al Catálogo</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandscapeOrientationNotice;
