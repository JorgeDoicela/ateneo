import React, { useRef, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useSpatialStore } from '../store/useSpatialStore';

export const CharacterController: React.FC = () => {
  const { camera, gl } = useThree();

  const setPlayerTransform = useSpatialStore((s) => s.setPlayerTransform);
  const beds = useSpatialStore((s) => s.beds);
  const hoveredBedId = useSpatialStore((s) => s.hoveredBedId);
  const setHoveredBed = useSpatialStore((s) => s.setHoveredBed);
  const openBedInspection = useSpatialStore((s) => s.openBedInspection);
  const isTabletOpen = useSpatialStore((s) => s.isTabletOpen);

  // Posición y rotación cinemática (Entrada Oeste del corredor mirando hacia el Este +X)
  const positionRef = useRef<THREE.Vector3>(new THREE.Vector3(-8.5, 1.58, 0));
  const yawRef = useRef<number>(-Math.PI / 2);
  const pitchRef = useRef<number>(-0.04);

  const keysRef = useRef<{ [key: string]: boolean }>({});
  const isMouseDownRef = useRef<boolean>(false);
  const previousMousePositionRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keysRef.current[e.code] = true;
      if ((e.code === 'KeyE' || e.code === 'Enter') && hoveredBedId && !isTabletOpen) {
        openBedInspection(hoveredBedId);
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      keysRef.current[e.code] = false;
    };

    const handleMouseDown = (e: MouseEvent) => {
      if (e.button === 0) {
        isMouseDownRef.current = true;
        previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
      }
    };

    const handleMouseUp = () => {
      isMouseDownRef.current = false;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isMouseDownRef.current || isTabletOpen) return;

      const deltaX = e.clientX - previousMousePositionRef.current.x;
      const deltaY = e.clientY - previousMousePositionRef.current.y;

      const sensitivity = 0.003;
      yawRef.current -= deltaX * sensitivity;
      pitchRef.current = Math.max(
        -Math.PI / 3,
        Math.min(Math.PI / 3, pitchRef.current - deltaY * sensitivity)
      );

      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    gl.domElement.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      gl.domElement.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [hoveredBedId, isTabletOpen, openBedInspection, gl]);

  useFrame((_, delta) => {
    if (isTabletOpen) return;

    const moveSpeed = (keysRef.current['ShiftLeft'] || keysRef.current['ShiftRight'] ? 6.0 : 3.5) * delta;

    // Vector de traslación en el plano XZ
    const forward = new THREE.Vector3(-Math.sin(yawRef.current), 0, -Math.cos(yawRef.current));
    const right = new THREE.Vector3(Math.cos(yawRef.current), 0, -Math.sin(yawRef.current));

    const moveDir = new THREE.Vector3(0, 0, 0);

    if (keysRef.current['KeyW'] || keysRef.current['ArrowUp']) moveDir.add(forward);
    if (keysRef.current['KeyS'] || keysRef.current['ArrowDown']) moveDir.sub(forward);
    if (keysRef.current['KeyA'] || keysRef.current['ArrowLeft']) moveDir.sub(right);
    if (keysRef.current['KeyD'] || keysRef.current['ArrowRight']) moveDir.add(right);

    if (moveDir.lengthSq() > 0) {
      moveDir.normalize().multiplyScalar(moveSpeed);
      positionRef.current.add(moveDir);

      // Confinamiento en los límites herméticos del pabellón
      positionRef.current.x = Math.max(-10.5, Math.min(10.5, positionRef.current.x));
      positionRef.current.z = Math.max(-7.8, Math.min(7.8, positionRef.current.z));
    }

    // Actualizar cámara
    camera.position.copy(positionRef.current);
    camera.rotation.set(0, 0, 0);
    camera.rotation.order = 'YXZ';
    camera.rotation.y = yawRef.current;
    camera.rotation.x = pitchRef.current;

    // Sincronizar posición con el store
    setPlayerTransform(
      [positionRef.current.x, positionRef.current.y, positionRef.current.z],
      yawRef.current
    );

    // Detección de proximidad a las camas (radio de 2.8 m)
    let closestBedId: string | null = null;
    let minDistance = 2.8;

    for (const bed of beds) {
      const dist = Math.hypot(
        positionRef.current.x - bed.position[0],
        positionRef.current.z - bed.position[2]
      );
      if (dist < minDistance) {
        minDistance = dist;
        closestBedId = bed.id;
      }
    }

    if (closestBedId !== hoveredBedId) {
      setHoveredBed(closestBedId);
    }
  });

  return null;
};

export default CharacterController;
