import React, { useRef, useState, useCallback, useEffect } from 'react';
import { Stethoscope } from 'lucide-react';
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

  // Alternar entre modo Caminar y Correr
  const toggleSprint = useCallback(() => {
    setIsSprinting((prev) => {
      const next = !prev;
      setTouchSprinting(next);
      return next;
    });
  }, [setTouchSprinting]);

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
    const maxRadius = rect.width / 2 - 18; // Radio máximo de desplazamiento

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
    const normalizedY = -clampedY / maxRadius;

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

      {/* 2. Joystick Virtual Análogo (Diseño Clínico Translúcido de Precisión Ateneo+) */}
      <div className="absolute bottom-6 left-6 pointer-events-auto touch-none">
        <div
          ref={joystickBaseRef}
          onPointerDown={handleJoystickPointerDown}
          onPointerMove={handleJoystickPointerMove}
          onPointerUp={handleJoystickPointerUp}
          onPointerCancel={handleJoystickPointerUp}
          className={`w-36 h-36 rounded-full border transition-all relative backdrop-blur-sm select-none flex items-center justify-center ${
            isJoystickActive
              ? 'bg-blue-950/10 border-[#0b57d0]/60 shadow-lg shadow-blue-500/15'
              : 'bg-slate-900/5 border-slate-400/35 shadow-xs'
          }`}
        >
          {/* Marcas de orientación cardinal sutiles tipo retícula médica */}
          <div className="absolute top-2 w-0.5 h-2 bg-slate-400/50 rounded-full" />
          <div className="absolute bottom-2 w-0.5 h-2 bg-slate-400/50 rounded-full" />
          <div className="absolute left-2 w-2 h-0.5 bg-slate-400/50 rounded-full" />
          <div className="absolute right-2 w-2 h-0.5 bg-slate-400/50 rounded-full" />

          {/* Anillo concéntrico sutil de rango */}
          <div className="absolute w-24 h-24 rounded-full border border-slate-400/15 pointer-events-none" />

          {/* Lente análoga deslizable en cristal óptico azul Ateneo+ (sin parches blancos opacos) */}
          <div
            style={{
              transform: `translate3d(${knobPos.x}px, ${knobPos.y}px, 0)`
            }}
            className={`w-14 h-14 rounded-full border-2 transition-all flex items-center justify-center backdrop-blur-md shadow-sm ${
              isJoystickActive
                ? 'bg-[#0b57d0]/25 border-[#0b57d0] shadow-blue-500/30 scale-105'
                : 'bg-white/40 border-[#0b57d0]/60 shadow-slate-900/10'
            }`}
          >
            {/* Punto focal central en azul institucional */}
            <div
              className={`w-3.5 h-3.5 rounded-full transition-transform ${
                isJoystickActive ? 'bg-[#0b57d0] scale-110' : 'bg-[#0b57d0]/80'
              }`}
            />
          </div>
        </div>
      </div>

      {/* 3. Botonera de Acción y Desplazamiento (Lado Inferior Derecho) */}
      <div className="absolute bottom-6 right-6 pointer-events-auto flex items-center space-x-3">
        {/* Botón contextual de Inspección de Cama si el médico está cerca */}
        {hoveredBed && (
          <button
            type="button"
            onClick={() => openBedInspection(hoveredBed.id)}
            className="px-5 py-2.5 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-700 hover:via-blue-700 hover:to-indigo-700 text-white rounded-full font-medium text-xs shadow-md shadow-blue-500/20 hover:shadow-lg transition-all flex items-center space-x-2 animate-pulse cursor-pointer"
          >
            <Stethoscope className="w-4 h-4 text-white" />
            <span>Examinar Cama {hoveredBed.bedNumber}</span>
          </button>
        )}

        {/* Botón de alternancia Caminar / Correr (estrictamente texto plano, translúcido sutil) */}
        <button
          type="button"
          onClick={toggleSprint}
          className={`px-5 py-2.5 rounded-full border shadow-xs backdrop-blur-md transition-all text-xs font-semibold tracking-wide cursor-pointer active:scale-95 ${
            isSprinting
              ? 'bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white border-blue-400 shadow-md shadow-blue-500/25'
              : 'bg-white/70 hover:bg-white/90 text-slate-700 border-slate-300/80 hover:border-blue-300'
          }`}
          title={isSprinting ? 'Modo Correr activo' : 'Modo Caminar activo'}
        >
          <span>{isSprinting ? 'Correr' : 'Caminar'}</span>
        </button>
      </div>
    </div>
  );
};

export default MobileTouchControls;
