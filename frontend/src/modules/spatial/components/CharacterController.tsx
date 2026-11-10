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

  // Posición y rotación cinemática inicial: Exterior del Hospital frente al portal abierto mirando al Este (+X)
  const positionRef = useRef<THREE.Vector3>(new THREE.Vector3(-33.5, 1.62, 0));
  const yawRef = useRef<number>(-Math.PI / 2);
  const pitchRef = useRef<number>(0.07);

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

    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1 && !isTabletOpen) {
        const touch = e.touches[0];
        // Si el toque no está en la esquina inferior izquierda (zona reservada al joystick)
        const isJoystickArea = touch.clientX < 180 && touch.clientY > window.innerHeight - 180;
        if (!isJoystickArea) {
          isMouseDownRef.current = true;
          previousMousePositionRef.current = { x: touch.clientX, y: touch.clientY };
        }
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!isMouseDownRef.current || isTabletOpen || e.touches.length === 0) return;
      const touch = e.touches[0];
      const deltaX = touch.clientX - previousMousePositionRef.current.x;
      const deltaY = touch.clientY - previousMousePositionRef.current.y;

      const sensitivity = 0.0035;
      yawRef.current -= deltaX * sensitivity;
      pitchRef.current = Math.max(
        -Math.PI / 3,
        Math.min(Math.PI / 3, pitchRef.current - deltaY * sensitivity)
      );

      previousMousePositionRef.current = { x: touch.clientX, y: touch.clientY };
    };

    const handleTouchEnd = () => {
      isMouseDownRef.current = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    gl.domElement.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('mousemove', handleMouseMove);
    gl.domElement.addEventListener('touchstart', handleTouchStart, { passive: true });
    window.addEventListener('touchmove', handleTouchMove, { passive: true });
    window.addEventListener('touchend', handleTouchEnd);
    window.addEventListener('touchcancel', handleTouchEnd);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      gl.domElement.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('mousemove', handleMouseMove);
      gl.domElement.removeEventListener('touchstart', handleTouchStart);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
      window.removeEventListener('touchcancel', handleTouchEnd);
    };
  }, [hoveredBedId, isTabletOpen, openBedInspection, gl]);

  useFrame((_, delta) => {
    if (isTabletOpen) return;

    // Consumir deltas táctiles acumulados desde la zona de rotación táctil
    const touchLook = useSpatialStore.getState().consumeTouchLookDelta();
    if (touchLook.dx !== 0 || touchLook.dy !== 0) {
      const touchSensitivity = 0.0035;
      yawRef.current -= touchLook.dx * touchSensitivity;
      pitchRef.current = Math.max(
        -Math.PI / 3,
        Math.min(Math.PI / 3, pitchRef.current - touchLook.dy * touchSensitivity)
      );
    }

    const touchInput = useSpatialStore.getState().touchInput;
    const isSprinting =
      keysRef.current['ShiftLeft'] ||
      keysRef.current['ShiftRight'] ||
      touchInput.isSprinting;
    const moveSpeed = (isSprinting ? 6.0 : 3.5) * delta;

    // Vector de traslación en el plano XZ
    const forward = new THREE.Vector3(-Math.sin(yawRef.current), 0, -Math.cos(yawRef.current));
    const right = new THREE.Vector3(Math.cos(yawRef.current), 0, -Math.sin(yawRef.current));

    const moveDir = new THREE.Vector3(0, 0, 0);

    if (keysRef.current['KeyW'] || keysRef.current['ArrowUp']) moveDir.add(forward);
    if (keysRef.current['KeyS'] || keysRef.current['ArrowDown']) moveDir.sub(forward);
    if (keysRef.current['KeyA'] || keysRef.current['ArrowLeft']) moveDir.sub(right);
    if (keysRef.current['KeyD'] || keysRef.current['ArrowRight']) moveDir.add(right);

    // Entrada análoga desde el joystick virtual táctil
    if (Math.abs(touchInput.moveX) > 0.04 || Math.abs(touchInput.moveY) > 0.04) {
      moveDir.addScaledVector(forward, touchInput.moveY);
      moveDir.addScaledVector(right, touchInput.moveX);
    }

    if (moveDir.lengthSq() > 0) {
      const prevX = positionRef.current.x;
      const prevZ = positionRef.current.z;

      moveDir.normalize().multiplyScalar(moveSpeed);
      positionRef.current.add(moveDir);

      // 1. Confinamiento global del campus hospitalario (Explanada Exterior + Pabellón Interior)
      positionRef.current.x = Math.max(-35.0, Math.min(10.5, positionRef.current.x));

      // 2. Colisión física con el Muro de Fachada Oeste (X = -12.0) y Portal de Puertas Abiertas (Z en [-1.55, 1.55])
      const inDoorwayZ = Math.abs(positionRef.current.z) <= 1.55;
      if (!inDoorwayZ) {
        if (prevX <= -12.45 && positionRef.current.x > -12.45) {
          positionRef.current.x = -12.45;
        } else if (prevX >= -11.55 && positionRef.current.x < -11.55) {
          positionRef.current.x = -11.55;
        }
      }

      // 3. Límites laterales Z según zona (Umbral de puerta vs. Interior del Pabellón vs. Explanada Exterior)
      if (positionRef.current.x > -12.45 && positionRef.current.x < -11.55) {
        positionRef.current.z = Math.max(-1.55, Math.min(1.55, positionRef.current.z));
      } else if (positionRef.current.x >= -11.55) {
        positionRef.current.z = Math.max(-7.8, Math.min(7.8, positionRef.current.z));
      } else {
        positionRef.current.z = Math.max(-16.0, Math.min(16.0, positionRef.current.z));

        // Colisión con la Ambulancia SVA estacionada en la bahía exterior (X en [-23.4, -20.2], Z en [4.6, 10.8])
        if (
          positionRef.current.x > -23.4 &&
          positionRef.current.x < -20.2 &&
          positionRef.current.z > 4.6 &&
          positionRef.current.z < 10.8
        ) {
          positionRef.current.x = prevX;
          positionRef.current.z = prevZ;
        }
      }
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
