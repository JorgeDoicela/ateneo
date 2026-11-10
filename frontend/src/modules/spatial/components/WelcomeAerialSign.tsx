import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

export const WelcomeAerialSign: React.FC = () => {
  const groupRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    // Micro-levitación armónica en el cielo despejado sobre el hospital
    const t = clock.getElapsedTime();
    groupRef.current.position.y = 17.2 + Math.sin(t * 1.0) * 0.08;
  });

  return (
    <group ref={groupRef} position={[-12.2, 17.2, 0.0]}>
      {/* Píldora Flotante Institucional Ateneo+ en el cielo sobre el hospital */}
      <Html
        transform
        center
        distanceFactor={14}
        position={[0, 0, 0]}
        rotation={[0, -Math.PI / 2, 0]}
        zIndexRange={[15, 0]}
        style={{
          backfaceVisibility: 'hidden',
          WebkitBackfaceVisibility: 'hidden',
          pointerEvents: 'none',
          userSelect: 'none'
        }}
      >
        <div className="bg-white/95 backdrop-blur-xl rounded-full border border-slate-200/80 shadow-2xl px-8 py-3.5 flex items-center space-x-3.5 select-none whitespace-nowrap">
          <img
            src="/ateneo.png"
            alt="Ateneo+"
            className="w-7 h-7 object-contain shrink-0"
          />
          <span className="text-2xl font-black tracking-tight bg-gradient-to-r from-[#06b6d4] via-[#2563eb] to-[#7c3aed] bg-clip-text text-transparent">
            ¡Bienvenidos a Ateneo+!
          </span>
        </div>
      </Html>
    </group>
  );
};

export default WelcomeAerialSign;
