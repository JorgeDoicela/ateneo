import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';

interface DoctorCharacterProps {
  positionRef: React.RefObject<THREE.Vector3>;
  yawRef: React.RefObject<number>;
  currentSpeedRef: React.RefObject<number>;
  isSprintingRef: React.RefObject<boolean>;
  visible?: boolean;
}

export const DoctorCharacter: React.FC<DoctorCharacterProps> = ({
  positionRef,
  yawRef,
  currentSpeedRef,
  isSprintingRef,
  visible = true
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const gltf = useGLTF('/models/doctor_character.glb');
  const clone = useMemo(() => gltf.scene.clone(true), [gltf.scene]);

  const walkTimerRef = useRef<number>(0);
  const idleTimerRef = useRef<number>(0);

  // Referencias directas a los pivotes cinemáticos en la jerarquía del modelo
  const pivotsRef = useRef<{
    armL?: THREE.Object3D;
    armR?: THREE.Object3D;
    legL?: THREE.Object3D;
    legR?: THREE.Object3D;
    hips?: THREE.Object3D;
    head?: THREE.Object3D;
  }>({});

  useEffect(() => {
    pivotsRef.current = {
      armL: clone.getObjectByName('Doctor_Arm_L_Pivot'),
      armR: clone.getObjectByName('Doctor_Arm_R_Pivot'),
      legL: clone.getObjectByName('Doctor_Leg_L_Pivot'),
      legR: clone.getObjectByName('Doctor_Leg_R_Pivot'),
      hips: clone.getObjectByName('Doctor_Hips_Pivot'),
      head: clone.getObjectByName('Doctor_Head_Pivot')
    };

    clone.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
  }, [clone]);

  useFrame((_, delta) => {
    if (!groupRef.current || !visible) return;

    const pos = positionRef.current;
    const yaw = yawRef.current ?? 0;
    const speed = currentSpeedRef.current ?? 0;
    const isSprinting = isSprintingRef.current ?? false;

    if (pos) {
      // Posición del médico en el suelo (Z = 0)
      groupRef.current.position.set(pos.x, 0, pos.z);
      // El avatar mira exactamente hacia la dirección horizontal de movimiento/cámara
      groupRef.current.rotation.y = yaw;
    }

    const { armL, armR, legL, legR, hips } = pivotsRef.current;
    const isMoving = speed > 0.08;
    const maxSpeed = isSprinting ? 5.8 : 3.2;
    const speedFactor = Math.min(1.0, speed / maxSpeed);

    if (isMoving) {
      // Cadencia de zancada biomecánica sincronizada con la velocidad real
      const cadence = isSprinting ? 13.8 : 8.8;
      walkTimerRef.current += delta * cadence;

      const legAmplitude = isSprinting ? 0.70 : 0.46;
      const armAmplitude = isSprinting ? 0.60 : 0.38;

      const legAngle = Math.sin(walkTimerRef.current) * legAmplitude * speedFactor;
      const armAngle = Math.sin(walkTimerRef.current) * armAmplitude * speedFactor;

      // Zancada armónica cruzada (pierna izquierda adelante con brazo derecho adelante)
      if (legL) legL.rotation.x = -legAngle;
      if (legR) legR.rotation.x = legAngle;
      if (armL) armL.rotation.x = armAngle;
      if (armR) armR.rotation.x = -armAngle;

      if (hips) {
        // Ligero rebote de cadera vertical por zancada
        hips.position.y = 0.90 + Math.abs(Math.sin(walkTimerRef.current)) * 0.022 * speedFactor;
      }
    } else {
      // Reposo: retorno suave a posición neutral (lerp) y respiración sutil
      idleTimerRef.current += delta * 1.5;
      const resetFactor = Math.min(1.0, 10.0 * delta);

      if (legL) legL.rotation.x = THREE.MathUtils.lerp(legL.rotation.x, 0, resetFactor);
      if (legR) legR.rotation.x = THREE.MathUtils.lerp(legR.rotation.x, 0, resetFactor);
      if (armL) armL.rotation.x = THREE.MathUtils.lerp(armL.rotation.x, 0, resetFactor);
      if (armR) armR.rotation.x = THREE.MathUtils.lerp(armR.rotation.x, 0, resetFactor);

      if (hips) {
        const breathY = 0.90 + Math.sin(idleTimerRef.current) * 0.0035;
        hips.position.y = THREE.MathUtils.lerp(hips.position.y, breathY, resetFactor);
      }
    }
  });

  return (
    <group ref={groupRef} visible={visible}>
      <primitive object={clone} />
    </group>
  );
};

useGLTF.preload('/models/doctor_character.glb');

export default DoctorCharacter;
