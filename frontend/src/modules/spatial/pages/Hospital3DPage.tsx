import React, { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, ContactShadows, Sky } from '@react-three/drei';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Maximize2,
  Minimize2,
  User,
  Eye
} from 'lucide-react';
import { useSpatialStore } from '../store/useSpatialStore';
import { useCases } from '../../cases/hooks/useCases';
import HospitalWardScene from '../components/HospitalWardScene';
import CharacterController from '../components/CharacterController';
import BedInteractionBadge from '../components/BedInteractionBadge';
import ClinicalBedsideTablet from '../components/ClinicalBedsideTablet';
import MobileTouchControls from '../components/MobileTouchControls';
import LandscapeOrientationNotice from '../components/LandscapeOrientationNotice';

export const Hospital3DPage: React.FC = () => {
  const navigate = useNavigate();
  const { cases } = useCases();

  const containerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isTouchDevice, setIsTouchDevice] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  });
  const [isPortrait, setIsPortrait] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return window.innerHeight > window.innerWidth;
  });

  const beds = useSpatialStore((s) => s.beds);
  const playerPosition = useSpatialStore((s) => s.playerPosition);
  const syncCasesWithBeds = useSpatialStore((s) => s.syncCasesWithBeds);
  const hoveredBedId = useSpatialStore((s) => s.hoveredBedId);
  const openBedInspection = useSpatialStore((s) => s.openBedInspection);
  const cameraMode = useSpatialStore((s) => s.cameraMode);
  const toggleCameraMode = useSpatialStore((s) => s.toggleCameraMode);
  const isInsideOrAtThreshold = playerPosition[0] >= -13.5;

  useEffect(() => {
    if (cases && cases.length > 0) {
      syncCasesWithBeds(cases);
    }
  }, [cases, syncCasesWithBeds]);

  // Detección reactiva de orientación en pantalla y capacidades táctiles
  useEffect(() => {
    const checkOrientation = () => {
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      const portrait = window.innerHeight > window.innerWidth;
      setIsTouchDevice(hasTouch);
      setIsPortrait(portrait);
    };

    checkOrientation();
    window.addEventListener('resize', checkOrientation);
    window.addEventListener('orientationchange', checkOrientation);

    return () => {
      window.removeEventListener('resize', checkOrientation);
      window.removeEventListener('orientationchange', checkOrientation);
    };
  }, []);

  // Manejo reactivo del modo pantalla completa nativo
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  const toggleFullscreen = async () => {
    if (!containerRef.current) return;

    try {
      if (!document.fullscreenElement) {
        await containerRef.current.requestFullscreen();
        if (screen.orientation && 'lock' in screen.orientation) {
          try {
            await (screen.orientation as any).lock('landscape');
          } catch {
            // Silencioso si el navegador móvil no permite bloqueo de orientación por software
          }
        }
      } else if (document.exitFullscreen) {
        await document.exitFullscreen();
      }
    } catch (err) {
      console.error('Error al conmutar pantalla completa:', err);
    }
  };

  const hoveredBed = beds.find((b) => b.id === hoveredBedId);

  return (
    <div
      ref={containerRef}
      className={`w-full overflow-hidden select-none transition-all duration-300 ${
        isFullscreen ? 'h-screen w-screen fixed inset-0 z-50 bg-[#f0f4f9]' : 'relative h-full w-full bg-[#f0f4f9]'
      }`}
    >
      {/* 1. Canvas WebGL/WebGPU Tridimensional con Iluminación PBR */}
      <Canvas
        shadows="percentage"
        camera={{ position: [-33.5, 1.62, 0], fov: 64, near: 0.1, far: 150 }}
        className="w-full h-full cursor-crosshair"
      >
        <color attach="background" args={['#7ec0ee']} />
        <Sky sunPosition={[-45, 32, -15]} turbidity={0.18} rayleigh={0.85} />

        {/* Iluminación Global Solar y Reflejos Fotorrealistas */}
        <ambientLight intensity={1.15} color="#ffffff" />
        <hemisphereLight args={['#f8fafc', '#cbd5e1', 0.75]} />
        <directionalLight
          position={[-28, 26, -12]}
          intensity={1.35}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-near={0.5}
          shadow-camera-far={80}
          shadow-camera-left={-36}
          shadow-camera-right={18}
          shadow-camera-top={24}
          shadow-camera-bottom={-24}
        />

        {/* Mapa de Entorno Interior/Exterior para Reflejos Metálicos y Muro Cortina */}
        <Environment preset="city" />

        {/* Sombras de Contacto Suaves sobre el Suelo del Campus y Pabellón */}
        <ContactShadows
          position={[-10, 0.01, 0]}
          opacity={0.42}
          scale={56}
          blur={1.8}
          far={4.0}
          color="#0f172a"
        />

        {/* Escenario PBR de la Sala de Urgencias y Choque */}
        <HospitalWardScene />

        {/* Controlador Cinemático en Primera Persona */}
        <CharacterController />

        {/* Rótulos Diegéticos HTML Flotantes sobre las Camas (visibles al cruzar el umbral interior) */}
        {isInsideOrAtThreshold &&
          beds.map((bed) => (
            <BedInteractionBadge
              key={bed.id}
              bed={bed}
              isHovered={hoveredBedId === bed.id}
              onClick={() => openBedInspection(bed.id)}
            />
          ))}
      </Canvas>

      {/* 2. HUD Superior: Navegación, Triaje y Pantalla Completa (Liquid Glassmorphism Ateneo+) */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between pointer-events-none z-10">
        {/* Lado Izquierdo: Volver al Catálogo */}
        <div className="flex items-center space-x-3 pointer-events-auto">
          <button
            onClick={() => navigate('/cases')}
            className="px-3.5 py-2 bg-white/90 hover:bg-white text-slate-800 rounded-full border border-slate-200/80 shadow-xs backdrop-blur-md transition-all flex items-center space-x-2 text-xs font-semibold hover:border-blue-300 cursor-pointer"
            title="Volver al Catálogo 2D"
          >
            <ArrowLeft className="w-4 h-4 text-[#0b57d0]" />
            <span className="hidden sm:inline">Catálogo</span>
          </button>
        </div>

        {/* Lado Derecho: Conmutador de Perspectiva y Pantalla Completa */}
        <div className="flex items-center space-x-2.5 pointer-events-auto">
          {/* Conmutador de Perspectiva 3ª Persona / 1ª Persona */}
          <button
            onClick={toggleCameraMode}
            className="px-3.5 py-2 bg-white/90 hover:bg-white text-slate-800 rounded-full border border-slate-200/80 shadow-xs backdrop-blur-md transition-all flex items-center space-x-2 text-xs font-semibold hover:border-blue-300 cursor-pointer"
            title={cameraMode === 'third-person' ? 'Cambiar a 1ª Persona' : 'Cambiar a 3ª Persona (Avatar Médico)'}
            aria-label="Conmutar perspectiva de cámara"
          >
            {cameraMode === 'third-person' ? (
              <>
                <User className="w-4 h-4 text-[#0b57d0]" />
                <span className="hidden sm:inline">3ª Persona</span>
              </>
            ) : (
              <>
                <Eye className="w-4 h-4 text-[#0b57d0]" />
                <span className="hidden sm:inline">1ª Persona</span>
              </>
            )}
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-2.5 bg-white/90 hover:bg-white text-slate-800 rounded-full border border-slate-200/80 shadow-xs backdrop-blur-md transition-all flex items-center justify-center hover:border-blue-300"
            title={isFullscreen ? 'Salir de Pantalla Completa (Esc)' : 'Ver en Pantalla Completa'}
            aria-label={isFullscreen ? 'Salir de Pantalla Completa' : 'Ver en Pantalla Completa'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4 text-[#0b57d0]" />
            ) : (
              <Maximize2 className="w-4 h-4 text-[#0b57d0]" />
            )}
          </button>
        </div>
      </div>

      {/* 3. Indicador de Interacción Central en Escritorio (Prompt contextual Ateneo+) */}
      {!isTouchDevice && hoveredBed && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 pointer-events-none animate-fadeIn z-10">
          <div className="bg-white/95 backdrop-blur-xl text-slate-900 px-5 py-2.5 rounded-full border border-blue-300/80 shadow-xl flex items-center space-x-2.5 text-xs sm:text-sm">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500 animate-ping" />
            <span>
              <strong className="font-bold text-slate-900">Cama {hoveredBed.bedNumber}:</strong>{' '}
              <span className="text-slate-600 font-medium">{hoveredBed.label}</span>
            </span>
            <span className="text-slate-300">•</span>
            <span>
              Presiona{' '}
              <kbd className="bg-slate-100 px-1.5 py-0.5 rounded text-[11px] font-mono border border-slate-300 text-slate-800 font-semibold shadow-2xs">
                E
              </kbd>{' '}
              o{' '}
              <button
                onClick={() => openBedInspection(hoveredBed.id)}
                className="pointer-events-auto text-[#0b57d0] underline font-semibold hover:text-blue-700"
              >
                examinar
              </button>
            </span>
          </div>
        </div>
      )}

      {/* 4. Controles Táctiles y Joystick Virtual para Dispositivos Móviles (en Modo Horizontal) */}
      {isTouchDevice && !isPortrait && <MobileTouchControls />}

      {/* 5. Bloqueo y Exigencia Institucional de Modo Horizontal en Dispositivos Móviles */}
      {isTouchDevice && isPortrait && (
        <LandscapeOrientationNotice onRequestFullscreen={toggleFullscreen} />
      )}

      {/* 6. Tableta Clínica Diegética Superpuesta */}
      <ClinicalBedsideTablet />
    </div>
  );
};

export default Hospital3DPage;
