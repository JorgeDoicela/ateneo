import logging
from fastapi import APIRouter, HTTPException, Form, Depends, WebSocket, WebSocketDisconnect
from typing import Optional, Dict, Any
from modules.collaboration.dependencies import get_collaboration_service
from modules.collaboration.service import CollaborationService
from modules.collaboration.connection_manager import connection_manager
from modules.cases.dependencies import get_case_service
from modules.evaluation.dependencies import get_evaluation_service
from modules.evaluation.service import EvaluationService
from auth.security import get_optional_current_user, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ateneo", tags=["Ateneo de Sala Colaborativo"])

@router.post("/create")
async def create_ateneo_room(
    case_id: str = Form(...),
    docente_id: str = Form("usr_docente_001"),
    docente_nombre: str = Form("Dr. Carlos Andrade (Docente)"),
    modo_resolucion: str = Form("individual"),
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Docente crea una sala de Ateneo sincrónica para un caso clínico.
    Soporta 'modo_resolucion': 'individual' o 'grupal'.
    """
    try:
        real_docente_id = current_user.id if current_user else docente_id
        real_docente_nombre = current_user.nombre if current_user else docente_nombre
        target_tenant_id = getattr(current_user, "tenant_id", "tenant_default") if current_user else "tenant_default"
        room = collab_service.create_room(
            case_id=case_id,
            docente_id=real_docente_id,
            docente_nombre=real_docente_nombre,
            tenant_id=target_tenant_id,
            modo_resolucion=modo_resolucion
        )
        return room
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/join")
async def join_ateneo_room(
    room_code: str = Form(...),
    user_id: str = Form("usr_alumno_001"),
    user_email: str = Form("alumno@ateneo.edu.ec"),
    user_nombre: str = Form("Estudiante María José Silva"),
    user_rol: str = Form("alumno"),
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Unirse a una sala de Ateneo activa usando el room_code de 6 caracteres.
    """
    try:
        real_user_id = current_user.id if current_user else user_id
        real_user_email = current_user.email if current_user else user_email
        real_user_nombre = current_user.nombre if current_user else user_nombre
        real_user_rol = current_user.rol.value if current_user else user_rol

        room = collab_service.join_room(room_code, real_user_id, real_user_email, real_user_nombre, real_user_rol)
        # Notificar a los clientes conectados por WebSocket
        await connection_manager.broadcast_to_room(room_code, {
            "type": "ROOM_STATE_UPDATED",
            "payload": room
        })
        return room
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/teacher/rooms")
async def get_teacher_rooms(
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Lista las salas de Ateneo creadas o moderadas por el docente autenticado.
    Si es docente o administrador, retorna sus salas con analítica enriquecida.
    """
    docente_id = current_user.id if current_user else "usr_docente_001"
    tenant_id = getattr(current_user, "tenant_id", "tenant_default") if current_user else "tenant_default"
    rooms = collab_service.get_rooms_by_docente(docente_id=docente_id, tenant_id=tenant_id)
    return rooms

@router.delete("/room/{room_code}")
async def delete_ateneo_room(
    room_code: str,
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Elimina una sala de Ateneo. Requiere rol docente o administrador.
    """
    if current_user and current_user.rol not in ["docente", "administrador"]:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: solo el docente moderador o un administrador puede eliminar la sala."
        )
    docente_id = current_user.id if current_user else "usr_docente_001"
    success = collab_service.delete_room(room_code, docente_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Sala '{room_code}' no encontrada para eliminación.")
    return {"status": "ok", "message": f"Sala '{room_code}' eliminada exitosamente."}

@router.get("/room/{room_code}")
async def get_room_state(
    room_code: str,
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Retorna el estado en tiempo real de la sala de Ateneo.
    """
    room = collab_service.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail=f"Sala '{room_code}' no encontrada.")
    return room

@router.post("/room/{room_code}/status")
async def update_room_status(
    room_code: str,
    nuevo_estado: str = Form(...),
    docente_id: str = Form("usr_docente_001"),
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Docente cambia la fase de la sala ('espera' -> 'resolucion' -> 'discusion' -> 'finalizado').
    Requiere que el usuario autenticado sea docente o el creador de la sala.
    """
    if current_user and current_user.rol not in ["docente", "administrador"]:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: solo el docente moderador o un administrador puede cambiar el estado de la sala."
        )

    try:
        real_docente_id = current_user.id if current_user else docente_id
        room = collab_service.change_room_status(room_code, nuevo_estado, real_docente_id)
        # Difundir transición de fase a los clientes WebSocket en tiempo real
        await connection_manager.broadcast_to_room(room_code, {
            "type": "PHASE_TRANSITION",
            "payload": {
                "nuevo_estado": room["estado"],
                "room": room
            }
        })
        await connection_manager.broadcast_to_room(room_code, {
            "type": "ROOM_STATE_UPDATED",
            "payload": room
        })
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/room/{room_code}/submit")
async def submit_ateneo_answer(
    room_code: str,
    user_email: str = Form(...),
    respuesta_estudiante: str = Form(...),
    collab_service: CollaborationService = Depends(get_collaboration_service),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Estudiante envía su razonamiento dentro de la sala de Ateneo.
    Se ejecuta la evaluación RAG y se almacena en la sala para la fase de discusión.
    """
    room = collab_service.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail=f"La sala '{room_code}' no existe.")

    # Evaluación RAG y LLM delegada íntegramente en EvaluationService
    try:
        resultado_eval = evaluation_service.evaluate_reasoning(
            case_id=room["case_id"],
            student_answer=respuesta_estudiante
        )
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación de la sala: {str(e)}")

    # Actualizar estado de respuesta del estudiante en la sala
    eval_dict = resultado_eval.model_dump() if hasattr(resultado_eval, "model_dump") else resultado_eval.dict()
    updated_room = collab_service.submit_student_answer(
        room_code=room_code,
        user_email=user_email,
        respuesta_estudiante=respuesta_estudiante,
        eval_result=eval_dict
    )

    # Difundir recepción de entrega en tiempo real
    await connection_manager.broadcast_to_room(room_code, {
        "type": "ANSWER_SUBMITTED",
        "payload": {
            "user_email": user_email,
            "room": updated_room
        }
    })
    await connection_manager.broadcast_to_room(room_code, {
        "type": "ROOM_STATE_UPDATED",
        "payload": updated_room
    })

    return {
        "status": "ok",
        "evaluacion": resultado_eval,
        "room": updated_room
    }

@router.post("/room/{room_code}/mode")
async def update_room_mode(
    room_code: str,
    modo_resolucion: str = Form(...),
    docente_id: str = Form("usr_docente_001"),
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Docente o moderador conmuta el modo de resolución de la sala ('individual' <-> 'grupal').
    Difunde el cambio instantáneamente vía WebSockets a todos los estudiantes conectados.
    """
    if current_user and current_user.rol not in ["docente", "administrador"]:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado: solo el docente moderador o administrador puede cambiar el modo de resolución."
        )

    try:
        real_docente_id = current_user.id if current_user else docente_id
        room = collab_service.change_resolution_mode(room_code, modo_resolucion, real_docente_id)
        await connection_manager.broadcast_to_room(room_code, {
            "type": "MODE_CHANGED",
            "payload": {
                "modo_resolucion": room["modo_resolucion"],
                "room": room
            }
        })
        await connection_manager.broadcast_to_room(room_code, {
            "type": "ROOM_STATE_UPDATED",
            "payload": room
        })
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/room/{room_code}/submit-group")
async def submit_ateneo_group_answer(
    room_code: str,
    respuesta_grupal: str = Form(...),
    user_nombre: str = Form("Equipo Clínico"),
    current_user: Optional[UserResponse] = Depends(get_optional_current_user),
    collab_service: CollaborationService = Depends(get_collaboration_service),
    evaluation_service: EvaluationService = Depends(get_evaluation_service)
):
    """
    Envía el dictamen de consenso colectivo en Modo Grupal (Ateneo Colaborativo).
    Ejecuta el motor de evaluación RAG contra la GPC y almacena el dictamen de sala.
    """
    room = collab_service.get_room(room_code)
    if not room:
        raise HTTPException(status_code=404, detail=f"La sala '{room_code}' no existe.")

    try:
        resultado_eval = evaluation_service.evaluate_reasoning(
            case_id=room["case_id"],
            student_answer=respuesta_grupal
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación de dictamen grupal: {str(e)}")

    eval_dict = resultado_eval.model_dump() if hasattr(resultado_eval, "model_dump") else resultado_eval.dict()
    submitter_nombre = current_user.nombre if current_user else user_nombre
    updated_room = collab_service.submit_group_answer(
        room_code=room_code,
        texto_grupal=respuesta_grupal,
        eval_result=eval_dict,
        submitted_by_nombre=submitter_nombre
    )

    await connection_manager.broadcast_to_room(room_code, {
        "type": "GROUP_ANSWER_SUBMITTED",
        "payload": {
            "room": updated_room,
            "evaluacion": eval_dict,
            "submitted_by": submitter_nombre
        }
    })
    await connection_manager.broadcast_to_room(room_code, {
        "type": "ROOM_STATE_UPDATED",
        "payload": updated_room
    })

    return {
        "status": "ok",
        "evaluacion": eval_dict,
        "room": updated_room
    }


@router.websocket("/ws/{room_code}")
async def websocket_ateneo_room(
    websocket: WebSocket,
    room_code: str,
    collab_service: CollaborationService = Depends(get_collaboration_service)
):
    """
    Canal WebSocket bidireccional y de baja latencia para salas colaborativas de Ateneo+.
    Sincroniza en tiempo real: presencia activa, transiciones pedagógicas de fase,
    votos de hipótesis diagnóstica y dictámenes grupales sin polling HTTP.
    """
    room = collab_service.get_room(room_code)
    if not room:
        await websocket.close(code=4004, reason=f"Sala '{room_code}' no encontrada")
        return

    await connection_manager.connect(room_code, websocket)
    try:
        # Enviar estado actual consolidado al cliente al momento del apretón de manos
        await websocket.send_json({
            "type": "ROOM_STATE_UPDATED",
            "payload": room
        })

        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type == "PING":
                await websocket.send_json({
                    "type": "PONG",
                    "payload": {"server_time": payload.get("timestamp")}
                })

            elif msg_type == "IDENTIFY":
                user_id = payload.get("user_id") or "usr_alumno_001"
                user_email = payload.get("email") or f"{user_id}@ateneo.edu.ec"
                user_nombre = payload.get("nombre") or "Estudiante Clínico"
                user_rol = payload.get("rol", "alumno")

                meta = {
                    "user_id": user_id,
                    "nombre": user_nombre,
                    "email": user_email,
                    "rol": user_rol
                }
                connection_manager.client_meta[websocket] = meta

                # Si es un alumno o participante de sala, registrarlo formalmente y actualizar métricas
                current_room_data = collab_service.get_room(room_code)
                updated_room = current_room_data
                if current_room_data and (user_rol != "docente" or user_id != current_room_data.get("docente_id")):
                    try:
                        updated_room = collab_service.join_room(
                            room_code=room_code,
                            user_id=user_id,
                            user_email=user_email,
                            user_nombre=user_nombre,
                            user_rol=user_rol
                        )
                    except Exception as err:
                        logger.error(f"[WS] Error registrando participante en IDENTIFY: {err}")

                await connection_manager.broadcast_to_room(room_code, {
                    "type": "PARTICIPANT_JOINED",
                    "payload": {
                        "user": meta,
                        "total_conectados": connection_manager.get_connected_count(room_code),
                        "room": updated_room
                    }
                })
                if updated_room:
                    await connection_manager.broadcast_to_room(room_code, {
                        "type": "ROOM_STATE_UPDATED",
                        "payload": updated_room
                    })

            elif msg_type == "VOTE_CAST":
                # Estudiante emite o actualiza su voto de hipótesis clínica
                await connection_manager.broadcast_to_room(room_code, {
                    "type": "VOTE_CAST",
                    "payload": payload
                })

            elif msg_type == "PHASE_TRANSITION_REQUEST":
                nuevo_estado = payload.get("nuevo_estado")
                docente_id = payload.get("user_id") or "usr_docente_001"
                if nuevo_estado:
                    try:
                        room_updated = collab_service.change_room_status(room_code, nuevo_estado, docente_id)
                        await connection_manager.broadcast_to_room(room_code, {
                            "type": "PHASE_TRANSITION",
                            "payload": {
                                "nuevo_estado": room_updated["estado"],
                                "room": room_updated
                            }
                        })
                        await connection_manager.broadcast_to_room(room_code, {
                            "type": "ROOM_STATE_UPDATED",
                            "payload": room_updated
                        })
                    except Exception as err:
                        logger.error(f"[WS] Error en transición de fase: {err}")

            elif msg_type == "COLLAB_TEXT_UPDATE":
                # Sincronización en tiempo real de texto de redacción colaborativa en vivo
                texto = payload.get("texto", "")
                user_id = payload.get("user_id", "")
                user_nombre = payload.get("user_nombre", "Estudiante")
                client_id = payload.get("client_id", "")
                try:
                    collab_service.update_collaborative_text(room_code, texto, user_id, user_nombre)
                    await connection_manager.broadcast_to_room(room_code, {
                        "type": "COLLAB_TEXT_SYNC",
                        "payload": {
                            "texto": texto,
                            "user_id": user_id,
                            "user_nombre": user_nombre,
                            "client_id": client_id
                        }
                    })
                except Exception as err:
                    logger.error(f"[WS] Error sincronizando borrador colaborativo: {err}")

            elif msg_type == "COLLAB_TYPING":
                # Indicador de presencia de escritura en el lienzo grupal
                await connection_manager.broadcast_to_room(room_code, {
                    "type": "COLLAB_TYPING_INDICATOR",
                    "payload": {
                        "user_id": payload.get("user_id"),
                        "user_nombre": payload.get("user_nombre"),
                        "client_id": payload.get("client_id", ""),
                        "is_typing": payload.get("is_typing", False)
                    }
                })

            elif msg_type == "SYNC_REQUEST":
                fresh_state = collab_service.get_room(room_code)
                await websocket.send_json({
                    "type": "ROOM_STATE_UPDATED",
                    "payload": fresh_state
                })

    except WebSocketDisconnect:
        meta = await connection_manager.disconnect(room_code, websocket)
        if meta:
            await connection_manager.broadcast_to_room(room_code, {
                "type": "PARTICIPANT_LEFT",
                "payload": {
                    "user": meta,
                    "total_conectados": connection_manager.get_connected_count(room_code)
                }
            })
    except Exception as e:
        logger.error(f"[WS] Error inesperado en socket de sala '{room_code}': {e}")
        await connection_manager.disconnect(room_code, websocket)

