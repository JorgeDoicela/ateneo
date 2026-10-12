"""
Arnés de Auditoría Científica y Benchmarking RAG - Plataforma Ateneo+
Valida empíricamente la recuperación normativa (BGE-M3 + BM25 + RRF),
la calibración del LLM frente a errores clínicos letales y la convergencia psicométrica (BKT/ZDP).
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Tuple
import requests

# Resolución de rutas en contenedor o entorno local
sys.path.insert(0, "/app")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.retriever import retrieve_relevant_chunk

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")


def run_experiment_1() -> List[Dict[str, Any]]:
    print("=" * 80)
    print("EXPERIMENTO 1: Fidelidad y Precisión de Recuperación del RAG Híbrido (BGE-M3 + BM25)")
    print("=" * 80)
    consultas: List[Tuple[str, str, int]] = [
        ("Esquema Zuspan sulfato de magnesio dosis ataque y mantenimiento", "preeclampsia", 40),
        ("Atonia uterina codigo rojo dosis oxitocina misoprostol", "hemorragia_posparto", 27),
        ("Tratamiento tuberculosis sensible fase inicial y consolidacion 2HRZE", "tuberculosis", 56),
    ]

    results = []
    for q, g, pag_esperada in consultas:
        chunk = retrieve_relevant_chunk(query=q, guia_filtro=g)
        if not chunk:
            raise RuntimeError(f"Fallo crítico: No se recuperó fragmento para '{q}' en guía '{g}'")

        res = {
            "query": q,
            "filtro": g,
            "chunk_id": chunk.get("chunk_id"),
            "guia_fuente": chunk.get("guia_fuente"),
            "pagina_real": chunk.get("pagina"),
            "pagina_esperada": pag_esperada,
            "seccion": chunk.get("seccion"),
            "rrf_score": chunk.get("rrf_score"),
            "snippet": (chunk.get("texto") or "")[:350],
        }
        results.append(res)
        print(f"\n[CONSULTA]: {q}")
        print(f"  Chunk ID        : {res['chunk_id']}")
        print(f"  Guía Fuente     : {res['guia_fuente']}")
        print(f"  Página (Real/Esp): {res['pagina_real']} / {res['pagina_esperada']}")
        print(f"  Sección Oficial : {res['seccion']}")
        print(f"  RRF Score       : {res['rrf_score']}")
        print(f"  Extracto Texto  :\n  {res['snippet']}...\n")

    return results


def run_experiment_2() -> Dict[str, Any]:
    print("=" * 80)
    print("EXPERIMENTO 2: Sensibilidad del Evaluador LLM ante Respuestas Clínicas Extremas")
    print("=" * 80)
    respuestas = {
        "A_Correcta": {
            "texto": (
                "Diagnostico de Preeclampsia con Criterios de Severidad. Tratamiento inmediato con Sulfato de Magnesio "
                "esquema Zuspan: impregnacion 4g IV en 20 min y mantenimiento 1g/h en infusion continua. Como antihipertensivo "
                "Nifedipino 10 mg oral cada 20 min."
            ),
            "score_min_esperado": 8.0,
            "score_max_esperado": 10.0,
        },
        "B_Peligrosa": {
            "texto": "Administro 20 gramos de sulfato de magnesio en bolo directo intravenoso sin diluir. No se requiere antihipertensivo.",
            "score_min_esperado": 0.0,
            "score_max_esperado": 4.0,
        },
        "C_Evasiva": {
            "texto": "La paciente tiene dolor de cabeza, le indico paracetamol 500 mg y reposo en sala.",
            "score_min_esperado": 0.0,
            "score_max_esperado": 2.5,
        },
    }

    results = {}
    for tipo, conf in respuestas.items():
        print(f"\n>>> Evaluando Escenario: {tipo}...")
        resp = requests.post(
            f"{API_BASE_URL}/api/evaluate",
            data={"case_id": "case_preeclampsia_01", "respuesta_estudiante": conf["texto"]},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        results[tipo] = data

        score = data.get("score", 0.0)
        assert conf["score_min_esperado"] <= score <= conf["score_max_esperado"], (
            f"Fallo psicométrico en {tipo}: Score {score} fuera del rango [{conf['score_min_esperado']}, {conf['score_max_esperado']}]"
        )

        print(f"  Puntaje Obtenido        : {score}/{data.get('score_max', 10)}")
        print(f"  Faithfulness Score      : {data.get('faithfulness_score')}")
        print(f"  Nivel de Grounding      : {data.get('grounding_level')}")
        print(f"  Aciertos ({len(data.get('aciertos', []))}): {data.get('aciertos')}")
        print(f"  Omisiones ({len(data.get('omisiones', []))}): {data.get('omisiones')}")
        print(f"  Competencias Deficientes: {len(data.get('competencias_deficientes', []))} detectadas")
        cita = data.get("cita_normativa") or {}
        print(f"  Cita Normativa          : {cita.get('guia')} (Pág. {cita.get('pagina')})")
        print(f"  Retroalimentación       :\n  {data.get('retroalimentacion_general', '')[:250]}...\n")

    return results


def run_experiment_3() -> Dict[str, Any]:
    print("=" * 80)
    print("EXPERIMENTO 3: Validación del Faithfulness Score (Control de Alucinaciones)")
    print("=" * 80)
    resp = requests.get(f"{API_BASE_URL}/api/history/faithfulness-benchmark", timeout=120)
    resp.raise_for_status()
    data = resp.json()

    print(f"Resumen del Benchmark Institucional:")
    print(f"  Total Casos Auditados   : {data.get('total_casos_auditados')}")
    print(f"  Faithfulness Promedio   : {data.get('promedio_faithfulness_score')} ({data.get('promedio_fidelidad_porcentaje')}%)")
    print(f"  Nivel Global Anti-Alucin: {data.get('nivel_global')}")
    print("\nDetalle por Caso Clínico:")
    for c in data.get("detalles_por_caso", []):
        print(f"  - [{c.get('case_id')}] Score: {c.get('faithfulness_score')} | Nivel: {c.get('grounding_level')} | Guía: {c.get('guia')}")

    return data


def run_experiment_4() -> Dict[str, Any]:
    print("=" * 80)
    print("EXPERIMENTO 4: Diálogo Socrático Adaptativo con Streaming en Vivo (SSE)")
    print("=" * 80)
    payload = {
        "case_id": "case_preeclampsia_01",
        "omision_clinica": "Uso de antihipertensivos o diuréticos en preeclampsia con criterios de severidad",
        "estudiante_replica": "¿Por qué no se debe usar diuréticos en preeclampsia?",
        "historial": [],
    }

    start_time = time.time()
    first_token_time = None
    streamed_text = ""
    event_count = 0

    with requests.post(
        f"{API_BASE_URL}/api/evaluate/socratic-turn",
        json=payload,
        stream=True,
        timeout=120,
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                content = line[6:]
                if first_token_time is None:
                    first_token_time = time.time() - start_time
                streamed_text += content
                event_count += 1
                print(content, end="", flush=True)

    total_time = time.time() - start_time
    print("\n" + "-" * 40)
    print("Métricas de Rendimiento SSE:")
    print(f"  Latencia primer token (TTFT): {first_token_time:.2f} s")
    print(f"  Duración total streaming     : {total_time:.2f} s")
    print(f"  Chunks transmitidos          : {event_count}")
    print(f"  Longitud del texto formativo : {len(streamed_text)} caracteres")

    return {
        "ttft": first_token_time,
        "total_time": total_time,
        "event_count": event_count,
        "generated_text": streamed_text,
    }


def run_experiment_5() -> Dict[str, Any]:
    print("=" * 80)
    print("EXPERIMENTO 5: Impacto Psicométrico en el Grafo de Aprendizaje (BKT y ZDP)")
    print("=" * 80)
    student_id = "usr_alumno_001"

    # 1. Estado de competencias cognitivas (BKT)
    r_state = requests.get(f"{API_BASE_URL}/api/adaptive/knowledge-state?student_id={student_id}", timeout=60)
    r_state.raise_for_status()
    bkt_data = r_state.json()

    print(f"Estado Cognitivo BKT para {student_id}:")
    competencias = bkt_data.get("knowledge_state", {})
    for comp_id, p_dominio in competencias.items():
        print(f"  - Competencia {comp_id:30s}: Dominio {p_dominio:.4f} ({p_dominio * 100:.1f}%)")

    # 2. Recomendación adaptativa en la Zona de Desarrollo Próximo (ZDP)
    r_next = requests.get(f"{API_BASE_URL}/api/adaptive/next-case?student_id={student_id}", timeout=60)
    r_next.raise_for_status()
    zdp_data = r_next.json()

    caso = zdp_data.get("case", {})
    comp_focal = zdp_data.get("competencia_objetivo", {})
    print(f"\nRecomendación ZDP para Próximo Caso:")
    print(f"  Caso ID Recomendado   : {caso.get('id')}")
    print(f"  Título del Caso       : {caso.get('titulo')}")
    print(f"  Nivel Esperado        : {caso.get('nivel_esperado')}")
    print(f"  Competencia Focal     : {comp_focal.get('nombre')} (p_dominio: {comp_focal.get('p_dominio')})")
    print(f"  Justificación ZDP     : {zdp_data.get('justificacion_pedagogica')}")

    return {"bkt_state": bkt_data, "zdp_next_case": zdp_data}


if __name__ == "__main__":
    audit_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "api_base_url": API_BASE_URL,
        "exp1": run_experiment_1(),
        "exp2": run_experiment_2(),
        "exp3": run_experiment_3(),
        "exp4": run_experiment_4(),
        "exp5": run_experiment_5(),
    }

    dump_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "audit_results_dump.json"))
    with open(dump_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, ensure_ascii=False, indent=2)

    print("\nAuditoría científica finalizada exitosamente.")
    print(f"Resultados consolidados guardados en: {dump_path}")
