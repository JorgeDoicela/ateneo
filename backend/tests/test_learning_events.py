import sys
from pathlib import Path
import json
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.database import SessionLocal
from modules.analytics_history.models import LearningActivityEventModel
from modules.analytics_history.repository import HistoryRepository, LearningEventRepository
from modules.analytics_history.service import AnalyticsHistoryService
from models.schemas import LearningActivityEventCreate, LearningActivityEventResponse


def test_learning_event_pydantic_schemas():
    """Valida los contratos de serialización Pydantic de eventos granulares."""
    create_req = LearningActivityEventCreate(
        case_id="case_preeclampsia_01",
        event_type="case_opened",
        metadata={"navegador": "Chrome", "modo": "fases"},
        tenant_id="tenant_uce"
    )
    cdata = create_req.model_dump()
    assert cdata["case_id"] == "case_preeclampsia_01"
    assert cdata["event_type"] == "case_opened"
    assert cdata["metadata"]["navegador"] == "Chrome"
    assert cdata["tenant_id"] == "tenant_uce"

    resp = LearningActivityEventResponse(
        id=101,
        user_id="usr_alumno_001",
        tenant_id="tenant_uce",
        case_id="case_preeclampsia_01",
        event_type="case_opened",
        metadata={"navegador": "Chrome"},
        timestamp="2026-10-12T16:00:00"
    )
    rdata = resp.model_dump()
    assert rdata["id"] == 101
    assert rdata["event_type"] == "case_opened"
    print("  [PASS] Contratos Pydantic de eventos de aprendizaje validados.")


def test_learning_event_database_lifecycle():
    """Valida la persistencia física, claves foráneas y consultas en SQLite/SQLAlchemy."""
    db = SessionLocal()
    try:
        repo = LearningEventRepository(db)
        event = LearningActivityEventModel(
            user_id="usr_alumno_001",
            tenant_id="tenant_default",
            case_id="case_preeclampsia_01",
            event_type="paraclinical_inspected",
            metadata_json=json.dumps({"estudio": "ecg_trazado", "zoom": 1.5}),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        saved = repo.create(event)
        assert saved.id is not None

        # Consultar por usuario
        user_events = repo.list_by_user("usr_alumno_001", limit=10)
        assert len(user_events) > 0
        assert any(e.event_type == "paraclinical_inspected" for e in user_events)

        # Consultar conteo por tipo
        count = repo.count_by_type("paraclinical_inspected")
        assert count >= 1

        # Limpiar registro creado en el test
        db.delete(saved)
        db.commit()
        print("  [PASS] Ciclo de vida y consultas de LearningEventRepository validados.")
    finally:
        db.close()
        from core.database import engine
        engine.dispose()


def test_service_event_recording_and_listing():
    """Valida la API del servicio de analítica para registrar y listar eventos."""
    db = SessionLocal()
    try:
        history_repo = HistoryRepository(db)
        event_repo = LearningEventRepository(db)
        service = AnalyticsHistoryService(history_repo, event_repo)

        # Registrar evento
        event_dict = service.record_learning_event(
            user_id="usr_alumno_001",
            case_id="case_preeclampsia_01",
            event_type="socratic_debrief_opened",
            metadata={"omision": "sulfato_de_magnesio"},
            tenant_id="tenant_default"
        )
        assert event_dict["id"] is not None
        assert event_dict["event_type"] == "socratic_debrief_opened"
        assert event_dict["metadata"]["omision"] == "sulfato_de_magnesio"

        # Listar eventos
        listed = service.list_learning_events(user_id="usr_alumno_001", limit=5)
        assert len(listed) > 0
        assert any(e["event_type"] == "socratic_debrief_opened" for e in listed)

        # Limpiar
        to_del = event_repo.list_by_user("usr_alumno_001", limit=5)
        for d in to_del:
            if d.event_type == "socratic_debrief_opened":
                db.delete(d)
        db.commit()
        print("  [PASS] Métodos record_learning_event y list_learning_events de AnalyticsHistoryService validados.")
    finally:
        db.close()
        from core.database import engine
        engine.dispose()


def test_http_endpoints_learning_events():
    """Valida los endpoints HTTP reales POST /api/analytics/events y GET /api/analytics/events."""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    # 1. Ingesta mediante /api/analytics/events
    payload = {
        "case_id": "case_preeclampsia_01",
        "event_type": "case_opened",
        "metadata": {"origen": "test_http_audit", "viewport": "1920x1080"},
        "tenant_id": "tenant_default"
    }
    res_post = client.post("/api/analytics/events", json=payload)
    assert res_post.status_code == 201, f"Error esperado 201, recibido: {res_post.status_code} - {res_post.text}"
    body = res_post.json()
    assert body["event_type"] == "case_opened"
    assert body["case_id"] == "case_preeclampsia_01"
    event_id = body["id"]

    # 2. Ingesta mediante alias /api/history/events
    res_alias = client.post("/api/history/events", json=payload)
    assert res_alias.status_code == 201

    # 3. Consulta de eventos
    res_get = client.get("/api/analytics/events?case_id=case_preeclampsia_01&limit=10")
    assert res_get.status_code == 200
    events_list = res_get.json()
    assert isinstance(events_list, list)
    assert len(events_list) >= 1

    # Limpiar eventos de prueba creados
    db = SessionLocal()
    try:
        repo = LearningEventRepository(db)
        e1 = repo.get_by_id(event_id)
        if e1:
            db.delete(e1)
        e2 = repo.get_by_id(res_alias.json()["id"])
        if e2:
            db.delete(e2)
        db.commit()
    finally:
        db.close()
        from core.database import engine
        engine.dispose()

    print("  [PASS] Integración HTTP POST /api/analytics/events y GET /api/analytics/events (201 Created & 200 OK) validada.")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" SUITE DE PRUEBAS UNITARIAS: EVENTOS DE APRENDIZAJE (FASE 5)")
    print("=" * 70)
    test_learning_event_pydantic_schemas()
    test_learning_event_database_lifecycle()
    test_service_event_recording_and_listing()
    test_http_endpoints_learning_events()
    print("=" * 70)
    print(" TODAS LAS PRUEBAS DE EVENTOS DE APRENDIZAJE PASARON (100% PASS)\n")
