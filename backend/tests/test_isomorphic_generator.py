import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pytest
from unittest.mock import MagicMock, patch

from models.schemas import ClinicalCaseSchema
from modules.cases.dependencies import get_case_service
from rag.isomorphic_generator import (
    IsomorphicCaseGenerator,
    IsomorphicCaseResult,
    CURATED_ISOMORPHIC_CASES,
)
from services.llm_gateway import LLMGenerationResult, AllModelsExhaustedException


def test_curated_isomorphic_cases_structure_and_completeness():
    """Valida que el banco curado contenga las 10 patologías canónicas con fidelidad a las GPC del MSP."""
    expected_case_ids = [
        "case_preeclampsia_01",
        "case_hemorragia_01",
        "case_tb_01",
        "case_vih_01",
        "case_hta_01",
        "case_erc_01",
        "case_ehirn_01",
        "case_nac_01",
        "case_sepsis_neonatal_01",
        "case_aborto_01",
    ]

    for cid in expected_case_ids:
        assert cid in CURATED_ISOMORPHIC_CASES, f"El caso base '{cid}' debe contar con variante isomórfica curada."
        entry = CURATED_ISOMORPHIC_CASES[cid]
        assert len(entry["titulo"]) > 5
        assert len(entry["enunciado"]) > 50
        assert len(entry["pregunta"]) > 20
        assert len(entry["guia_asociada"]) > 5
        assert len(entry["competencias_evaluadas"]) > 0
        assert entry["faithfulness_score"] >= 0.95
        assert len(entry["variaciones_isomorficas"]) > 0


def test_generate_isomorphic_case_from_curated_bank():
    """Valida la generación de una variante isomórfica utilizando el catálogo calibrado."""
    case_service = get_case_service()
    base_case = case_service.get_case("case_preeclampsia_01")
    assert base_case is not None

    iso_case = IsomorphicCaseGenerator.generate_isomorphic_case(
        base_case=base_case,
        force_curated_only=True
    )

    assert isinstance(iso_case, IsomorphicCaseResult)
    assert iso_case.base_case_id == "case_preeclampsia_01"
    assert iso_case.id.startswith("iso_case_preeclampsia_01_")
    assert "Sulfato de Magnesio" in iso_case.pregunta or "Zuspan" in iso_case.pregunta
    assert iso_case.faithfulness_score == 1.0
    assert not iso_case.is_generated_by_llm

    # Validar isomorfismo psicométrico
    val = IsomorphicCaseGenerator.validate_case_isomorphism(base_case, iso_case)
    assert val["is_valid"] is True
    assert val["has_same_guide"] is True
    assert val["is_distinct_prompt"] is True
    assert val["competency_overlap_ratio"] >= 0.5


def test_generate_post_test_battery_from_pre_test_items():
    """Valida la generación de una batería de post-test a partir de los reactivos evaluados en el pre-test."""
    mock_items = [
        {
            "case_id": "case_preeclampsia_01",
            "score": 4.5,
            "omisiones": ["Omisión de esquema Zuspan para preeclampsia"]
        },
        {
            "case_id": "case_hemorragia_01",
            "score": 6.0,
            "omisiones": ["Demora en activación del Código Rojo"]
        },
        {
            "case_id": "case_nac_01",
            "score": 5.0,
            "omisiones": ["Cálculo omitido de CURB-65"]
        }
    ]

    battery = IsomorphicCaseGenerator.generate_post_test_battery(
        assessment_items=mock_items,
        force_curated_only=True
    )

    assert len(battery) == 3
    base_ids = [c.base_case_id for c in battery]
    assert "case_preeclampsia_01" in base_ids
    assert "case_hemorragia_01" in base_ids
    assert "case_nac_01" in base_ids


def test_generate_isomorphic_case_with_llm_success():
    """Valida la generación de variante isomórfica asistida por LLM mediante llm_gateway."""
    case_service = get_case_service()
    base_case = case_service.get_case("case_dengue_01") or case_service.get_case("case_preeclampsia_01")

    mock_llm_response = {
        "titulo": "Gestante con Cefalea Intensa y Sospecha de Trastorno Hipertensivo Severo",
        "enunciado": "Gestante de 36 semanas, 30 años, primigesta. Ingresa con PA 165/110 mmHg, cefalea frontal y epigastralgia.",
        "pregunta": "¿Cuál es la conducta diagnóstica y terapéutica según la GPC del MSP Ecuador?",
        "variaciones_isomorficas": {
            "demografia": "30 años, 36 semanas",
            "sintomas": "Cefalea frontal y epigastralgia"
        },
        "faithfulness_score": 0.96,
        "justificacion_clinica": "Caso equivalente con las mismas competencias de neuroprotección y manejo tensional."
    }

    mock_result = LLMGenerationResult(
        text=json.dumps(mock_llm_response),
        model_used="gemini-2.5-flash",
        fallback_occurred=False,
        attempts=[]
    )

    with patch("rag.isomorphic_generator.GEMINI_API_KEY", "test_key_active"):
        with patch("rag.isomorphic_generator.llm_gateway.generate", return_value=mock_result):
            iso_case = IsomorphicCaseGenerator.generate_isomorphic_case(
                base_case=base_case,
                custom_focus="Foco en neuroprotección",
                force_curated_only=False
            )

            assert iso_case.is_generated_by_llm is True
            assert iso_case.faithfulness_score == 0.96
            assert iso_case.base_case_id == base_case.id
            assert "Gestante con Cefalea Intensa" in iso_case.titulo


def test_generate_isomorphic_case_llm_fallback_on_exhaustion():
    """Valida la resiliencia del generador ante agotamiento de modelos del LLM (Fallback seguro a banco curado)."""
    case_service = get_case_service()
    base_case = case_service.get_case("case_preeclampsia_01")

    with patch("rag.isomorphic_generator.GEMINI_API_KEY", "test_key_active"):
        with patch("rag.isomorphic_generator.llm_gateway.generate", side_effect=AllModelsExhaustedException("Cuota agotada en todos los modelos")):
            iso_case = IsomorphicCaseGenerator.generate_isomorphic_case(
                base_case=base_case,
                force_curated_only=False
            )

            # Debe haber hecho fallback al banco curado transparente y limpio
            assert iso_case is not None
            assert iso_case.base_case_id == "case_preeclampsia_01"
            assert iso_case.is_generated_by_llm is False
            assert iso_case.faithfulness_score == 1.0
