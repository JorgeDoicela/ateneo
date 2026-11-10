import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

export const WelcomeAerialSign: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    // Animación de levitación suave y armónica en el aire
    const t = clock.getElapsedTime();
    groupRef.current.position.y = 5.3 + Math.sin(t * 1.2) * 0.08;
  });

  return (
    <group ref={groupRef} position={[-23.0, 5.3, 0.0]}>
      {/* 1. Estructura física 3D del letrero aéreo (Slab arquitectónico) */}
      {/* Panel principal blanco clínico */}
      <mesh position={[0, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.16, 2.0, 7.2]} />
        <meshStandardMaterial
          color="#f8fafc"
          roughness={0.25}
          metalness={0.08}
        />
      </mesh>

      {/* Marco perimetral satinado en acero institucional */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[0.17, 2.04, 7.24]} />
        <meshStandardMaterial
          color="#0b57d0"
          roughness={0.35}
          metalness={0.65}
          wireframe={false}
        />
      </mesh>

      {/* Tira LED superior iluminada en Cyan Clínico */}
      <mesh position={[0, 1.01, 0]}>
        <boxGeometry args={[0.18, 0.04, 7.22]} />
        <meshStandardMaterial
          color="#06b6d4"
          emissive="#06b6d4"
          emissiveIntensity={2.8}
        />
      </mesh>

      {/* Tira LED inferior iluminada en Azul Royal */}
      <mesh position={[0, -1.01, 0]}>
        <boxGeometry args={[0.18, 0.04, 7.22]} />
        <meshStandardMaterial
          color="#2563eb"
          emissive="#2563eb"
          emissiveIntensity={2.4}
        />
      </mesh>

      {/* Cables de suspensión arquitectónica hacia el cielo */}
      <mesh position={[0, 4.5, -3.2]}>
        <cylinderGeometry args={[0.012, 0.012, 7.0, 8]} />
        <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.2} />
      </mesh>
      <mesh position={[0, 4.5, 3.2]}>
        <cylinderGeometry args={[0.012, 0.012, 7.0, 8]} />
        <meshStandardMaterial color="#94a3b8" metalness={0.9} roughness={0.2} />
      </mesh>

      {/* 2. Cara Frontal (Mira al Oeste / -X, visible desde el punto de inicio en la calle) */}
      <Html
        transform
        center
        distanceFactor={11}
        position={[-0.09, 0, 0]}
        rotation={[0, -Math.PI / 2, 0]}
        zIndexRange={[15, 0]}
        className="pointer-events-none select-none"
      >
        <div className="w-[580px] p-6 text-center">
          {/* Badge superior de estatus clínico */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-slate-900/90 border border-cyan-400/50 shadow-md backdrop-blur-md mb-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-[11px] font-bold text-cyan-300 tracking-wider uppercase">
              Hospital Clínico de Simulación
            </span>
          </div>

          {/* Título Principal de Bienvenida */}
          <h1 className="text-3xl font-black tracking-tight text-slate-900 drop-shadow-xs">
            ¡BIENVENIDOS A ATENEO+!
          </h1>

          {/* Subtítulo institucional normado */}
          <p className="text-xs font-semibold text-slate-600 mt-1">
            Plataforma Médica Multimodal &amp; Razonamiento Clínico con IA • GPC Ecuador
          </p>

          {/* Indicación de navegación */}
          <div className="mt-3.5 inline-flex items-center space-x-2 px-4 py-1.5 bg-blue-50/90 rounded-full border border-blue-200/80 shadow-2xs">
            <span className="w-1.5 h-1.5 rounded-full bg-[#0b57d0]" />
            <span className="text-[11px] font-semibold text-[#0b57d0]">
              Avanza hacia las puertas de urgencias para examinar a los pacientes
            </span>
          </div>
        </div>
      </Html>

      {/* 3. Cara Posterior (Mira al Este / +X, visible al salir del hospital hacia la calle) */}
      <Html
        transform
        center
        distanceFactor={11}
        position={[0.09, 0, 0]}
        rotation={[0, Math.PI / 2, 0]}
        zIndexRange={[15, 0]}
        className="pointer-events-none select-none"
      >
        <div className="w-[560px] p-5 text-center">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/90 border border-blue-400/50 shadow-md backdrop-blur-md mb-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-400" />
            <span className="text-[10px] font-bold text-blue-200 tracking-wider uppercase">
              Explanada Exterior • Campus Universitario
            </span>
          </div>
          <h2 className="text-xl font-black text-slate-900">
            HOSPITAL UNIVERSITARIO ATENEO+
          </h2>
          <p className="text-[11px] font-medium text-slate-600 mt-0.5">
            Bahía de Soporte Vital Avanzado (SVA) y Acceso Peatonal
          </p>
        </div>
      </Html>
    </group>
  );
};

export default WelcomeAerialSign;
