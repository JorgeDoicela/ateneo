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
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="orientation-title"
      className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 select-none animate-fadeIn"
    >
      {/* Tarjeta Oficial Blanca Ateneo+ con Bordes Redondeados Amplios */}
      <div className="bg-white rounded-[28px] shadow-2xl border border-slate-200/60 max-w-md w-full p-6 sm:p-8 space-y-6 animate-scaleUp relative overflow-hidden flex flex-col items-center">
        {/* Halos difusos sutiles de fondo para refracción Glassmorphism */}
        <div
          className="pointer-events-none absolute -top-12 -right-12 w-48 h-48 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />
        <div
          className="pointer-events-none absolute -bottom-10 -left-10 w-48 h-48 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />

        {/* Cabecera Institucional: Imagotipo y Marca Oficial Ateneo+ */}
        <div className="flex flex-col items-center relative z-10">
          <img
            src="/ateneo.png"
            alt="Ateneo+"
            className="w-12 h-12 object-contain mb-3"
          />
          <h1 className="font-heading font-black tracking-tight text-slate-900 text-lg">
            ATENEO<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600">+</span>
          </h1>
          <p className="text-xs text-slate-500 font-semibold uppercase tracking-wider mt-0.5">
            Simulador Hospitalario 3D • GPC Ecuador
          </p>
        </div>

        {/* Icono de Smartphone animado rotando a Horizontal (plano, sin marcos circulares ni cajas) */}
        <div className="relative z-10 py-3 flex items-center justify-center">
          <Smartphone className="w-14 h-14 text-[#0b57d0] transition-transform duration-700 ease-in-out transform -rotate-90 animate-pulse" />
        </div>

        {/* Título y Mensaje Explicativo */}
        <div className="text-center relative z-10 space-y-2">
          <h2 id="orientation-title" className="text-lg sm:text-xl font-heading font-semibold text-slate-900 tracking-tight">
            Orientación Horizontal Requerida
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Para una experiencia de simulación clínica inmersiva y recorrer el hospital con ergonomía táctil completa, por favor gira tu teléfono a <strong className="text-slate-900 font-semibold">modo horizontal</strong>.
          </p>
        </div>

        {/* Botonera de Acción Píldora Ateneo+ */}
        <div className="w-full flex flex-col sm:flex-row items-center gap-3 relative z-10 pt-2">
          <button
            type="button"
            onClick={handleRotateAndFullscreen}
            className="w-full py-3 px-6 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-700 hover:via-blue-700 hover:to-indigo-700 text-white font-medium text-sm rounded-full transition-all shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer"
          >
            <Maximize2 className="w-4 h-4" />
            <span>Pantalla Completa</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/cases')}
            className="w-full py-3 px-6 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200/80 rounded-full font-medium text-sm transition-all shadow-xs flex items-center justify-center gap-2 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4 text-[#0b57d0]" />
            <span>Volver al Catálogo</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandscapeOrientationNotice;
