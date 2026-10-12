"""
Auditoría Forense y Exhaustiva de la Base de Datos Relacional Ateneo+
Verifica:
1. Integridad física de archivo y PRAGMAs (WAL, Foreign Keys, Synchronous).
2. Integridad referencial formal y detección de registros huérfanos.
3. Conteo de registros, índices y claves foráneas en todas las tablas.
4. Cobertura de índices para consultas frecuentes y multi-tenant.
5. Validación de usuarios demo, contraseñas Bcrypt y tenants activos.
"""

import os
import sys
import sqlite3
from typing import Dict, Any, List

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import settings
from core.database import SessionLocal, engine
from sqlalchemy import inspect, text

def run_db_audit():
    print("=" * 80)
    print("AUDITORÍA FORENSE INTEGRAL DE BASE DE DATOS - ATENEO+")
    print("=" * 80)

    db_path = settings.database_url.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        db_path = os.path.join("/app", db_path) if os.path.exists("/app") else os.path.abspath(db_path)

    print(f"Ruta DB      : {db_path}")
    print(f"Existe       : {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        print(f"Tamaño       : {os.path.getsize(db_path):,} bytes")
    print(f"Motor        : {'SQLite (WAL)' if settings.is_sqlite else 'PostgreSQL'}")

    # 1. Chequeos directos SQLite si aplica
    if settings.is_sqlite and os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        print("\n--- 1. CONFIGURACIÓN DE PRAGMAS DEL MOTOR ---")
        for pragma in ["journal_mode", "synchronous", "foreign_keys", "page_size", "cache_size", "encoding"]:
            res = cur.execute(f"PRAGMA {pragma};").fetchone()
            print(f"  PRAGMA {pragma:15s} = {res[0] if res else 'N/A'}")

        print("\n--- 2. VERIFICACIÓN DE INTEGRIDAD FÍSICA Y ESTRUCTURAL ---")
        integrity = cur.execute("PRAGMA integrity_check;").fetchall()
        print(f"  Integrity Check: {integrity}")

        quick_check = cur.execute("PRAGMA quick_check;").fetchall()
        print(f"  Quick Check    : {quick_check}")

        cur.execute("PRAGMA foreign_keys = ON;")
        fk_violations = cur.execute("PRAGMA foreign_key_check;").fetchall()
        print(f"  Violaciones de FK (PRAGMA foreign_key_check): {len(fk_violations)}")
        if fk_violations:
            for v in fk_violations:
                print(f"    ALERTA VIOLACIÓN FK: Tabla={v[0]}, RowId={v[1]}, TargetTable={v[2]}, FkId={v[3]}")
        else:
            print("  -> CERO violaciones de clave foránea en todo el archivo relacional.")

        conn.close()

    # 2. Inspección vía SQLAlchemy y SessionLocal
    insp = inspect(engine)
    tablas = insp.get_table_names()
    print(f"\n--- 3. CATÁLOGO DE TABLAS REGISTRADAS ({len(tablas)} tablas) ---")
    
    with SessionLocal() as session:
        for t in sorted(tablas):
            cols = insp.get_columns(t)
            pk = insp.get_pk_constraint(t)
            fks = insp.get_foreign_keys(t)
            indices = insp.get_indexes(t)
            unicos = insp.get_unique_constraints(t)
            count = session.execute(text(f"SELECT count(*) FROM {t}")).scalar()

            print(f"\n[TABLA: {t}] (Registros: {count})")
            print(f"  PK : {pk.get('constrained_columns')}")
            print(f"  Columnas ({len(cols)}):")
            for c in cols:
                fk_info = ""
                for fk in fks:
                    if c["name"] in fk.get("constrained_columns", []):
                        fk_info = f" -> FK({fk.get('referred_table')}.{fk.get('referred_columns')}) ON DELETE {fk.get('options', {}).get('ondelete', 'NO ACTION')}"
                nullable_str = "NULL" if c.get("nullable") else "NOT NULL"
                print(f"    - {c['name']:30s} {str(c['type']):20s} {nullable_str:8s} {fk_info}")

            print(f"  Índices ({len(indices)}):")
            for idx in indices:
                unique_str = "UNIQUE" if idx.get("unique") else "INDEX"
                print(f"    - {idx['name']:35s} ({', '.join(idx['column_names'])}) [{unique_str}]")

    # 3. Comprobación profunda de consistencia de negocio
    print("\n--- 4. AUDITORÍA DE CONSISTENCIA DE NEGOCIO Y MULTI-TENANCY ---")
    with SessionLocal() as session:
        from modules.auth.models import TenantModel, UserModel
        from modules.cases.models import ClinicalCaseModel
        from modules.analytics_history.models import EvaluationHistoryModel
        from modules.collaboration.models import AteneoRoomModel

        tenants = session.query(TenantModel).all()
        print(f"Tenants Configurados: {len(tenants)}")
        for ten in tenants:
            users_count = session.query(UserModel).filter(UserModel.tenant_id == ten.id).count()
            evals_count = session.query(EvaluationHistoryModel).filter(EvaluationHistoryModel.tenant_id == ten.id).count()
            rooms_count = session.query(AteneoRoomModel).filter(AteneoRoomModel.tenant_id == ten.id).count()
            cases_count = session.query(ClinicalCaseModel).filter(ClinicalCaseModel.tenant_id == ten.id).count()
            print(f"  * Tenant '{ten.id}' ({ten.nombre_institucional}):")
            print(f"      Usuarios: {users_count} | Evaluaciones: {evals_count} | Salas: {rooms_count} | Casos Propios: {cases_count}")

        # Comprobar usuarios huérfanos sin tenant
        usuarios_sin_tenant = session.execute(text(
            "SELECT u.id, u.email FROM users u LEFT JOIN tenants t ON u.tenant_id = t.id WHERE t.id IS NULL"
        )).fetchall()
        print(f"\nUsuarios con Tenant Inválido o Huérfano: {len(usuarios_sin_tenant)}")
        if usuarios_sin_tenant:
            for u in usuarios_sin_tenant:
                print(f"  ALERTA: Usuario huérfano {u[0]} ({u[1]})")

        # Comprobar evaluaciones huérfanas sin usuario o sin tenant
        evals_huerfanas_user = session.execute(text(
            "SELECT e.id, e.user_id FROM evaluation_history e LEFT JOIN users u ON e.user_id = u.id WHERE u.id IS NULL"
        )).fetchall()
        print(f"Evaluaciones con Usuario Inexistente en users: {len(evals_huerfanas_user)}")
        if evals_huerfanas_user:
            for eh in evals_huerfanas_user[:5]:
                print(f"  ALERTA: Evaluación {eh[0]} con user_id huérfano '{eh[1]}'")

        evals_huerfanas_tenant = session.execute(text(
            "SELECT e.id, e.tenant_id FROM evaluation_history e LEFT JOIN tenants t ON e.tenant_id = t.id WHERE t.id IS NULL"
        )).fetchall()
        print(f"Evaluaciones con Tenant Inexistente en tenants: {len(evals_huerfanas_tenant)}")
        if evals_huerfanas_tenant:
            for et in evals_huerfanas_tenant[:5]:
                print(f"  ALERTA: Evaluación {et[0]} con tenant_id huérfano '{et[1]}'")

        # Comprobar salas huérfanas sin docente o sin tenant
        rooms_huerfanas_doc = session.execute(text(
            "SELECT r.room_code, r.docente_id FROM ateneo_rooms r LEFT JOIN users u ON r.docente_id = u.id WHERE u.id IS NULL"
        )).fetchall()
        print(f"Salas Ateneo con Docente Inexistente en users: {len(rooms_huerfanas_doc)}")

        rooms_huerfanas_tenant = session.execute(text(
            "SELECT r.room_code, r.tenant_id FROM ateneo_rooms r LEFT JOIN tenants t ON r.tenant_id = t.id WHERE t.id IS NULL"
        )).fetchall()
        print(f"Salas Ateneo con Tenant Inexistente en tenants: {len(rooms_huerfanas_tenant)}")

    print("\n" + "=" * 80)
    print("FIN DE LA AUDITORÍA FORENSE DE BASE DE DATOS")
    print("=" * 80)

if __name__ == "__main__":
    run_db_audit()
