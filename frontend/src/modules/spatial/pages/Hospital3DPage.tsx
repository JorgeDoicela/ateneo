import React, { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, ContactShadows } from '@react-three/drei';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  ShieldAlert,
  CheckCircle2,
  Activity,
  Users,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { useSpatialStore } from '../store/useSpatialStore';
import { useCases } from '../../cases/hooks/useCases';
import HospitalWardScene from '../components/HospitalWardScene';
import CharacterController from '../components/CharacterController';
import BedInteractionBadge from '../components/BedInteractionBadge';
import ClinicalBedsideTablet from '../components/ClinicalBedsideTablet';

export const Hospital3DPage: React.FC = () => {
  const navigate = useNavigate();
  const { cases } = useCases();

  const containerRef = useRef<HTMLDivElement>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const beds = useSpatialStore((s) => s.beds);
  const syncCasesWithBeds = useSpatialStore((s) => s.syncCasesWithBeds);
  const hoveredBedId = useSpatialStore((s) => s.hoveredBedId);
  const openBedInspection = useSpatialStore((s) => s.openBedInspection);

  useEffect(() => {
    if (cases && cases.length > 0) {
      syncCasesWithBeds(cases);
    }
  }, [cases, syncCasesWithBeds]);

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
      } else if (document.exitFullscreen) {
        await document.exitFullscreen();
      }
    } catch (err) {
      console.error('Error al conmutar pantalla completa:', err);
    }
  };

  const hoveredBed = beds.find((b) => b.id === hoveredBedId);
  const activeRedCodes = beds.filter((b) => b.urgency === 'codigo_rojo' && !b.isSolved).length;
  const solvedCount = beds.filter((b) => b.isSolved).length;

  return (
    <div
      ref={containerRef}
      className={`relative w-full overflow-hidden select-none transition-all duration-300 ${
        isFullscreen ? 'h-screen w-screen fixed inset-0 z-50 bg-[#f0f4f9]' : 'h-[calc(100vh-4rem)] bg-[#f0f4f9]'
      }`}
    >
      {/* 1. Canvas WebGL/WebGPU Tridimensional con Iluminación PBR */}
      <Canvas
        shadows
        camera={{ position: [-9.2, 1.68, 0], fov: 62, near: 0.1, far: 50 }}
        className="w-full h-full cursor-crosshair"
      >
        <color attach="background" args={['#e2e8f0']} />

        {/* Iluminación Global y Reflejos Fotorrealistas */}
        <ambientLight intensity={1.1} color="#ffffff" />
        <hemisphereLight args={['#f8fafc', '#cbd5e1', 0.65]} />
        <directionalLight
          position={[4, 10, 4]}
          intensity={0.9}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-near={0.5}
          shadow-camera-far={25}
          shadow-camera-left={-12}
          shadow-camera-right={12}
          shadow-camera-top={12}
          shadow-camera-bottom={-12}
        />

        {/* Mapa de Entorno Interior para Reflejos Metálicos y Vinilo */}
        <Environment preset="city" />

        {/* Sombras de Contacto Suaves sobre el Suelo */}
        <ContactShadows
          position={[0, 0.01, 0]}
          opacity={0.45}
          scale={26}
          blur={1.8}
          far={3.5}
          color="#0f172a"
        />

        {/* Escenario PBR de la Sala de Urgencias y Choque */}
        <HospitalWardScene />

        {/* Controlador Cinemático en Primera Persona */}
        <CharacterController />

        {/* Rótulos Diegéticos HTML Flotantes sobre las Camas */}
        {beds.map((bed) => (
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
        {/* Lado Izquierdo: Volver y Título Institucional */}
        <div className="flex items-center space-x-3 pointer-events-auto">
          {!isFullscreen && (
            <button
              onClick={() => navigate('/cases')}
              className="px-3.5 py-2 bg-white/90 hover:bg-white text-slate-800 rounded-full border border-slate-200/80 shadow-xs backdrop-blur-md transition-all flex items-center space-x-2 text-xs font-semibold hover:border-blue-300"
              title="Volver al Catálogo 2D"
            >
              <ArrowLeft className="w-4 h-4 text-[#0b57d0]" />
              <span className="hidden sm:inline">Catálogo</span>
            </button>
          )}

          <div className="bg-white/90 backdrop-blur-md rounded-[20px] border border-white/80 px-4 py-2 shadow-xs">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-600 animate-pulse" />
              <h1 className="text-xs font-bold text-slate-900 tracking-tight">
                Simulador Hospitalario 3D
              </h1>
              <span className="text-[10px] font-black tracking-tight text-slate-900">
                ATENEO<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600">+</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Pabellón de Urgencias y Choque • GPC Ecuador</p>
          </div>
        </div>

        {/* Lado Derecho: Estadísticas de Triaje y Botón Pantalla Completa */}
        <div className="flex items-center space-x-2.5 pointer-events-auto">
          <div className="hidden md:flex items-center space-x-2 bg-white/90 backdrop-blur-md rounded-full border border-slate-200/80 px-3.5 py-2 text-xs text-slate-700 shadow-xs">
            <div className="flex items-center space-x-1 px-2 border-r border-slate-200">
              <Users className="w-3.5 h-3.5 text-[#2563eb]" />
              <span className="font-medium">{beds.length} Camas</span>
            </div>
            <div className="flex items-center space-x-1 px-2 border-r border-slate-200">
              <ShieldAlert className="w-3.5 h-3.5 text-red-500" />
              <span className={activeRedCodes > 0 ? 'text-red-600 font-bold' : 'font-medium'}>
                {activeRedCodes} Código Rojo
              </span>
            </div>
            <div className="flex items-center space-x-1 px-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-emerald-700 font-medium">{solvedCount} Resueltos</span>
            </div>
          </div>

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

      {/* 3. Indicador de Interacción Central (Prompt contextual Ateneo+) */}
      {hoveredBed && (
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

      {/* 4. Barra de Ayuda / Controles Inferior Izquierda */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-md rounded-full border border-slate-200/80 px-4 py-2 text-[11px] text-slate-600 shadow-xs flex items-center space-x-3 select-none z-10">
        <div>
          <span className="font-semibold text-slate-900">WASD:</span> Moverse
        </div>
        <span className="text-slate-300">•</span>
        <div>
          <span className="font-semibold text-slate-900">Arrastrar Ratón:</span> Mirar
        </div>
        <span className="text-slate-300">•</span>
        <div>
          <span className="font-semibold text-slate-900">Shift:</span> Correr
        </div>
        <span className="text-slate-300">•</span>
        <div>
          <span className="font-semibold text-slate-900">E:</span> Examinar Cama
        </div>
      </div>

      {/* 5. Tableta Clínica Diegética Superpuesta */}
      <ClinicalBedsideTablet />
    </div>
  );
};

export default Hospital3DPage;
