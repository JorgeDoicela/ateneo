from typing import Dict, Any, List, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from core.logger import get_logger

logger = get_logger("ateneo.telemetry.rum")

router = APIRouter(prefix="/api/telemetry", tags=["Telemetría y Observabilidad RUM"])


class DeviceContextSchema(BaseModel):
    userAgent: Optional[str] = None
    viewportWidth: Optional[int] = None
    viewportHeight: Optional[int] = None
    connectionType: Optional[str] = None
    deviceMemory: Optional[float] = None
    hardwareConcurrency: Optional[int] = None
    online: Optional[bool] = None


class RumPayloadSchema(BaseModel):
    context: Optional[Dict[str, Any]] = None
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    traceId: Optional[str] = None


@router.post("/rum", status_code=status.HTTP_200_OK, summary="Ingesta de métricas RUM de cliente")
async def ingest_rum_telemetry(payload: RumPayloadSchema):
    """
    Ingesta estructurada de telemetría de rendimiento y errores en cliente (RUM).
    Registra Core Web Vitals (LCP, CLS, TTFB) y excepciones de frontend para observabilidad continua.
    """
    metrics_count = len(payload.metrics)
    errors_count = len(payload.errors)

    if errors_count > 0:
        logger.warning(
            f"Telemetría RUM: {errors_count} errores reportados desde cliente.",
            extra={
                "action": "rum_errors_received",
                "trace_id": payload.traceId,
                "error_count": errors_count,
                "errors": payload.errors[:5]
            }
        )
    elif metrics_count > 0:
        logger.info(
            f"Telemetría RUM: {metrics_count} métricas Core Web Vitals recibidas.",
            extra={
                "action": "rum_metrics_received",
                "trace_id": payload.traceId,
                "metrics_count": metrics_count
            }
        )

    return {
        "status": "ok",
        "ingested": True,
        "metrics_recorded": metrics_count,
        "errors_recorded": errors_count
    }
