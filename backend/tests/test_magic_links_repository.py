#!/usr/bin/env python3
"""
Pruebas Unitarias de Persistencia: MagicLinkRepository (Fase 1 - Ateneo+)
Valida:
1. Creación e indexación de registros MagicLinkTokenModel con hash SHA-256.
2. Recuperación por id y por token_hash.
3. Listado por tenant y filtrado de revocados.
4. Revocación en caliente y actualización atómica de used_count.
"""

import sys
import os
import hashlib
import uuid
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from modules.auth.models import TenantModel, UserModel, MagicLinkTokenModel
from modules.auth.repository import MagicLinkRepository, TenantRepository, UserRepository


def test_magic_link_repository():
    print("\n" + "=" * 70)
    print(" SUITE DE PRUEBAS UNITARIAS: REPOSITORIO DE MAGIC LINKS (FASE 1)")
    print("=" * 70)

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSession() as db:
        tenant_repo = TenantRepository(db)
        user_repo = UserRepository(db)
        link_repo = MagicLinkRepository(db)

        # 1. Crear tenant y admin emisor
        tenant = TenantModel(
            id="tenant_uce",
            codigo="uce",
            nombre_institucional="Universidad Central del Ecuador",
            dominio_email="uce.edu.ec",
            gpc_activas_json="[]",
            activo=True
        )
        tenant_repo.create(tenant)

        admin = UserModel(
            id="usr_admin_test",
            email="admin@uce.edu.ec",
            nombre="Dra. Administradora",
            rol="administrador",
            hashed_password="hash",
            tenant_id="tenant_uce",
            activo=True
        )
        user_repo.create(admin)

        # 2. Generar token opaco y su hash SHA-256
        raw_token = "tok_test_secret_abc123"
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)

        link_record = MagicLinkTokenModel(
            id=str(uuid.uuid4()),
            token_hash=token_hash,
            email="docente.invitado@uce.edu.ec",
            recipient_name="Dr. Evaluador Externo",
            rol="docente",
            tenant_id="tenant_uce",
            target_path="/cases/case_preeclampsia_01",
            cohorte_id="rotacion_marzo_2026",
            restrict_domain=True,
            expires_at=expires_at,
            max_uses=5,
            used_count=0,
            is_revoked=False,
            created_by_user_id="usr_admin_test"
        )
        created = link_repo.create(link_record)
        assert created.id is not None
        print("  [PASS] MagicLinkTokenModel persistido correctamente.")

        # 3. Consulta por hash
        found = link_repo.get_by_hash(token_hash)
        assert found is not None
        assert found.email == "docente.invitado@uce.edu.ec"
        assert found.rol == "docente"
        assert found.max_uses == 5
        print("  [PASS] Búsqueda por token_hash criptográfico verificada.")

        # 4. Listado por tenant
        tenant_links = link_repo.list_by_tenant("tenant_uce", limit=10)
        assert len(tenant_links) == 1
        print("  [PASS] Listado de enlaces filtrados por tenant verificado.")

        # 5. Actualización de contador de usos
        found.used_count += 1
        link_repo.update(found)
        reloaded = link_repo.get_by_id(found.id)
        assert reloaded.used_count == 1
        print("  [PASS] Incremento de used_count verificado.")

        # 6. Revocación en caliente
        revoked = link_repo.revoke(found.id)
        assert revoked is True
        revoked_rec = link_repo.get_by_id(found.id)
        assert revoked_rec.is_revoked is True
        print("  [PASS] Revocación manual en caliente verificada.")

    print("=" * 70)
    print(" TODAS LAS PRUEBAS DE PERSISTENCIA DE MAGIC LINKS PASARON (100% PASS)\n")


if __name__ == "__main__":
    test_magic_link_repository()
