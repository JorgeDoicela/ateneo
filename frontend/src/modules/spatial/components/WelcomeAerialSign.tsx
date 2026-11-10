import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

export const WelcomeAerialSign: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    // Micro-levitación armónica sutil en el cielo sobre el coronamiento del hospital
    const t = clock.getElapsedTime();
    groupRef.current.position.y = 14.5 + Math.sin(t * 1.0) * 0.06;
  });

  return (
    <group ref={groupRef} position={[-12.2, 14.5, 0.0]}>
      {/* 1. Ménsulas arquitectónicas discretas fijadas al coronamiento del edificio */}
      <mesh position={[0, -1.2, -3.2]}>
        <cylinderGeometry args={[0.035, 0.035, 2.4, 12]} />
        <meshStandardMaterial color="#cbd5e1" metalness={0.7} roughness={0.3} />
      </mesh>
      <mesh position={[0, -1.2, 3.2]}>
        <cylinderGeometry args={[0.035, 0.035, 2.4, 12]} />
        <meshStandardMaterial color="#cbd5e1" metalness={0.7} roughness={0.3} />
      </mesh>

      {/* 2. Placa de respaldo arquitectónica blanca pura (evita transparencias invertidas) */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[0.10, 2.4, 9.2]} />
        <meshStandardMaterial color="#ffffff" roughness={0.2} metalness={0.02} />
      </mesh>

      {/* Friso perimetral sutil en Cyan Clínico de Ateneo+ */}
      <mesh position={[0, 1.21, 0]}>
        <boxGeometry args={[0.12, 0.03, 9.22]} />
        <meshStandardMaterial color="#06b6d4" emissive="#06b6d4" emissiveIntensity={1.5} />
      </mesh>
      <mesh position={[0, -1.21, 0]}>
        <boxGeometry args={[0.12, 0.03, 9.22]} />
        <meshStandardMaterial color="#2563eb" emissive="#2563eb" emissiveIntensity={1.2} />
      </mesh>

      {/* 3. Letrero Institucional Ateneo+ con Estilos Oficiales (Fondo blanco, rounded-[28px], gradiente de marca) */}
      <Html
        transform
        center
        distanceFactor={18}
        position={[-0.07, 0, 0]}
        rotation={[0, -Math.PI / 2, 0]}
        zIndexRange={[15, 0]}
        style={{
          backfaceVisibility: 'hidden',
          WebkitBackfaceVisibility: 'hidden',
          pointerEvents: 'none',
          userSelect: 'none'
        }}
      >
        <div className="w-[680px] bg-white/95 backdrop-blur-xl rounded-[28px] border border-slate-200/80 shadow-2xl p-7 text-center select-none">
          {/* Cabecera con Imagotipo Institucional Plano */}
          <div className="flex items-center justify-center space-x-2.5 mb-2.5">
            <img
              src="/ateneo.png"
              alt="Ateneo+"
              className="w-8 h-8 object-contain"
            />
            <span className="text-xs font-bold tracking-wider text-[#0b57d0] uppercase">
              Hospital Universitario • Ateneo+
            </span>
          </div>

          {/* Título Principal con Gradiente de Marca Ateneo+ */}
          <h1 className="text-3xl font-black tracking-tight bg-gradient-to-r from-[#06b6d4] via-[#2563eb] to-[#7c3aed] bg-clip-text text-transparent">
            ¡Bienvenidos al Simulador Clínico!
          </h1>

          {/* Subtítulo Clínico Fáctico */}
          <p className="text-xs font-semibold text-slate-600 mt-1.5 leading-relaxed">
            Plataforma Médica Multimodal &amp; Evaluación Formativa con IA • GPC Ecuador
          </p>

          {/* Guía de Acción Clínica en Píldora Institucional Limpia */}
          <div className="mt-4 inline-flex items-center space-x-2 px-4 py-1.5 bg-[#f0f4f9] rounded-full border border-slate-200/90 shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-[#0b57d0]" />
            <span className="text-xs font-semibold text-slate-800">
              Ingresa por el pasillo central y acércate a las camas para examinar a los pacientes
            </span>
          </div>
        </div>
      </Html>
    </group>
  );
};

export default WelcomeAerialSign;
