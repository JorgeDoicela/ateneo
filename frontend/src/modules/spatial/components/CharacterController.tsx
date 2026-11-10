import React, { useRef, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useSpatialStore } from '../store/useSpatialStore';
import DoctorCharacter from './DoctorCharacter';

export const CharacterController: React.FC = () => {
  const { camera, gl } = useThree();

  const setPlayerTransform = useSpatialStore((s) => s.setPlayerTransform);
  const cameraMode = useSpatialStore((s) => s.cameraMode);
  const beds = useSpatialStore((s) => s.beds);
  const hoveredBedId = useSpatialStore((s) => s.hoveredBedId);
  const setHoveredBed = useSpatialStore((s) => s.setHoveredBed);
  const openBedInspection = useSpatialStore((s) => s.openBedInspection);
  const isTabletOpen = useSpatialStore((s) => s.isTabletOpen);

  // Posición y rotación cinemática inicial: Exterior del Hospital frente al portal abierto mirando al Este (+X)
  const positionRef = useRef<THREE.Vector3>(new THREE.Vector3(-33.5, 1.62, 0));
  const yawRef = useRef<number>(-Math.PI / 2);
  const pitchRef = useRef<number>(0.07);

  // Dinámica física realista: velocidad con inercia, cadencia y bamboleo biomecánico (head bobbing)
  const velocityRef = useRef<THREE.Vector3>(new THREE.Vector3(0, 0, 0));
  const currentSpeedRef = useRef<number>(0);
  const isSprintingRef = useRef<boolean>(false);
  const bobTimerRef = useRef<number>(0);
  const idleTimerRef = useRef<number>(0);
  const currentBobYRef = useRef<number>(0);
  const currentBobSwayRef = useRef<number>(0);
  const currentBobRollRef = useRef<number>(0);

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
        -Math.PI / 2.3,
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
        -Math.PI / 2.3,
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
        -Math.PI / 2.3,
        Math.min(Math.PI / 3, pitchRef.current - touchLook.dy * touchSensitivity)
      );
    }

    const touchInput = useSpatialStore.getState().touchInput;
    const isSprinting =
      keysRef.current['ShiftLeft'] ||
      keysRef.current['ShiftRight'] ||
      touchInput.isSprinting;

    // Vectores direccionales relativos al ángulo de mirada horizontal
    const forward = new THREE.Vector3(-Math.sin(yawRef.current), 0, -Math.cos(yawRef.current));
    const right = new THREE.Vector3(Math.cos(yawRef.current), 0, -Math.sin(yawRef.current));

    const inputDir = new THREE.Vector3(0, 0, 0);

    if (keysRef.current['KeyW'] || keysRef.current['ArrowUp']) inputDir.add(forward);
    if (keysRef.current['KeyS'] || keysRef.current['ArrowDown']) inputDir.sub(forward);
    if (keysRef.current['KeyA'] || keysRef.current['ArrowLeft']) inputDir.sub(right);
    if (keysRef.current['KeyD'] || keysRef.current['ArrowRight']) inputDir.add(right);

    // Entrada análoga desde el joystick virtual táctil
    if (Math.abs(touchInput.moveX) > 0.04 || Math.abs(touchInput.moveY) > 0.04) {
      inputDir.addScaledVector(forward, touchInput.moveY);
      inputDir.addScaledVector(right, touchInput.moveX);
    }

    const hasInput = inputDir.lengthSq() > 0.001;
    if (hasInput && inputDir.lengthSq() > 1.0) {
      inputDir.normalize();
    }

    // 1. Inercia biomecánica y aceleración suave
    const targetSpeed = hasInput ? (isSprinting ? 5.8 : 3.2) : 0.0;
    const targetVelocity = inputDir.clone().multiplyScalar(targetSpeed);

    // Tasa de aceleración (arranque rápido y frenado suave orgánico)
    const accelRate = hasInput ? 13.0 : 9.5;
    velocityRef.current.lerp(targetVelocity, Math.min(1.0, accelRate * delta));

    const currentSpeed = velocityRef.current.length();
    currentSpeedRef.current = currentSpeed;
    isSprintingRef.current = isSprinting;

    // 2. Desplazamiento y resolución de colisiones físicas
    if (currentSpeed > 0.005) {
      const prevX = positionRef.current.x;
      const prevZ = positionRef.current.z;

      positionRef.current.x += velocityRef.current.x * delta;
      positionRef.current.z += velocityRef.current.z * delta;

      // 2A. Confinamiento perimetral del campus hospitalario
      if (positionRef.current.x < -35.0) {
        positionRef.current.x = -35.0;
        velocityRef.current.x = 0;
      } else if (positionRef.current.x > 10.5) {
        positionRef.current.x = 10.5;
        velocityRef.current.x = 0;
      }

      // 2B. Colisión física con el Muro de Fachada Oeste (X = -12.0) y Portal de Puertas Abiertas (Z en [-1.55, 1.55])
      const inDoorwayZ = Math.abs(positionRef.current.z) <= 1.55;
      if (!inDoorwayZ) {
        if (prevX <= -12.45 && positionRef.current.x > -12.45) {
          positionRef.current.x = -12.45;
          velocityRef.current.x = 0;
        } else if (prevX >= -11.55 && positionRef.current.x < -11.55) {
          positionRef.current.x = -11.55;
          velocityRef.current.x = 0;
        }
      }

      // 2C. Límites laterales Z según zona
      if (positionRef.current.x > -12.45 && positionRef.current.x < -11.55) {
        positionRef.current.z = Math.max(-1.55, Math.min(1.55, positionRef.current.z));
      } else if (positionRef.current.x >= -11.55) {
        if (positionRef.current.z < -7.8 || positionRef.current.z > 7.8) {
          positionRef.current.z = Math.max(-7.8, Math.min(7.8, positionRef.current.z));
          velocityRef.current.z = 0;
        }
      } else {
        if (positionRef.current.z < -16.0 || positionRef.current.z > 16.0) {
          positionRef.current.z = Math.max(-16.0, Math.min(16.0, positionRef.current.z));
          velocityRef.current.z = 0;
        }

        // Colisión con la Ambulancia SVA estacionada en la bahía exterior (X en [-23.4, -20.2], Z en [4.6, 10.8])
        if (
          positionRef.current.x > -23.4 &&
          positionRef.current.x < -20.2 &&
          positionRef.current.z > 4.6 &&
          positionRef.current.z < 10.8
        ) {
          positionRef.current.x = prevX;
          positionRef.current.z = prevZ;
          velocityRef.current.set(0, 0, 0);
        }
      }
    }

    // 3. Bamboleo natural del paso (Head Bobbing) y respiración
    const isRunning = isSprinting && currentSpeed > 3.4;
    const speedRatio = Math.min(1.0, currentSpeed / 5.8);

    let targetBobY = 0;
    let targetBobSway = 0;
    let targetBobRoll = 0;

    if (currentSpeed > 0.12) {
      // Cadencia: ~1.4 pasos/s caminando (8.8 rad/s), ~2.2 pasos/s corriendo (13.8 rad/s)
      const stepCadence = isRunning ? 13.8 : 8.8;
      bobTimerRef.current += stepCadence * delta;

      const ampY = isRunning ? 0.038 : 0.020;
      const ampSway = isRunning ? 0.016 : 0.009;
      const ampRoll = isRunning ? 0.012 : 0.006;

      // Oscilación vertical en cada pisada
      targetBobY = Math.sin(bobTimerRef.current) * ampY * speedRatio;
      // Balanceo lateral biomecánico (un ciclo por cada dos pasos)
      targetBobSway = Math.cos(bobTimerRef.current * 0.5) * ampSway * speedRatio;
      targetBobRoll = Math.cos(bobTimerRef.current * 0.5) * ampRoll * speedRatio;
    } else {
      // Respiración sutil en reposo
      idleTimerRef.current += delta * 1.5;
      targetBobY = Math.sin(idleTimerRef.current) * 0.0025;
    }

    // Suavizado dinámico de transiciones
    currentBobYRef.current = THREE.MathUtils.lerp(currentBobYRef.current, targetBobY, Math.min(1.0, 14.0 * delta));
    currentBobSwayRef.current = THREE.MathUtils.lerp(currentBobSwayRef.current, targetBobSway, Math.min(1.0, 12.0 * delta));
    currentBobRollRef.current = THREE.MathUtils.lerp(currentBobRollRef.current, targetBobRoll, Math.min(1.0, 12.0 * delta));

    // 4. Posicionamiento dinámico de la cámara según el modo activo (3ª Persona / 1ª Persona)
    if (cameraMode === 'third-person') {
      // Punto de enfoque en la espalda superior / nuca del médico (Z = 1.44m)
      const lookTarget = new THREE.Vector3(
        positionRef.current.x,
        1.44,
        positionRef.current.z
      );
      const camDistance = 2.45;
      const cosP = Math.cos(pitchRef.current);
      const sinP = Math.sin(pitchRef.current);

      // Posición orbital detrás del médico en dirección opuesta al vector de mirada
      const camPos = new THREE.Vector3(
        lookTarget.x + Math.sin(yawRef.current) * cosP * camDistance,
        Math.max(0.35, lookTarget.y - sinP * camDistance + 0.22),
        lookTarget.z + Math.cos(yawRef.current) * cosP * camDistance
      );

      camera.position.copy(camPos);
      camera.lookAt(lookTarget);
    } else {
      // Modo Primera Persona inmersiva con cinemática biomecánica y cuerpo propio visible (True First Person)
      const eyePosition = positionRef.current.clone();
      // Ojos anatómicos ubicados 8 cm adelante del eje corporal
      eyePosition.addScaledVector(forward, 0.08);
      eyePosition.y = 1.62 + currentBobYRef.current;
      eyePosition.addScaledVector(right, currentBobSwayRef.current);

      camera.position.copy(eyePosition);
      camera.rotation.set(0, 0, 0);
      camera.rotation.order = 'YXZ';
      camera.rotation.y = yawRef.current;
      camera.rotation.x = pitchRef.current;
      camera.rotation.z = currentBobRollRef.current;
    }

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

  return (
    <DoctorCharacter
      positionRef={positionRef}
      yawRef={yawRef}
      currentSpeedRef={currentSpeedRef}
      isSprintingRef={isSprintingRef}
      cameraMode={cameraMode}
      visible={true}
    />
  );
};

export default CharacterController;
