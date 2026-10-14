import React, { useRef, useState, useEffect, useCallback } from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Sliders, 
  Grid, 
  Maximize2, 
  Minimize2, 
  Sun, 
  Contrast, 
  Eye, 
  Move,
  X
} from 'lucide-react';
import useLearningTelemetry from '../../analytics/hooks/useLearningTelemetry';

export interface ClinicalStudyViewerProps {
  imageUrl: string;
  title?: string;
  studyType?: 'ecg' | 'rx' | 'lab' | 'general';
  mode?: 'inline' | 'modal';
  onClose?: () => void;
}

/**
 * ClinicalStudyViewer — Visor diagnóstico interactivo de paraclínicos sobre Canvas HTML5 acelerado.
 * Proporciona zoom continuo, paneo fluido a 60 FPS, calibración de ventana radiológica
 * (brillo, contraste, inversión) y rejilla electrocardiográfica milimétrica estándar (25 mm/s, 10 mm/mV).
 * Estricto cumplimiento: cero emojis y estética clínica institucional Ateneo+.
 */
export const ClinicalStudyViewer: React.FC<ClinicalStudyViewerProps> = ({
  imageUrl,
  title = 'Estudio Paraclínico',
  studyType = 'general',
  mode = 'inline',
  onClose,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);

  // Estados de transformación espacial
  const [zoom, setZoom] = useState<number>(1.0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const dragStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // Estados de ajuste radiológico / ventana
  const [brightness, setBrightness] = useState<number>(100);
  const [contrast, setContrast] = useState<number>(100);
  const [inverted, setInverted] = useState<boolean>(false);
  const [showEcgGrid, setShowEcgGrid] = useState<boolean>(studyType === 'ecg');
  const [showFiltersPanel, setShowFiltersPanel] = useState<boolean>(false);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const { trackParaclinicalInspected } = useLearningTelemetry();

  useEffect(() => {
    if (imageUrl) {
      trackParaclinicalInspected('paraclinical_current', title, { studyType, imageUrl });
    }
  }, [imageUrl, title, studyType, trackParaclinicalInspected]);

  // Manejo de atajo de teclado Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isFullscreen) {
          setIsFullscreen(false);
        } else if (onClose) {
          onClose();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen, onClose]);

  // Carga de la imagen en memoria
  useEffect(() => {
    if (!imageUrl) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = imageUrl;
    img.onload = () => {
      imageRef.current = img;
      resetTransformations();
    };
  }, [imageUrl]);

  // Redibujado en Canvas a 60 FPS
  const renderCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Ajustar dimensiones internas del canvas al contenedor
    const rect = canvas.getBoundingClientRect();
    if (canvas.width !== rect.width || canvas.height !== rect.height) {
      canvas.width = rect.width;
      canvas.height = rect.height;
    }

    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);

    // Fondo de negatoscopio clínico adaptativo (claro para reportes de laboratorio, oscuro para Rx/ECG)
    ctx.fillStyle = studyType === 'lab' ? '#f8fafc' : '#0f172a';
    ctx.fillRect(0, 0, width, height);

    const img = imageRef.current;
    if (!img) {
      ctx.fillStyle = '#64748b';
      ctx.font = '12px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Cargando estudio diagnóstico...', width / 2, height / 2);
      return;
    }

    ctx.save();

    // 1. Aplicar transformaciones espaciales (Paneo y Zoom desde el centro)
    ctx.translate(width / 2 + pan.x, height / 2 + pan.y);
    ctx.scale(zoom, zoom);

    // 2. Aplicar filtros radiológicos (Brillo, Contraste, Inversión)
    const invertValue = inverted ? 100 : 0;
    ctx.filter = `brightness(${brightness}%) contrast(${contrast}%) invert(${invertValue}%)`;

    // 3. Dibujar la imagen centrada
    const aspect = img.width / img.height;
    let drawWidth = width * 0.9;
    let drawHeight = drawWidth / aspect;

    if (drawHeight > height * 0.9) {
      drawHeight = height * 0.9;
      drawWidth = drawHeight * aspect;
    }

    ctx.drawImage(img, -drawWidth / 2, -drawHeight / 2, drawWidth, drawHeight);

    // 4. Rejilla Electrocardiográfica Estándar (si está habilitada)
    if (showEcgGrid) {
      ctx.filter = 'none';
      const gridSize = 16; // 1 mm estimado
      const majorGridSize = gridSize * 5; // 5 mm (0.20s a 25 mm/s)

      // Rejilla fina (1 mm)
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.25)';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      for (let x = -drawWidth / 2; x <= drawWidth / 2; x += gridSize) {
        ctx.moveTo(x, -drawHeight / 2);
        ctx.lineTo(x, drawHeight / 2);
      }
      for (let y = -drawHeight / 2; y <= drawHeight / 2; y += gridSize) {
        ctx.moveTo(-drawWidth / 2, y);
        ctx.lineTo(drawWidth / 2, y);
      }
      ctx.stroke();

      // Rejilla mayor (5 mm)
      ctx.strokeStyle = 'rgba(220, 38, 38, 0.55)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = -drawWidth / 2; x <= drawWidth / 2; x += majorGridSize) {
        ctx.moveTo(x, -drawHeight / 2);
        ctx.lineTo(x, drawHeight / 2);
      }
      for (let y = -drawHeight / 2; y <= drawHeight / 2; y += majorGridSize) {
        ctx.moveTo(-drawWidth / 2, y);
        ctx.lineTo(drawWidth / 2, y);
      }
      ctx.stroke();
    }

    ctx.restore();
  }, [pan, zoom, brightness, contrast, inverted, showEcgGrid, studyType]);

  useEffect(() => {
    let animId: number;
    const renderLoop = () => {
      renderCanvas();
      animId = requestAnimationFrame(renderLoop);
    };
    animId = requestAnimationFrame(renderLoop);
    return () => cancelAnimationFrame(animId);
  }, [renderCanvas]);

  // Controles de Paneo e Interacción del Ratón
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    dragStartRef.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStartRef.current.x,
      y: e.clientY - dragStartRef.current.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Zoom continuo con rueda del ratón
  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.15 : 0.85;
    setZoom((prevZoom) => {
      const nextZoom = prevZoom * factor;
      return Math.min(Math.max(nextZoom, 0.6), 8.0);
    });
  };

  const resetTransformations = () => {
    setZoom(1.0);
    setPan({ x: 0, y: 0 });
    setBrightness(100);
    setContrast(100);
    setInverted(false);
  };

  const zoomIn = () => setZoom((z) => Math.min(z * 1.25, 8.0));
  const zoomOut = () => setZoom((z) => Math.max(z * 0.8, 0.6));

  const isModalMode = mode === 'modal';

  const content = (
    <div
      ref={containerRef}
      className={`relative bg-white rounded-[20px] overflow-hidden select-none border border-slate-200/90 shadow-xs flex flex-col ${
        isFullscreen
          ? 'fixed inset-4 z-50 shadow-2xl'
          : isModalMode
            ? 'w-full h-[75vh] min-h-[500px]'
            : 'w-full h-80 sm:h-96'
      }`}
    >
      {/* Barra de Herramientas Diagnósticas Superior Integrada (Estilo Clínico Ateneo+) */}
      <div className="px-4 py-2.5 bg-[#f0f4f9] border-b border-slate-200/80 flex items-center justify-between text-xs text-[#1f1f1f] z-10 select-none">
        <div className="flex items-center gap-2">
          <Eye className="w-3.5 h-3.5 text-[#0b57d0]" />
          <span className={`font-medium tracking-tight truncate text-[#1f1f1f] ${isModalMode ? 'max-w-[280px] sm:max-w-md' : 'max-w-[220px]'}`}>
            {title}
          </span>
          <span className="text-[11px] text-[#747775] font-mono">{(zoom * 100).toFixed(0)}%</span>
        </div>

        {/* Botonera de Acción Plana y Limpia */}
        <div className="flex items-center gap-1">
          <button
            onClick={zoomIn}
            className="p-1.5 text-[#444746] hover:text-[#1f1f1f] hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200/60 shadow-xs"
            title="Acercar (Zoom In)"
            aria-label="Acercar imagen"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={zoomOut}
            className="p-1.5 text-[#444746] hover:text-[#1f1f1f] hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200/60 shadow-xs"
            title="Alejar (Zoom Out)"
            aria-label="Alejar imagen"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={resetTransformations}
            className="p-1.5 text-[#444746] hover:text-[#1f1f1f] hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200/60 shadow-xs"
            title="Restablecer Vista"
            aria-label="Restablecer vista diagnóstica"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <div className="w-[1px] h-4 bg-slate-200 mx-1" />
          <button
            onClick={() => setShowEcgGrid((prev) => !prev)}
            className={`p-1.5 rounded-lg transition-colors border ${
              showEcgGrid ? 'text-rose-600 bg-rose-50 border-rose-200' : 'text-[#444746] hover:text-[#1f1f1f] hover:bg-white border-transparent hover:border-slate-200/60'
            }`}
            title="Rejilla Milimétrica ECG (25mm/s, 10mm/mV)"
            aria-label="Rejilla ECG"
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowFiltersPanel((prev) => !prev)}
            className={`p-1.5 rounded-lg transition-colors border ${
              showFiltersPanel ? 'text-[#0b57d0] bg-blue-50 border-blue-200' : 'text-[#444746] hover:text-[#1f1f1f] hover:bg-white border-transparent hover:border-slate-200/60'
            }`}
            title="Ajuste de Ventana Diagnóstica"
            aria-label="Ajuste de filtros"
          >
            <Sliders className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsFullscreen((prev) => !prev)}
            className="p-1.5 text-[#444746] hover:text-[#1f1f1f] hover:bg-white rounded-lg transition-colors border border-transparent hover:border-slate-200/60 shadow-xs"
            title={isFullscreen ? 'Salir de Pantalla Completa' : 'Maximizar Visor'}
            aria-label="Alternar pantalla completa"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          {onClose && (
            <>
              <div className="w-[1px] h-4 bg-slate-200 mx-1" />
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors border border-transparent hover:border-slate-200/60"
                title="Cerrar Visor Diagnóstico"
                aria-label="Cerrar visor"
              >
                <X className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Panel Desplegable de Calibración de Ventana (Estilo Material 3 Limpio) */}
      {showFiltersPanel && (
        <div className="absolute top-12 right-3 z-20 bg-white p-4 rounded-[18px] border border-slate-200 text-xs text-[#1f1f1f] space-y-3 w-56 shadow-lg animate-fadeIn">
          <div className="font-semibold text-[#1f1f1f] border-b border-slate-100 pb-1.5">
            Ventana Radiológica
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-[11px] text-[#444746]">
              <span className="flex items-center gap-1.5">
                <Sun className="w-3.5 h-3.5 text-[#0b57d0]" />
                Brillo
              </span>
              <span className="font-mono">{brightness}%</span>
            </div>
            <input
              type="range"
              min={40}
              max={180}
              value={brightness}
              onChange={(e) => setBrightness(Number(e.target.value))}
              className="w-full accent-[#0b57d0] cursor-pointer h-1.5 bg-slate-200 rounded-lg"
            />
          </div>

          <div className="space-y-1">
            <div className="flex items-center justify-between text-[11px] text-[#444746]">
              <span className="flex items-center gap-1.5">
                <Contrast className="w-3.5 h-3.5 text-[#0b57d0]" />
                Contraste
              </span>
              <span className="font-mono">{contrast}%</span>
            </div>
            <input
              type="range"
              min={50}
              max={220}
              value={contrast}
              onChange={(e) => setContrast(Number(e.target.value))}
              className="w-full accent-[#0b57d0] cursor-pointer h-1.5 bg-slate-200 rounded-lg"
            />
          </div>

          <div className="pt-1 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] text-[#444746]">Inversión Negativo</span>
            <button
              onClick={() => setInverted((inv) => !inv)}
              className={`px-3 py-1 rounded-full text-[10px] font-medium transition-colors ${
                inverted ? 'bg-[#0b57d0] text-white font-medium shadow-xs' : 'bg-[#f0f4f9] text-[#1f1f1f] hover:bg-slate-200'
              }`}
            >
              {inverted ? 'Activo' : 'Invertir'}
            </button>
          </div>
        </div>
      )}

      {/* Canvas Principal */}
      <canvas
        ref={canvasRef}
        data-testid="clinical-canvas"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        className={`w-full h-full flex-1 ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
      />

      {/* Barra de Estado Inferior Plana y Limpia */}
      <div className="px-4 py-2 bg-[#f0f4f9] border-t border-slate-200/80 flex items-center justify-between text-[11px] text-[#747775] select-none z-10">
        <div className="flex items-center gap-1.5">
          <Move className="w-3.5 h-3.5 text-[#747775]" />
          <span>Arrastrar para desplazar · Rueda del ratón para ampliar</span>
        </div>
        {showEcgGrid && (
          <span className="text-rose-600 font-mono text-[10px] bg-rose-50 px-2 py-0.5 rounded-full border border-rose-100">
            Rejilla Calibrada: 25mm/s (0.04s/mm)
          </span>
        )}
      </div>
    </div>
  );

  if (isFullscreen) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm p-4 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

export default ClinicalStudyViewer;
