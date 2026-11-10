import React, { useMemo } from 'react';
import { useGLTF } from '@react-three/drei';

/**
 * Escenario de Alta Fidelidad del Pabellón Hospitalario
 * Carga hospital_ward.glb con materiales PBR reales (vinilo, azulejos, acero y monitores ECG).
 */
export const HospitalWardScene: React.FC = () => {
  const { scene } = useGLTF('/models/hospital_ward.glb');
  const clonedScene = useMemo(() => scene.clone(true), [scene]);

  return (
    <group name="hospital_ward_root">
      <primitive object={clonedScene} />

      {/* Luces puntuales estériles sobre cada bahía clínica y corredor central */}
      {[-7, 0, 7].map((x) =>
        [-5, 0, 5].map((z) => (
          <pointLight
            key={`light_${x}_${z}`}
            position={[x, 3.4, z]}
            intensity={10}
            distance={14}
            decay={1.8}
            color="#f8fafc"
          />
        ))
      )}

      {/* Iluminación bajo la marquesina exterior de Urgencias y umbral de puertas abiertas */}
      <pointLight position={[-15.5, 3.3, 0]} intensity={14} distance={14} decay={1.6} color="#f8fafc" />
      <pointLight position={[-12.0, 2.6, 0]} intensity={12} distance={10} decay={1.6} color="#e0f2fe" />

      {/* Iluminación sobre central de enfermería al fondo Este */}
      <pointLight position={[9.5, 3.3, 0]} intensity={12} distance={10} decay={1.8} color="#f0f9ff" />
    </group>
  );
};

useGLTF.preload('/models/hospital_ward.glb');

export default HospitalWardScene;
