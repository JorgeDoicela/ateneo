import { createPortal } from 'react-dom';
import { Share, PlusSquare, X, Smartphone, Monitor, Download, ArrowRight } from 'lucide-react';

export interface PWAInstallModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * PWAInstallModal — Diálogo de orientación clínica para la instalación de Ateneo+ PWA.
 * Adaptativo según la plataforma detectada: iOS Safari vs. Escritorio (Chrome, Edge) y otros navegadores.
 */
export default function PWAInstallModal({ isOpen, onClose }: PWAInstallModalProps) {
  if (!isOpen) return null;

  const isIOS = typeof navigator !== 'undefined' && 
    /iPad|iPhone|iPod/.test(navigator.userAgent) && 
    !(window as unknown as { MSStream?: unknown }).MSStream;

  return createPortal(
    <div 
      className="fixed inset-0 z-[120] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="pwa-install-title"
    >
      <div 
        className="bg-white rounded-[28px] shadow-2xl border border-slate-200/60 max-w-md w-full p-6 sm:p-7 space-y-5 animate-scaleUp relative overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Halos difusos sutiles de fondo para refracción Glassmorphism */}
        <div 
          className="pointer-events-none absolute -top-12 -right-12 w-48 h-48 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />
        <div 
          className="pointer-events-none absolute -bottom-10 -left-10 w-48 h-48 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />

        {/* Cabecera del Diálogo */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 relative z-10">
          <div className="flex items-center gap-2.5">
            {isIOS ? (
              <Smartphone className="w-5 h-5 text-[#0b57d0] shrink-0" />
            ) : (
              <Monitor className="w-5 h-5 text-[#0b57d0] shrink-0" />
            )}
            <div>
              <h3 id="pwa-install-title" className="text-base font-heading font-normal text-slate-900 tracking-tight">
                {isIOS ? 'Instalar Ateneo+ en iOS' : 'Instalar Ateneo+ en este equipo'}
              </h3>
              <p className="text-xs text-slate-500">
                Acceso clínico directo en ventana independiente
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer transition-colors"
            aria-label="Cerrar modal de instalación"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Pasos de Instalación Adaptativos */}
        <div className="space-y-3 relative z-10 text-xs text-slate-700">
          {isIOS ? (
            <>
              <div className="flex items-start gap-3 p-3 bg-slate-50/70 rounded-2xl border border-slate-100/80">
                <Share className="w-5 h-5 text-[#0b57d0] shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-900">1. Toca el botón Compartir</p>
                  <p className="text-slate-500 mt-0.5 leading-relaxed">
                    En la barra inferior de Safari, pulsa el icono de Compartir (el cuadro con una flecha hacia arriba).
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-slate-50/70 rounded-2xl border border-slate-100/80">
                <PlusSquare className="w-5 h-5 text-[#0b57d0] shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-900">2. Selecciona "Añadir a pantalla de inicio"</p>
                  <p className="text-slate-500 mt-0.5 leading-relaxed">
                    Desplázate por el menú hacia abajo y pulsa para anclar Ateneo+ a tu pantalla principal.
                  </p>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-start gap-3 p-3 bg-slate-50/70 rounded-2xl border border-slate-100/80">
                <Download className="w-5 h-5 text-[#0b57d0] shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-900">1. Barra de direcciones del navegador</p>
                  <p className="text-slate-500 mt-0.5 leading-relaxed">
                    Haz clic en el icono de instalación (pantalla con flecha o símbolo <strong>⊕</strong>) situado a la derecha de la barra de direcciones de Chrome o Edge.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 bg-slate-50/70 rounded-2xl border border-slate-100/80">
                <ArrowRight className="w-5 h-5 text-[#0b57d0] shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-slate-900">2. O desde el menú de opciones</p>
                  <p className="text-slate-500 mt-0.5 leading-relaxed">
                    Abre el menú de opciones del navegador (los tres puntos <strong>⋮</strong> arriba a la derecha) y selecciona <strong>"Instalar Ateneo+"</strong> o <strong>"Instalar aplicación"</strong>.
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Botón de Cierre */}
        <div className="pt-2 relative z-10">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2.5 px-4 rounded-full bg-[#0b57d0] hover:bg-blue-700 text-white font-medium text-xs shadow-xs hover:shadow-sm transition-all cursor-pointer"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
}
