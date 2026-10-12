#!/usr/bin/env python3
"""
Script Maestro de Migración Idempotente: Tabla magic_link_tokens (Fase 1 - Ateneo+)
Valida y actualiza la estructura relacional para Magic Links e Invitaciones Configurables:
- Crea la tabla magic_link_tokens con claves foráneas e índices de alto rendimiento.
- Preserva de forma transaccional el 100% de los datos preexistentes en ateneo_clinical.db.
- Verifica integridad física (PRAGMA integrity_check) y consistencia relacional (PRAGMA foreign_key_check).
"""

import sys
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ateneo_clinical.db"

if not DB_PATH.exists():
    ALT_PATH = Path("/app/data/ateneo_clinical.db")
    if ALT_PATH.exists():
        DB_PATH = ALT_PATH
    else:
        print(f"[ERROR] Base de datos no encontrada en {DB_PATH} ni en {ALT_PATH}")
        sys.exit(1)


def run_migration():
    print(f"\n[ATENEO+ MIGRACIÓN MAGIC LINKS] Conectando a {DB_PATH}...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # 1. Contar registros iniciales para verificar preservación
        cursor.execute("SELECT count(*) FROM evaluation_history")
        initial_eval_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM ateneo_rooms")
        initial_rooms_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM users")
        initial_users_count = cursor.fetchone()[0]

        print(f"  • Registros preexistentes: {initial_eval_count} evaluaciones, {initial_rooms_count} salas, {initial_users_count} usuarios.")

        # 2. Crear tabla magic_link_tokens si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='magic_link_tokens'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            print("  • Creando tabla magic_link_tokens...")
            cursor.execute("""
                CREATE TABLE magic_link_tokens (
                    id VARCHAR(64) PRIMARY KEY,
                    token_hash VARCHAR(64) NOT NULL UNIQUE,
                    email VARCHAR(150),
                    recipient_name VARCHAR(150),
                    rol VARCHAR(50) NOT NULL DEFAULT 'alumno',
                    tenant_id VARCHAR(50) NOT NULL,
                    target_path VARCHAR(255) NOT NULL DEFAULT '/cases',
                    cohorte_id VARCHAR(50) DEFAULT 'general',
                    restrict_domain BOOLEAN NOT NULL DEFAULT 0,
                    expires_at TIMESTAMP NOT NULL,
                    max_uses INTEGER NOT NULL DEFAULT 1,
                    used_count INTEGER NOT NULL DEFAULT 0,
                    is_revoked BOOLEAN NOT NULL DEFAULT 0,
                    created_by_user_id VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_magic_token_hash ON magic_link_tokens(token_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_magic_tenant_active ON magic_link_tokens(tenant_id, is_revoked)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_magic_expires ON magic_link_tokens(expires_at)")
            print("  • Tabla magic_link_tokens e índices creados con éxito.")
        else:
            print("  • La tabla magic_link_tokens ya existe. Validando columnas...")
            cursor.execute("PRAGMA table_info(magic_link_tokens)")
            cols = [row[1] for row in cursor.fetchall()]
            required_cols = [
                "id", "token_hash", "email", "recipient_name", "rol", "tenant_id",
                "target_path", "cohorte_id", "restrict_domain", "expires_at",
                "max_uses", "used_count", "is_revoked", "created_by_user_id", "created_at"
            ]
            for col in required_cols:
                assert col in cols, f"Columna obligatoria '{col}' ausente en magic_link_tokens"
            print("  • Estructura de columnas verificada al 100%.")

        conn.commit()

        # 3. Validar preservación transaccional
        cursor.execute("SELECT count(*) FROM evaluation_history")
        final_eval_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM ateneo_rooms")
        final_rooms_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM users")
        final_users_count = cursor.fetchone()[0]

        assert final_eval_count == initial_eval_count, "Inconsistencia en conteo de evaluaciones"
        assert final_rooms_count == initial_rooms_count, "Inconsistencia en conteo de salas"
        assert final_users_count == initial_users_count, "Inconsistencia en conteo de usuarios"

        # 4. Validar integridad física y claves foráneas
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchall()
        assert integrity == [('ok',)], f"Fallo en PRAGMA integrity_check: {integrity}"

        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        assert len(fk_violations) == 0, f"Violaciones de clave foránea detectadas: {fk_violations}"

        print("\n[OK] Migración de Magic Links completada exitosamente.")
        print("  • PRAGMA integrity_check: OK")
        print("  • PRAGMA foreign_key_check: 0 violaciones")
        print(f"  • Evaluaciones preservadas: {final_eval_count}")
        print(f"  • Salas preservadas: {final_rooms_count}")
        print(f"  • Usuarios preservados: {final_users_count}")

    except Exception as e:
        conn.rollback()
        print(f"[FATAL] Error durante la migración: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
