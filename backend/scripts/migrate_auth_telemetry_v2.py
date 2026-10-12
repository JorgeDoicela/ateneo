#!/usr/bin/env python3
"""
Script Maestro de Migración Idempotente y Validación de Esquema (Fase 5 - Ateneo+)
Valida y actualiza la estructura relacional completa en ateneo_clinical.db:
- Extensiones de users (last_login_at, login_count, etc.)
- Tabla user_sessions (control JTI y revocación)
- Extensiones de evaluation_history (llm_latency_ms, llm_model_used, etc.)
- Tabla learning_activity_events (eventos de interacción de aprendizaje)
- Preservación transaccional absoluta de registros existentes.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Resolver ruta de la base de datos
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
    print(f"\n[ATENEO+ MIGRACIÓN] Conectando a {DB_PATH}...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # 1. Contar registros actuales para verificar preservación
        cursor.execute("SELECT count(*) FROM evaluation_history")
        initial_eval_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM ateneo_rooms")
        initial_rooms_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM users")
        initial_users_count = cursor.fetchone()[0]

        print(f"  • Registros preexistentes: {initial_eval_count} evaluaciones, {initial_rooms_count} salas, {initial_users_count} usuarios.")

        # 2. Verificar columnas de users
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [row[1] for row in cursor.fetchall()]

        user_alter_statements = [
            ("last_login_at", "ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP"),
            ("login_count", "ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0"),
            ("failed_login_attempts", "ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"),
            ("locked_until", "ALTER TABLE users ADD COLUMN locked_until TIMESTAMP"),
            ("email_verified", "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0")
        ]
        for col_name, sql in user_alter_statements:
            if col_name not in user_cols:
                print(f"  • Aplicando DDL en users: {col_name}")
                cursor.execute(sql)

        # 3. Verificar tabla user_sessions
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")
        if not cursor.fetchone():
            print("  • Creando tabla user_sessions...")
            cursor.execute("""
                CREATE TABLE user_sessions (
                    id VARCHAR(64) PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL,
                    tenant_id VARCHAR(50) NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent VARCHAR(255),
                    is_revoked BOOLEAN NOT NULL DEFAULT 0,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_session_user ON user_sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_session_revoked ON user_sessions(is_revoked)")

        # 4. Verificar columnas de evaluation_history
        cursor.execute("PRAGMA table_info(evaluation_history)")
        eval_cols = [row[1] for row in cursor.fetchall()]

        eval_alter_statements = [
            ("llm_latency_ms", "ALTER TABLE evaluation_history ADD COLUMN llm_latency_ms FLOAT DEFAULT 0.0"),
            ("llm_model_used", "ALTER TABLE evaluation_history ADD COLUMN llm_model_used VARCHAR(50) DEFAULT 'gemini-3.8-flash'"),
            ("rag_tokens_used", "ALTER TABLE evaluation_history ADD COLUMN rag_tokens_used INTEGER DEFAULT 0"),
            ("paraclinical_studies_count", "ALTER TABLE evaluation_history ADD COLUMN paraclinical_studies_count INTEGER DEFAULT 0")
        ]
        for col_name, sql in eval_alter_statements:
            if col_name not in eval_cols:
                print(f"  • Aplicando DDL en evaluation_history: {col_name}")
                cursor.execute(sql)

        # 5. Crear tabla learning_activity_events si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='learning_activity_events'")
        if not cursor.fetchone():
            print("  • Creando tabla learning_activity_events...")
            cursor.execute("""
                CREATE TABLE learning_activity_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(100) NOT NULL,
                    tenant_id VARCHAR(50) NOT NULL,
                    case_id VARCHAR(100) NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_event_user_case_time ON learning_activity_events(user_id, case_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_event_tenant_type ON learning_activity_events(tenant_id, event_type)")

        conn.commit()

        # 6. Validar integridad y preservación de registros
        cursor.execute("SELECT count(*) FROM evaluation_history")
        final_eval_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM ateneo_rooms")
        final_rooms_count = cursor.fetchone()[0]

        cursor.execute("SELECT count(*) FROM users")
        final_users_count = cursor.fetchone()[0]

        assert final_eval_count == initial_eval_count, "Inconsistencia en conteo de evaluaciones"
        assert final_rooms_count == initial_rooms_count, "Inconsistencia en conteo de salas"
        assert final_users_count == initial_users_count, "Inconsistencia en conteo de usuarios"

        # 7. Comprobación estricta de integridad y claves foráneas
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchall()
        assert integrity == [('ok',)], f"Fallo en PRAGMA integrity_check: {integrity}"

        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        assert len(fk_violations) == 0, f"Violaciones de clave foránea detectadas: {fk_violations}"

        print(f"\n[OK] Migración idempotente completada exitosamente.")
        print(f"  • PRAGMA integrity_check: OK")
        print(f"  • PRAGMA foreign_key_check: 0 violaciones")
        print(f"  • Evaluaciones preservadas: {final_eval_count}")
        print(f"  • Salas preservadas: {final_rooms_count}")
        print(f"  • Usuarios verificados: {final_users_count}")

    except Exception as e:
        conn.rollback()
        print(f"[FATAL] Error durante la migración: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
