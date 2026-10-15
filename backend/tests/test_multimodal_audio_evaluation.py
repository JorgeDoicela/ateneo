import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))

from main import app
from models.schemas import EvaluationResult, PhaseEvaluationResult, CitaNormativa
from models.clinical_case import get_case_by_id, load_all_cases
from rag.evaluator import evaluate_clinical_reasoning, evaluate_phase_reasoning
from modules.evaluation.service import EvaluationService

client = TestClient(app)

def test_evaluate_clinical_reasoning_with_audio_mock():
    """Valida que evaluate_clinical_reasoning procese partes de audio y propague transcripcion_audio."""
    caso = get_case_by_id("case_preeclampsia_01") or load_all_cases()[0]
    dummy_audio = (b"RIFF....WAVEfmt ....data....", "audio/webm")
    chunk_mock = {
        "texto": "Administrar sulfato de magnesio segun norma MSP.",
        "guia_fuente": "Guía de Trastornos Hipertensivos del Embarazo",
        "seccion": "Tratamiento de Preeclampsia Severa",
        "pagina": 15
    }

    mock_llm_json = """{
        "score": 9.5,
        "score_max": 10,
        "aciertos": ["Diagnóstico certero de preeclampsia con criterios de severidad", "Uso normado de sulfato de magnesio"],
        "omisiones": [],
        "competencias_deficientes": [],
        "cita_normativa": {
            "guia": "Guía de Trastornos Hipertensivos del Embarazo",
            "seccion": "Tratamiento de Preeclampsia Severa",
            "pagina": 15,
            "texto_relevante": "Administrar sulfato de magnesio segun norma MSP."
        },
        "retroalimentacion_general": "Excelente razonamiento verbal.",
        "transcripcion_audio": "Paciente de 32 semanas con PA 165/110 y proteinuria. Inicio impregnación con sulfato de magnesio 4g IV en 20 minutos y maduración pulmonar."
    }"""

    with patch("rag.evaluator.call_gemini_llm", return_value=(mock_llm_json, 120.0, "gemini-3.8-flash")):
        res = evaluate_clinical_reasoning(
            caso=caso,
            respuesta_estudiante="",
            chunk=chunk_mock,
            audio_bytes=dummy_audio
        )

        assert isinstance(res, EvaluationResult)
        assert res.score == 9.5
        assert res.transcripcion_audio is not None
        assert "sulfato de magnesio" in res.transcripcion_audio
        assert len(res.aciertos) == 2


def test_evaluate_phase_reasoning_with_audio_mock():
    """Valida que evaluate_phase_reasoning procese audio multimodal y devuelva PhaseEvaluationResult."""
    caso = get_case_by_id("case_preeclampsia_01") or load_all_cases()[0]
    dummy_audio = (b"DUMMY_AUDIO_PHASE_BYTES", "audio/webm")
    chunk_mock = {
        "texto": "Criterios diagnósticos de severidad según GPC MSP.",
        "guia_fuente": "GPC Preeclampsia",
        "seccion": "Fase 1: Diagnóstico",
        "pagina": 12
    }

    mock_phase_json = """{
        "score": 8.5,
        "score_max": 10,
        "aciertos": ["Identificación oportuna de cefalea y fosfenos"],
        "omisiones": ["Faltó verificar reflejos osteotendinosos"],
        "competencias_deficientes": [],
        "cita_normativa": {
            "guia": "GPC Preeclampsia",
            "seccion": "Fase 1",
            "pagina": 12,
            "texto_relevante": "Criterios diagnósticos de severidad."
        },
        "retroalimentacion_general": "Buen enfoque inicial de anamnesis en fase 1.",
        "transcripcion_audio": "Valoro a la gestante con cefalea holocraneana y cifras tensionales en rango de crisis."
    }"""

    with patch("rag.evaluator.call_gemini_llm", return_value=(mock_phase_json, 95.0, "gemini-3.8-flash")):
        res_fase = evaluate_phase_reasoning(
            caso=caso,
            fase_numero=1,
            respuesta_estudiante="",
            chunk=chunk_mock,
            audio_bytes=dummy_audio
        )

        assert isinstance(res_fase, PhaseEvaluationResult)
        assert res_fase.score_fase == 8.5
        assert res_fase.transcripcion_audio is not None
        assert "cifras tensionales" in res_fase.transcripcion_audio


def test_api_endpoint_evaluate_direct_with_audio_file():
    """Valida la llamada HTTP al endpoint POST /api/evaluate con audio multipart sin texto."""
    caso = get_case_by_id("case_preeclampsia_01") or load_all_cases()[0]
    audio_file_content = b"RIFFfakeaudioforunittestingwebm"

    mock_llm_response = EvaluationResult(
        score=9.0,
        score_max=10,
        aciertos=["Manejo protocolizado según GPC"],
        omisiones=[],
        competencias_deficientes=[],
        cita_normativa=CitaNormativa(
            guia="GPC Trastornos Hipertensivos",
            seccion="Manejo",
            pagina=10,
            texto_relevante="Norma MSP Ecuador"
        ),
        retroalimentacion_general="Dictamen emitido a partir de la nota de voz clínica.",
        transcripcion_audio="Diagnóstico de preeclampsia severa. Indico sulfato de magnesio y monitoreo horario."
    )

    with patch.object(EvaluationService, "evaluate_reasoning", return_value=mock_llm_response):
        response = client.post(
            "/api/evaluate",
            data={
                "case_id": caso.id,
                "respuesta_estudiante": ""
            },
            files={
                "audio_estudiante": ("nota_voz.webm", audio_file_content, "audio/webm")
            }
        )

        assert response.status_code == 200, f"Error en endpoint: {response.text}"
        data = response.json()
        assert data["score"] == 9.0
        assert data["transcripcion_audio"] == "Diagnóstico de preeclampsia severa. Indico sulfato de magnesio y monitoreo horario."
        assert "cita_normativa" in data


def test_api_endpoint_evaluate_phase_with_audio_file():
    """Valida la llamada HTTP al endpoint POST /api/evaluate/phase con audio multipart."""
    caso = get_case_by_id("case_preeclampsia_01") or load_all_cases()[0]
    audio_file_content = b"RIFFfakeaudioforphaseevaluation"

    mock_phase_response = PhaseEvaluationResult(
        fase_numero=1,
        score_fase=8.0,
        aciertos=["Anamnesis completa dirigida"],
        omisiones=[],
        competencias_deficientes=[],
        cita_normativa=CitaNormativa(
            guia="GPC Trastornos Hipertensivos",
            seccion="Anamnesis",
            pagina=8,
            texto_relevante="Norma MSP Ecuador"
        ),
        retroalimentacion_fase="Aprobada fase 1.",
        transcripcion_audio="Interrogo antecedentes familiares y síntomas premonitorios de eclampsia."
    )

    with patch.object(EvaluationService, "evaluate_phase", return_value=mock_phase_response):
        response = client.post(
            "/api/evaluate/phase",
            data={
                "case_id": caso.id,
                "fase_numero": 1,
                "respuesta_estudiante": ""
            },
            files={
                "audio_estudiante": ("nota_fase.webm", audio_file_content, "audio/webm")
            }
        )

        assert response.status_code == 200, f"Error en endpoint: {response.text}"
        data = response.json()
        assert data["score_fase"] == 8.0
        assert "eclampsia" in data["transcripcion_audio"]
