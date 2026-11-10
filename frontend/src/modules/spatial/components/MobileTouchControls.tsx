import React, { useRef, useState, useCallback, useEffect } from 'react';
import {
  Zap,
  RotateCcw,
  RotateCw,
  Stethoscope
} from 'lucide-react';
import { useSpatialStore } from '../store/useSpatialStore';

export const MobileTouchControls: React.FC = () => {
  const isTabletOpen = useSpatialStore((s) => s.isTabletOpen);
  const hoveredBedId = useSpatialStore((s) => s.hoveredBedId);
  const beds = useSpatialStore((s) => s.beds);
  const openBedInspection = useSpatialStore((s) => s.openBedInspection);
  const setTouchMove = useSpatialStore((s) => s.setTouchMove);
  const setTouchSprinting = useSpatialStore((s) => s.setTouchSprinting);
  const addTouchLookDelta = useSpatialStore((s) => s.addTouchLookDelta);

  const [isSprinting, setIsSprinting] = useState<boolean>(false);
  const [knobPos, setKnobPos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isJoystickActive, setIsJoystickActive] = useState<boolean>(false);

  const joystickBaseRef = useRef<HTMLDivElement>(null);
  const activePointerIdRef = useRef<number | null>(null);
  const lookPointerIdRef = useRef<number | null>(null);
  const lastLookPosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const hoveredBed = beds.find((b) => b.id === hoveredBedId);

  // Toggle de correr / sprint
  const toggleSprint = useCallback(() => {
    setIsSprinting((prev) => {
      const next = !prev;
      setTouchSprinting(next);
      return next;
    });
  }, [setTouchSprinting]);

  // Rotación rápida mediante toques de botón (giro de 45 grados)
  const handleQuickTurn = useCallback(
    (direction: 'left' | 'right') => {
      const angleDelta = direction === 'left' ? -220 : 220;
      addTouchLookDelta(angleDelta, 0);
    },
    [addTouchLookDelta]
  );

  // =========================================================================
  // GESTIÓN DEL JOYSTICK VIRTUAL ANÁLOGO
  // =========================================================================
  const handleJoystickPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (activePointerIdRef.current !== null) return;
    activePointerIdRef.current = e.pointerId;
    e.currentTarget.setPointerCapture(e.pointerId);
    setIsJoystickActive(true);

    updateJoystickPosition(e.clientX, e.clientY);
  };

  const updateJoystickPosition = (clientX: number, clientY: number) => {
    if (!joystickBaseRef.current) return;
    const rect = joystickBaseRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const deltaX = clientX - centerX;
    const deltaY = clientY - centerY;
    const distance = Math.hypot(deltaX, deltaY);
    const maxRadius = rect.width / 2 - 16; // Radio máximo permitido

    let clampedX = deltaX;
    let clampedY = deltaY;

    if (distance > maxRadius) {
      const angle = Math.atan2(deltaY, deltaX);
      clampedX = Math.cos(angle) * maxRadius;
      clampedY = Math.sin(angle) * maxRadius;
    }

    setKnobPos({ x: clampedX, y: clampedY });

    // Normalizar entre -1.0 y 1.0 (X: derecha/izquierda, Y: adelante/atrás)
    const normalizedX = clampedX / maxRadius;
    const normalizedY = -clampedY / maxRadius; // Arriba en pantalla es avanzar (+Y en espacio local)

    setTouchMove(normalizedX, normalizedY);
  };

  const handleJoystickPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (activePointerIdRef.current !== e.pointerId) return;
    updateJoystickPosition(e.clientX, e.clientY);
  };

  const handleJoystickPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (activePointerIdRef.current !== e.pointerId) return;
    activePointerIdRef.current = null;
    setIsJoystickActive(false);
    setKnobPos({ x: 0, y: 0 });
    setTouchMove(0, 0);
  };

  // =========================================================================
  // GESTIÓN DE SUPERFICIE DE VISTA / TOUCH-LOOK
  // =========================================================================
  const handleLookPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (lookPointerIdRef.current !== null) return;
    lookPointerIdRef.current = e.pointerId;
    e.currentTarget.setPointerCapture(e.pointerId);
    lastLookPosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleLookPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (lookPointerIdRef.current !== e.pointerId) return;
    const dx = e.clientX - lastLookPosRef.current.x;
    const dy = e.clientY - lastLookPosRef.current.y;

    addTouchLookDelta(dx, dy);
    lastLookPosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleLookPointerUp = (e: React.PointerEvent<HTMLDivElement>) => {
    if (lookPointerIdRef.current !== e.pointerId) return;
    lookPointerIdRef.current = null;
  };

  // Reset al desmontar
  useEffect(() => {
    return () => {
      setTouchMove(0, 0);
      setTouchSprinting(false);
    };
  }, [setTouchMove, setTouchSprinting]);

  if (isTabletOpen) return null;

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-20 overflow-hidden">
      {/* 1. Superficie de rotación de vista (Mitad derecha de la pantalla) */}
      <div
        className="absolute top-16 bottom-24 right-0 w-[55vw] pointer-events-auto touch-none"
        onPointerDown={handleLookPointerDown}
        onPointerMove={handleLookPointerMove}
        onPointerUp={handleLookPointerUp}
        onPointerCancel={handleLookPointerUp}
      />

      {/* 2. Joystick Virtual Análogo (Lado Inferior Izquierdo) */}
      <div className="absolute bottom-5 left-6 pointer-events-auto touch-none">
        <div
          ref={joystickBaseRef}
          onPointerDown={handleJoystickPointerDown}
          onPointerMove={handleJoystickPointerMove}
          onPointerUp={handleJoystickPointerUp}
          onPointerCancel={handleJoystickPointerUp}
          className={`w-32 h-32 rounded-full border flex items-center justify-center transition-colors relative backdrop-blur-md shadow-xl ${
            isJoystickActive
              ? 'bg-slate-900/40 border-cyan-400/60 shadow-cyan-500/20'
              : 'bg-slate-900/25 border-white/40 shadow-black/20'
          }`}
        >
          {/* Guías cardinales discretas */}
          <div className="absolute top-2 w-1.5 h-1.5 rounded-full bg-white/50" />
          <div className="absolute bottom-2 w-1.5 h-1.5 rounded-full bg-white/50" />
          <div className="absolute left-2 w-1.5 h-1.5 rounded-full bg-white/50" />
          <div className="absolute right-2 w-1.5 h-1.5 rounded-full bg-white/50" />

          {/* Perilla análoga deslizable */}
          <div
            style={{
              transform: `translate3d(${knobPos.x}px, ${knobPos.y}px, 0)`
            }}
            className={`w-14 h-14 rounded-full border transition-shadow flex items-center justify-center shadow-lg ${
              isJoystickActive
                ? 'bg-white border-cyan-400 shadow-cyan-400/50 scale-105'
                : 'bg-white/90 border-slate-200/90'
            }`}
          >
            <div className="w-4 h-4 rounded-full bg-[#0b57d0]/80" />
          </div>
        </div>
      </div>

      {/* 3. Botonera de Acción y Navegación Rápida (Lado Inferior Derecho) */}
      <div className="absolute bottom-5 right-6 pointer-events-auto flex items-end space-x-3">
        {/* Botón contextual de Inspección de Cama si el médico está cerca */}
        {hoveredBed && (
          <button
            type="button"
            onClick={() => openBedInspection(hoveredBed.id)}
            className="px-4 py-3 bg-[#0b57d0] hover:bg-blue-700 text-white rounded-full border border-blue-300 shadow-xl backdrop-blur-md transition-all flex items-center space-x-2 text-xs font-bold animate-pulse cursor-pointer"
          >
            <Stethoscope className="w-4 h-4 text-cyan-300" />
            <span>Examinar Cama {hoveredBed.bedNumber}</span>
          </button>
        )}

        {/* Botones de rotación rápida de cámara (45°) */}
        <div className="flex flex-col space-y-2">
          <button
            type="button"
            onClick={() => handleQuickTurn('left')}
            className="p-3 bg-white/85 active:bg-white text-slate-800 rounded-full border border-slate-200/80 shadow-md backdrop-blur-md transition-all flex items-center justify-center hover:border-blue-300"
            title="Girar 45° a la izquierda"
            aria-label="Girar a la izquierda"
          >
            <RotateCcw className="w-4 h-4 text-[#0b57d0]" />
          </button>
          <button
            type="button"
            onClick={() => handleQuickTurn('right')}
            className="p-3 bg-white/85 active:bg-white text-slate-800 rounded-full border border-slate-200/80 shadow-md backdrop-blur-md transition-all flex items-center justify-center hover:border-blue-300"
            title="Girar 45° a la derecha"
            aria-label="Girar a la derecha"
          >
            <RotateCw className="w-4 h-4 text-[#0b57d0]" />
          </button>
        </div>

        {/* Botón conmutador de Correr / Sprint */}
        <button
          type="button"
          onClick={toggleSprint}
          className={`px-3.5 py-3 rounded-full border shadow-lg backdrop-blur-md transition-all flex items-center space-x-1.5 text-xs font-semibold cursor-pointer ${
            isSprinting
              ? 'bg-[#0b57d0] text-white border-blue-400 shadow-blue-500/30 ring-2 ring-blue-300'
              : 'bg-white/85 text-slate-800 border-slate-200/80 hover:border-blue-300'
          }`}
          title={isSprinting ? 'Corriendo (Velocidad x2)' : 'Caminar (Toca para correr)'}
        >
          <Zap className={`w-4 h-4 ${isSprinting ? 'text-amber-300 fill-amber-300' : 'text-[#0b57d0]'}`} />
          <span className="hidden sm:inline">{isSprinting ? 'Corriendo' : 'Caminar'}</span>
        </button>
      </div>
    </div>
  );
};

export default MobileTouchControls;
