import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from auth.security import init_demo_users
from tests.client_helper import get_test_client

init_demo_users()
client = get_test_client()


def get_auth_token(email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def test_teacher_room_lifecycle_and_management():
    # 1. Autenticación como docente
    teacher_token = get_auth_token("docente@ateneo.edu.ec", "Docente123!")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}

    # 2. Docente crea una sala sincrónica
    res_create = client.post("/api/ateneo/create", data={
        "case_id": "case_preeclampsia_01",
        "docente_id": "usr_docente_001",
        "docente_nombre": "Dr. Carlos Andrade"
    }, headers=teacher_headers)
    assert res_create.status_code == 200
    room = res_create.json()
    room_code = room["room_code"]
    assert room["estado"] == "espera"
    assert room["docente_id"] == "usr_docente_001"

    # 3. Alumno se une a la sala
    student_token = get_auth_token("alumno@ateneo.edu.ec", "Alumno123!")
    student_headers = {"Authorization": f"Bearer {student_token}"}
    res_join = client.post("/api/ateneo/join", data={
        "room_code": room_code,
        "user_id": "usr_alumno_001",
        "user_email": "alumno@ateneo.edu.ec",
        "user_nombre": "Estudiante María José Silva",
        "user_rol": "alumno"
    }, headers=student_headers)
    assert res_join.status_code == 200
    joined_room = res_join.json()
    assert "alumno@ateneo.edu.ec" in joined_room["participantes"]

    # 4. Docente avanza la sala a fase de resolución
    res_resolucion = client.post(
        f"/api/ateneo/room/{room_code}/status",
        data={"nuevo_estado": "resolucion"},
        headers=teacher_headers
    )
    assert res_resolucion.status_code == 200
    assert res_resolucion.json()["estado"] == "resolucion"

    # 5. Soporte defensivo de alias de fase (frontend enviando 'consenso' -> normalizado a 'discusion')
    res_alias = client.post(
        f"/api/ateneo/room/{room_code}/status",
        data={"nuevo_estado": "consenso"},
        headers=teacher_headers
    )
    assert res_alias.status_code == 200
    assert res_alias.json()["estado"] == "discusion"

    # 6. Alumno NO puede cambiar el estado de la sala (RBAC estricto 403)
    res_unauthorized = client.post(
        f"/api/ateneo/room/{room_code}/status",
        data={"nuevo_estado": "finalizado"},
        headers=student_headers
    )
    assert res_unauthorized.status_code == 403

    # 7. Docente consulta sus salas activas (/api/ateneo/teacher/rooms)
    res_teacher_rooms = client.get("/api/ateneo/teacher/rooms", headers=teacher_headers)
    assert res_teacher_rooms.status_code == 200
    rooms_list = res_teacher_rooms.json()
    assert isinstance(rooms_list, list)
    found_room = next((r for r in rooms_list if r["room_code"] == room_code), None)
    assert found_room is not None
    assert "analitica_consenso" in found_room
    assert "score_promedio" in found_room["analitica_consenso"]

    # 8. Docente finaliza la sesión
    res_final = client.post(
        f"/api/ateneo/room/{room_code}/status",
        data={"nuevo_estado": "finalizado"},
        headers=teacher_headers
    )
    assert res_final.status_code == 200
    assert res_final.json()["estado"] == "finalizado"

    # 9. Docente elimina la sala de prueba
    res_del = client.delete(f"/api/ateneo/room/{room_code}", headers=teacher_headers)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "ok"


def test_collaborative_group_mode_lifecycle():
    """Valida el ciclo completo de Modo Grupal (Ateneo Colaborativo), tolerancia de prefijos y dictamen grupal."""
    teacher_token = get_auth_token("docente@ateneo.edu.ec", "Docente123!")
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    student_token = get_auth_token("alumno@ateneo.edu.ec", "Alumno123!")
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 1. Crear sala en modo grupal
    res_create = client.post("/api/ateneo/create", data={
        "case_id": "case_ehirn_01",
        "docente_id": "usr_docente_001",
        "docente_nombre": "Dr. Carlos Andrade",
        "modo_resolucion": "grupal"
    }, headers=teacher_headers)
    assert res_create.status_code == 200
    room = res_create.json()
    room_code = room["room_code"]
    assert room["modo_resolucion"] == "grupal"
    assert "borrador_grupal" in room
    assert room["borrador_grupal"]["texto"] == ""

    # 2. Tolerancia de prefijo de código (consultar por código corto sin 'ATENEO-')
    short_code = room_code.replace("ATENEO-", "")
    res_lookup = client.get(f"/api/ateneo/room/{short_code}")
    assert res_lookup.status_code == 200
    assert res_lookup.json()["room_code"] == room_code

    # 3. Conmutar modo a 'individual' y luego de vuelta a 'grupal'
    res_mode_ind = client.post(
        f"/api/ateneo/room/{room_code}/mode",
        data={"modo_resolucion": "individual"},
        headers=teacher_headers
    )
    assert res_mode_ind.status_code == 200
    assert res_mode_ind.json()["modo_resolucion"] == "individual"

    res_mode_grp = client.post(
        f"/api/ateneo/room/{room_code}/mode",
        data={"modo_resolucion": "grupal"},
        headers=teacher_headers
    )
    assert res_mode_grp.status_code == 200
    assert res_mode_grp.json()["modo_resolucion"] == "grupal"

    # 4. Iniciar fase de resolución
    client.post(
        f"/api/ateneo/room/{room_code}/status",
        data={"nuevo_estado": "resolucion"},
        headers=teacher_headers
    )

    # 5. Enviar dictamen de consenso colectivo (submit-group)
    res_group_submit = client.post(
        f"/api/ateneo/room/{room_code}/submit-group",
        data={
            "respuesta_grupal": "Sospecha nosológica de Enfermedad Hemorrágica del Recién Nacido (EHIRN) forma clásica por inicio a los 3 días de vida sin profilaxis neonatal de Vitamina K. Conducta terapéutica de urgencia: Administrar Fitomenadiona 1 mg IM o infusión IV lenta, monitoreo de tiempos de coagulación TP/TTP y hemodinámica continua según GPC MSP Ecuador.",
            "user_nombre": "Equipo Ateneo Cohorte A"
        },
        headers=student_headers
    )
    assert res_group_submit.status_code == 200
    body = res_group_submit.json()
    assert body["status"] == "ok"
    assert "evaluacion" in body
    assert body["evaluacion"]["score"] > 0
    assert body["room"]["resultado_evaluacion_grupal"] is not None
    assert body["room"]["dictamen_grupal_emitido"] is True

    # 6. Limpieza: Eliminar sala
    client.delete(f"/api/ateneo/room/{room_code}", headers=teacher_headers)

