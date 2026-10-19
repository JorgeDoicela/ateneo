import React, { useEffect, useState, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X, ArrowRight, ArrowLeft, Check, Sparkles } from 'lucide-react';
import { useTourStore } from './useTourStore';
import { CATALOG_TOUR_STEPS } from './tourSteps';

interface RectPosition {
  top: number;
  left: number;
  width: number;
  height: number;
}

export const StudentTourGuide: React.FC = () => {
  const { isOpen, currentStepIndex, closeTour, nextStep, prevStep } = useTourStore();
  const [targetRect, setTargetRect] = useState<RectPosition | null>(null);
  const [tooltipPos, setTooltipPos] = useState<{ top: number; left: number; arrowPlacement: 'top' | 'bottom' }>({
    top: 0,
    left: 0,
    arrowPlacement: 'top',
  });
  const tooltipRef = useRef<HTMLDivElement>(null);

  const step = CATALOG_TOUR_STEPS[currentStepIndex] || CATALOG_TOUR_STEPS[0];
  const totalSteps = CATALOG_TOUR_STEPS.length;

  // Función para obtener el elemento objetivo visible en el viewport
  const getVisibleTargetElement = useCallback((): HTMLElement | null => {
    if (!step) return null;
    const elements = Array.from(document.querySelectorAll(step.targetSelector)) as HTMLElement[];
    // Seleccionar el primer elemento que tenga dimensiones reales y no esté oculto por CSS
    return elements.find((el) => {
      const b = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      return b.width > 0 && b.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
    }) || null;
  }, [step]);

  // Actualizar coordenadas del elemento objetivo
  const updateTargetCoordinates = useCallback(() => {
    if (!isOpen) return;

    const el = getVisibleTargetElement();
    if (el) {
      const b = el.getBoundingClientRect();
      if (b.width > 0 && b.height > 0) {
        setTargetRect({
          top: b.top,
          left: b.left,
          width: b.width,
          height: b.height,
        });
        return;
      }
    }
    // Fallback si el selector no se encuentra visible
    setTargetRect(null);
  }, [isOpen, getVisibleTargetElement]);

  // Desplazar hacia el elemento cuando cambia el paso
  useEffect(() => {
    if (!isOpen || !step) return;

    const el = getVisibleTargetElement();
    if (el) {
      const isFixed = window.getComputedStyle(el).position === 'fixed' || Boolean(el.closest('.fixed'));
      if (!isFixed) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    // Mediciones periódicas para asegurar precisión durante el scroll suave
    updateTargetCoordinates();
    const t1 = setTimeout(updateTargetCoordinates, 80);
    const t2 = setTimeout(updateTargetCoordinates, 250);
    const t3 = setTimeout(updateTargetCoordinates, 500);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [isOpen, step, getVisibleTargetElement, updateTargetCoordinates]);

  // Escuchar redimensionamiento, desplazamiento y atajos de teclado
  useEffect(() => {
    if (!isOpen) return;

    window.addEventListener('resize', updateTargetCoordinates);
    window.addEventListener('scroll', updateTargetCoordinates, true);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeTour();
      } else if (e.key === 'ArrowRight') {
        nextStep(totalSteps);
      } else if (e.key === 'ArrowLeft') {
        prevStep();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('resize', updateTargetCoordinates);
      window.removeEventListener('scroll', updateTargetCoordinates, true);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, closeTour, nextStep, prevStep, totalSteps, updateTargetCoordinates]);

  // Calcular la posición óptima del tooltip y la flecha indicadora
  useEffect(() => {
    if (!tooltipRef.current) return;

    const tooltipEl = tooltipRef.current;
    const tooltipWidth = tooltipEl.offsetWidth || 340;
    const tooltipHeight = tooltipEl.offsetHeight || 190;
    const padding = 16;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    if (!targetRect) {
      // Posición centralizada en pantalla si no se detectó rect
      setTooltipPos({
        top: Math.max(padding, (viewportHeight - tooltipHeight) / 2),
        left: Math.max(padding, (viewportWidth - tooltipWidth) / 2),
        arrowPlacement: 'top',
      });
      return;
    }

    let left = targetRect.left + (targetRect.width / 2) - (tooltipWidth / 2);

    // Confinar horizontalmente dentro del viewport
    if (left < padding) left = padding;
    if (left + tooltipWidth > viewportWidth - padding) {
      left = viewportWidth - tooltipWidth - padding;
    }

    // Determinar si colocar arriba o abajo del elemento objetivo
    const spaceBelow = viewportHeight - (targetRect.top + targetRect.height + padding);
    const spaceAbove = targetRect.top - padding;

    let top = 0;
    let arrowPlacement: 'top' | 'bottom' = 'top';

    if (step.placement === 'top' || (spaceBelow < tooltipHeight + 20 && spaceAbove > tooltipHeight)) {
      // Colocar arriba del elemento (la flecha del tooltip apunta hacia abajo)
      top = targetRect.top - tooltipHeight - 16;
      arrowPlacement = 'bottom';
    } else {
      // Colocar debajo del elemento (la flecha del tooltip apunta hacia arriba)
      top = targetRect.top + targetRect.height + 16;
      arrowPlacement = 'top';
    }

    // Asegurar límites verticales estrictos
    if (top < padding) {
      top = padding;
      arrowPlacement = 'top';
    } else if (top + tooltipHeight > viewportHeight - padding) {
      top = viewportHeight - tooltipHeight - padding;
      arrowPlacement = 'bottom';
    }

    setTooltipPos({ top, left, arrowPlacement });
  }, [targetRect, step]);

  if (!isOpen) return null;

  const isLastStep = currentStepIndex === totalSteps - 1;

  // Cálculo del centro horizontal del elemento para alinear la flecha
  const arrowLeftOffset = targetRect
    ? Math.max(24, Math.min(310, targetRect.left + (targetRect.width / 2) - tooltipPos.left))
    : 160;

  const content = (
    <div className="fixed inset-0 z-[100] select-none pointer-events-auto">
      {/* SVG Spotlight Cutout Overlay */}
      <svg
        className="fixed inset-0 w-full h-full pointer-events-none"
        style={{ width: '100vw', height: '100vh' }}
        aria-hidden="true"
      >
        <defs>
          <mask id="ateneo-spotlight-mask">
            {/* Fondo blanco revela todo el overlay oscuro */}
            <rect x="0" y="0" width="100%" height="100%" fill="white" />
            {/* Rectángulo negro perfora el foco hacia el elemento con margen óptico */}
            {targetRect && (
              <rect
                x={targetRect.left - 6}
                y={targetRect.top - 6}
                width={targetRect.width + 12}
                height={targetRect.height + 12}
                rx="18"
                ry="18"
                fill="black"
              />
            )}
          </mask>
        </defs>

        {/* Capa oscura que recibe clics para cerrar */}
        <rect
          x="0"
          y="0"
          width="100%"
          height="100%"
          fill="rgba(15, 23, 42, 0.70)"
          mask="url(#ateneo-spotlight-mask)"
          className="pointer-events-auto cursor-pointer"
          onClick={closeTour}
        />

        {/* Halo luminoso de realce alrededor del elemento objetivo */}
        {targetRect && (
          <rect
            x={targetRect.left - 6}
            y={targetRect.top - 6}
            width={targetRect.width + 12}
            height={targetRect.height + 12}
            rx="18"
            ry="18"
            fill="none"
            stroke="url(#ateneo-tour-gradient)"
            strokeWidth="3"
            strokeDasharray="8 6"
            className="animate-pulse"
          />
        )}

        <linearGradient id="ateneo-tour-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="50%" stopColor="#2563eb" />
          <stop offset="100%" stopColor="#7c3aed" />
        </linearGradient>
      </svg>

      {/* Tarjeta Flotante Tooltip en Liquid Glassmorphism */}
      <div
        ref={tooltipRef}
        role="dialog"
        aria-labelledby="tour-step-title"
        aria-describedby="tour-step-desc"
        style={{
          position: 'fixed',
          top: `${tooltipPos.top}px`,
          left: `${tooltipPos.left}px`,
        }}
        className="w-[calc(100vw-2rem)] sm:w-96 max-w-md bg-white/95 backdrop-blur-xl border border-slate-200/90 rounded-[24px] shadow-2xl p-5 space-y-4 animate-scaleUp z-[110]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Flecha Indicadora de Dirección hacia el elemento */}
        {targetRect && tooltipPos.arrowPlacement === 'top' && (
          <div
            style={{ left: `${arrowLeftOffset}px` }}
            className="absolute -top-2.5 -translate-x-1/2 w-0 h-0 border-x-[10px] border-x-transparent border-b-[10px] border-b-white filter drop-shadow-[0_-2px_3px_rgba(0,0,0,0.06)]"
          />
        )}

        {targetRect && tooltipPos.arrowPlacement === 'bottom' && (
          <div
            style={{ left: `${arrowLeftOffset}px` }}
            className="absolute -bottom-2.5 -translate-x-1/2 w-0 h-0 border-x-[10px] border-x-transparent border-t-[10px] border-t-white filter drop-shadow-[0_2px_3px_rgba(0,0,0,0.06)]"
          />
        )}

        {/* Cabecera del Paso */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#0b57d0]">
            <Sparkles className="w-4 h-4 text-[#0b57d0]" />
            <span>Guía Formativa • Paso {currentStepIndex + 1} de {totalSteps}</span>
          </div>
          <button
            type="button"
            onClick={closeTour}
            className="p-1.5 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
            aria-label="Cerrar tour de ayuda"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Contenido Clínico del Paso */}
        <div className="space-y-1.5">
          <h3 id="tour-step-title" className="text-base font-semibold text-slate-900 font-heading leading-snug">
            {step.title}
          </h3>
          <p id="tour-step-desc" className="text-xs text-slate-600 leading-relaxed">
            {step.description}
          </p>
        </div>

        {/* Barra de Navegación y Acciones del Tour */}
        <div className="flex items-center justify-between pt-2">
          {/* Botón Saltar */}
          <button
            type="button"
            onClick={closeTour}
            className="text-[11px] font-medium text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
          >
            Saltar guía
          </button>

          {/* Indicadores de progreso (Dots) */}
          <div className="flex items-center gap-1">
            {CATALOG_TOUR_STEPS.map((_, i) => (
              <span
                key={i}
                className={`h-1.5 rounded-full transition-all ${
                  i === currentStepIndex
                    ? 'w-4 bg-[#0b57d0]'
                    : 'w-1.5 bg-slate-200'
                }`}
              />
            ))}
          </div>

          {/* Botones Anterior / Siguiente */}
          <div className="flex items-center gap-2">
            {currentStepIndex > 0 && (
              <button
                type="button"
                onClick={prevStep}
                className="p-1.5 rounded-full border border-slate-200 text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
                title="Paso anterior"
                aria-label="Paso anterior"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
              </button>
            )}

            <button
              type="button"
              onClick={() => nextStep(totalSteps)}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:opacity-95 text-white text-xs font-medium shadow-xs cursor-pointer active:scale-95 transition-all"
            >
              <span>{isLastStep ? 'Entendido' : 'Siguiente'}</span>
              {isLastStep ? <Check className="w-3.5 h-3.5" /> : <ArrowRight className="w-3.5 h-3.5" />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(content, document.body);
};

export default StudentTourGuide;
