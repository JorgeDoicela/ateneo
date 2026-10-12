import json
import sqlite3
from pathlib import Path

def inspect_all():
    print("=== 1. VERIFICACIÓN DE CASOS CANÓNICOS VS PDFS FUENTE ===")
    cases_path = Path("/app/cases_data/cases.json")
    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)["cases"]

    raw_pdfs = Path("/app/data/raw_pdfs")
    all_pdfs = [p.name for p in raw_pdfs.glob("*.pdf")]
    print(f"Total PDFs existentes en /app/data/raw_pdfs: {len(all_pdfs)}")

    missing_pdfs = []
    for c in cases:
        pdf_name = c["guia_asociada"]
        exists = (raw_pdfs / pdf_name).exists()
        print(f"[{c['id']}] Guía: {pdf_name} -> Existe en disco: {exists}")
        if not exists:
            missing_pdfs.append((c['id'], pdf_name))

    print(f"\nPDFs faltantes para los casos del catálogo: {len(missing_pdfs)}")

    print("\n=== 2. VERIFICACIÓN DE FRAGMENTOS Y COLECCIONES CHROMADB ===")
    chroma_v1 = Path("/app/data/chroma_db")
    chroma_v2 = Path("/app/data/chroma_db_v2")
    print(f"Directorio ChromaDB v1 (legacy): existe={chroma_v1.exists()}")
    print(f"Directorio ChromaDB v2 (activo): existe={chroma_v2.exists()}")

    from rag.retriever import get_chroma_client
    client = get_chroma_client()
    collections = client.list_collections()
    col_names = [col.name for col in collections]
    print(f"Colecciones registradas en ChromaDB: {col_names}")
    for name in col_names:
        col = client.get_collection(name)
        print(f" - Colección '{name}': {col.count()} fragmentos indexados")

    print("\n=== 3. VERIFICACIÓN DE EVALUATION_HISTORY EN SQLITE ===")
    conn = sqlite3.connect("/app/data/ateneo_clinical.db")
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM evaluation_history;")
    total_evals = cur.fetchone()[0]
    print(f"Total evaluaciones registradas en historial: {total_evals}")

    cur.execute("SELECT count(*) FROM evaluation_history WHERE fragmento_gpc LIKE '%fallback%' OR cita_normativa LIKE '%fallback%';")
    total_fallbacks = cur.fetchone()[0]
    print(f"Evaluaciones con fallbacks sintéticos en historial: {total_fallbacks}")

if __name__ == "__main__":
    inspect_all()
