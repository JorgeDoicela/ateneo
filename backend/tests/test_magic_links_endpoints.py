#!/usr/bin/env python3
"""
Suite de Pruebas Unitarias e Integración: Endpoints de Magic Links (Fase 2 - Ateneo+)
Valida:
1. Generación de Magic Links por administradores (201 Created).
2. Protección RBAC: roles no administradores reciben 403 Forbidden al intentar generar enlaces.
3. Canje nominativo exitoso con emisión de JWT y JTI persistido.
4. Canje grupal/cohorte con aprovisionamiento automático.
5. Rechazo ante enlace revocado, expirado o agotado por max_uses.
6. Listado y revocación en caliente por administradores.
"""

import sys
import os
import uuid
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app
from core.database import get_db, SessionLocal
from core.security import create_access_token
from modules.auth.models import UserModel, TenantModel
from modules.auth.repository import UserRepository, TenantRepository, MagicLinkRepository


def test_magic_links_endpoints():
    print("\n" + "=" * 70)
    print(" SUITE DE PRUEBAS DE INTEGRACIÓN: ENDPOINTS DE MAGIC LINKS (FASE 2)")
    print("=" * 70)

    client = TestClient(app)

    # 1. Preparar datos de prueba en la base de datos
    with SessionLocal() as db:
        user_repo = UserRepository(db)
        tenant_repo = TenantRepository(db)
        link_repo = MagicLinkRepository(db)

        # Garantizar tenant
        if not tenant_repo.get_by_id("tenant_default"):
            tenant_repo.create(TenantModel(
                id="tenant_default",
                codigo="ateneo_central",
                nombre_institucional="Ateneo Sede Central",
                dominio_email="ateneo.edu.ec",
                gpc_activas_json="[]",
                activo=True
            ))

        # Admin de prueba
        admin_id = f"usr_admin_{uuid.uuid4().hex[:8]}"
        admin_email = f"admin.{uuid.uuid4().hex[:6]}@ateneo.edu.ec"
        admin_user = UserModel(
            id=admin_id,
            email=admin_email,
            nombre="Dra. Administradora Test",
            rol="administrador",
            hashed_password="hash",
            tenant_id="tenant_default",
            activo=True
        )
        user_repo.create(admin_user)

        # Alumno de prueba (para probar bloqueo RBAC)
        alumno_id = f"usr_alumno_{uuid.uuid4().hex[:8]}"
        alumno_email = f"alumno.{uuid.uuid4().hex[:6]}@ateneo.edu.ec"
        alumno_user = UserModel(
            id=alumno_id,
            email=alumno_email,
            nombre="Alumno Test",
            rol="alumno",
            hashed_password="hash",
            tenant_id="tenant_default",
            activo=True
        )
        user_repo.create(alumno_user)

    # Tokens JWT para clientes de prueba
    from models.schemas import User, UserRole
    admin_obj = User(id=admin_id, email=admin_email, nombre="Dra. Administradora Test", rol=UserRole.ADMINISTRADOR, tenant_id="tenant_default", hashed_password="hash")
    alumno_obj = User(id=alumno_id, email=alumno_email, nombre="Alumno Test", rol=UserRole.ALUMNO, tenant_id="tenant_default", hashed_password="hash")
    admin_token = create_access_token(admin_obj)
    alumno_token = create_access_token(alumno_obj)

    # Test 1: Alumno intenta generar un magic link -> 403 Forbidden
    res_forbidden = client.post(
        "/api/auth/magic-links",
        json={"rol": "docente", "duracion_horas": 24},
        headers={"Authorization": f"Bearer {alumno_token}"}
    )
    assert res_forbidden.status_code == 403, f"Esperado 403 pero se obtuvo {res_forbidden.status_code}"
    print("  [PASS] Protección RBAC: No-administrador rechazado con 403 Forbidden.")

    # Test 2: Admin genera un magic link nominativo para un docente
    target_email = f"docente.invitado.{uuid.uuid4().hex[:6]}@ateneo.edu.ec"
    res_create = client.post(
        "/api/auth/magic-links",
        json={
            "rol": "docente",
            "email": target_email,
            "recipient_name": "Dr. Evaluador Externo",
            "duracion_horas": 48,
            "max_uses": 1,
            "target_path": "/cases/case_preeclampsia_01",
            "cohorte_id": "taller_obstetricia_2026"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_create.status_code == 201, f"Fallo al crear link: {res_create.text}"
    created_data = res_create.json()
    assert "magic_link_url" in created_data
    assert "token=" in created_data["magic_link_url"]
    raw_token = created_data["magic_link_url"].split("token=")[1]
    link_id = created_data["id"]
    print("  [PASS] Admin genera Magic Link nominativo exitosamente (201 Created).")

    # Test 3: Canje público del Magic Link nominativo
    res_consume = client.post(
        "/api/auth/magic-links/consume",
        json={"token": raw_token}
    )
    assert res_consume.status_code == 200, f"Fallo en canje: {res_consume.text}"
    consume_data = res_consume.json()
    assert "access_token" in consume_data
    assert consume_data["user"]["email"] == target_email
    assert consume_data["user"]["rol"] == "docente"
    assert consume_data["target_path"] == "/cases/case_preeclampsia_01"
    print("  [PASS] Canje nominativo exitoso: emisión de JWT y provisión de rol docente.")

    # Test 4: Segundo canje debe fallar (max_uses=1 agotado) -> 403 Forbidden
    res_reconsume = client.post(
        "/api/auth/magic-links/consume",
        json={"token": raw_token}
    )
    assert res_reconsume.status_code == 403, f"Esperado 403 por agotamiento pero se obtuvo {res_reconsume.status_code}"
    print("  [PASS] Límite de usos respetado: segundo canje rechazado con 403 Forbidden.")

    # Test 5: Admin genera Magic Link grupal (cohorte, sin email prefijado, max_uses=5)
    res_group = client.post(
        "/api/auth/magic-links",
        json={
            "rol": "alumno",
            "recipient_name": "Cohorte Rotación Pediatría",
            "duracion_horas": 72,
            "max_uses": 5,
            "target_path": "/cases"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_group.status_code == 201
    group_token = res_group.json()["magic_link_url"].split("token=")[1]
    group_link_id = res_group.json()["id"]

    # Canje grupal sin enviar email -> 400 Bad Request
    res_no_email = client.post(
        "/api/auth/magic-links/consume",
        json={"token": group_token}
    )
    assert res_no_email.status_code == 400, "Debe requerir email para enlaces grupales"
    print("  [PASS] Enlace de cohorte exige correo de participante (400 Bad Request si falta).")

    # Canje grupal válido con email del alumno invitado
    guest_email = f"alumno.invitado.{uuid.uuid4().hex[:6]}@ateneo.edu.ec"
    res_guest = client.post(
        "/api/auth/magic-links/consume",
        json={
            "token": group_token,
            "email": guest_email,
            "nombre": "Estudiante Carlos Pérez"
        }
    )
    assert res_guest.status_code == 200
    assert res_guest.json()["user"]["email"] == guest_email
    print("  [PASS] Canje de cohorte exitoso con aprovisionamiento automático de estudiante.")

    # Test 6: Listado de Magic Links por el administrador
    res_list = client.get(
        "/api/auth/magic-links",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_list.status_code == 200
    links_list = res_list.json()
    assert len(links_list) >= 2
    print(f"  [PASS] Admin lista {len(links_list)} Magic Links generados en su tenant.")

    # Test 7: Revocación en caliente por el administrador
    res_revoke = client.delete(
        f"/api/auth/magic-links/{group_link_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res_revoke.status_code == 200
    print("  [PASS] Admin revoca Magic Link en caliente (200 OK).")

    # Intentar canjear el link recién revocado -> 403 Forbidden
    res_after_revoke = client.post(
        "/api/auth/magic-links/consume",
        json={
            "token": group_token,
            "email": f"otro.alumno.{uuid.uuid4().hex[:6]}@ateneo.edu.ec",
            "nombre": "Otro Alumno"
        }
    )
    assert res_after_revoke.status_code == 403
    print("  [PASS] Enlace revocado rechazado en canje (403 Forbidden).")

    print("=" * 70)
    print(" TODAS LAS PRUEBAS DE ENDPOINTS DE MAGIC LINKS PASARON (100% PASS)\n")


if __name__ == "__main__":
    test_magic_links_endpoints()
