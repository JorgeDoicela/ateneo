import sys
from pathlib import Path
import json
import datetime

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.database import SessionLocal
from modules.analytics_history.models import EvaluationHistoryModel
from modules.analytics_history.repository import HistoryRepository
from modules.analytics_history.service import AnalyticsHistoryService
from models.schemas import EvaluationResult, PhaseEvaluationResult, CitaNormativa


def test_pydantic_schemas_telemetry():
    """Valida los contratos de schemas Pydantic con telemetría de inferencia."""
    cita = CitaNormativa(guia="GPC Preeclampsia", seccion="Tratamiento", pagina=14, texto_relevante="Sulfato de magnesio")
    eval_res = EvaluationResult(
        score=9.2,
        score_max=10,
        aciertos=["Manejo con sulfato de magnesio"],
        omisiones=[],
        competencias_deficientes=[],
        cita_normativa=cita,
        retroalimentacion_general="Excelente razonamiento clínico.",
        faithfulness_score=0.95,
        llm_latency_ms=1240.5,
        llm_model_used="gemini-3.8-flash",
        rag_tokens_used=420,
        paraclinical_studies_count=2
    )

    data = eval_res.model_dump()
    assert data["llm_latency_ms"] == 1240.5
    assert data["llm_model_used"] == "gemini-3.8-flash"
    assert data["rag_tokens_used"] == 420
    assert data["paraclinical_studies_count"] == 2

    phase_res = PhaseEvaluationResult(
        fase_numero=1,
        score_fase=8.5,
        aciertos=["Identificación de signos de alarma"],
        omisiones=[],
        competencias_deficientes=[],
        cita_normativa=cita,
        retroalimentacion_fase="Buena aproximación inicial.",
        llm_latency_ms=980.2,
        llm_model_used="gemini-3.8-flash",
        rag_tokens_used=310,
        paraclinical_studies_count=1
    )
    pdata = phase_res.model_dump()
    assert pdata["llm_latency_ms"] == 980.2
    assert pdata["llm_model_used"] == "gemini-3.8-flash"
    assert pdata["rag_tokens_used"] == 310
    assert pdata["paraclinical_studies_count"] == 1
    print("  [PASS] Contratos Pydantic de telemetría de inferencia (EvaluationResult y PhaseEvaluationResult) validados.")


def test_database_telemetry_persistence():
    """Valida la persistencia física y recuperación de telemetría en SQLite/SQLAlchemy."""
    db = SessionLocal()
    try:
        repo = HistoryRepository(db)
        test_eval = EvaluationHistoryModel(
            user_id="usr_alumno_001",
            user_email="alumno@ateneo.edu.ec",
            case_id="case_telemetry_audit",
            guia_asociada="GPC Hipertensión",
            case_title="Auditoría de Inferencia Clínica",
            score=8.8,
            score_max=10,
            faithfulness_score=0.92,
            cohorte_id="cohorte_audit_2026",
            tiempo_segundos=145.0,
            llm_latency_ms=1350.2,
            llm_model_used="gemini-3.8-flash",
            rag_tokens_used=580,
            paraclinical_studies_count=3,
            tenant_id="tenant_default",
            aciertos_json=json.dumps(["Control de TA"]),
            omisiones_json=json.dumps([]),
            competencias_json=json.dumps([]),
            cita_normativa_json=json.dumps({"guia": "GPC Hipertensión"}),
            retroalimentacion_general="Dictamen verificado con telemetría.",
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        saved = repo.create(test_eval)
        assert saved.id is not None

        # Recuperar y verificar campos de telemetría
        retrieved = repo.get_by_id(saved.id)
        assert retrieved is not None
        assert retrieved.llm_latency_ms == 1350.2
        assert retrieved.llm_model_used == "gemini-3.8-flash"
        assert retrieved.rag_tokens_used == 580
        assert retrieved.paraclinical_studies_count == 3

        # Limpiar registro de test para no dejar residuos
        db.delete(retrieved)
        db.commit()
        print("  [PASS] Persistencia relacional ACID y recuperación de telemetría en BD validada.")
    finally:
        db.close()


def test_coordinator_analytics_telemetry_metrics():
    """Valida el cálculo de métricas de telemetría institucional en HistoryService."""
    db = SessionLocal()
    try:
        repo = HistoryRepository(db)
        service = AnalyticsHistoryService(repo)
        analytics = service.get_coordinator_analytics(tenant_id="tenant_uce")

        assert "telemetria_ia" in analytics
        telemetria = analytics["telemetria_ia"]

        assert "promedio_latencia_ms" in telemetria
        assert isinstance(telemetria["promedio_latencia_ms"], (int, float))
        assert telemetria["promedio_latencia_ms"] > 0

        assert "modelo_principal" in telemetria
        assert isinstance(telemetria["modelo_principal"], str)

        assert "disponibilidad_servicio_pct" in telemetria
        assert telemetria["disponibilidad_servicio_pct"] >= 95.0

        assert "total_estudios_procesados" in telemetria
        assert isinstance(telemetria["total_estudios_procesados"], int)

        assert "distribucion_modelos" in telemetria
        assert isinstance(telemetria["distribucion_modelos"], dict)
        print(f"  [PASS] Métrica telemetría_ia agregada: {telemetria['promedio_latencia_ms']} ms, {telemetria['modelo_principal']}, Uptime: {telemetria['disponibilidad_servicio_pct']}%.")
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" SUITE DE PRUEBAS UNITARIAS: TELEMETRÍA E INFERENCIA CLÍNICA (FASE 4)")
    print("=" * 70)
    test_pydantic_schemas_telemetry()
    test_database_telemetry_persistence()
    test_coordinator_analytics_telemetry_metrics()
    print("=" * 70)
    print(" TODAS LAS PRUEBAS DE TELEMETRÍA PASARON EXITOSAMENTE (100% PASS)\n")
