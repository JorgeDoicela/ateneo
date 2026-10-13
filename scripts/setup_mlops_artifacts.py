#!/usr/bin/env python3
"""
Ateneo+ — Script Automatizado de Aprovisionamiento de Artefactos MLOps.
Descomprime, sanitiza metadatos y certifica ChromaDB v2 y el modelo fino BGE-M3
para despliegues inmediatos en nuevas máquinas y servidores.

Uso:
  python scripts/setup_mlops_artifacts.py [DIRECTORIO_DESCARGAS_O_ARTEFACTOS]

Ejemplo:
  python scripts/setup_mlops_artifacts.py /home/jorge/Descargas
"""

import os
import sys
import tarfile
import zipfile
import sqlite3
import json
import argparse
from pathlib import Path

# Resolver raíz del repositorio
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DATA_DIR = ROOT_DIR / "backend" / "data"
MODELS_DIR = BACKEND_DATA_DIR / "models"
CHROMA_DIR = BACKEND_DATA_DIR / "chroma_db_v2"


def sanitize_model_configs(model_dir: Path) -> None:
    """Normaliza los archivos JSON del modelo fine-tuned para sentence-transformers estándar."""
    print("-> Sanitizando metadatos de configuración del modelo...")

    # 1. modules.json
    modules_file = model_dir / "modules.json"
    if modules_file.exists():
        with open(modules_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            t = item.get("type", "")
            if "Transformer" in t:
                item["type"] = "sentence_transformers.models.Transformer"
            elif "Pooling" in t:
                item["type"] = "sentence_transformers.models.Pooling"
            elif "Normalize" in t:
                item["type"] = "sentence_transformers.models.Normalize"
        with open(modules_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("   [OK] modules.json normalizado a sentence_transformers.models.*")

    # 2. sentence_bert_config.json
    sbert_config = model_dir / "sentence_bert_config.json"
    if sbert_config.exists():
        with open(sbert_config, "r", encoding="utf-8") as f:
            data = json.load(f)
        clean_data = {
            "max_seq_length": data.get("max_seq_length", 8192),
            "do_lower_case": data.get("do_lower_case", False)
        }
        with open(sbert_config, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2)
        print("   [OK] sentence_bert_config.json normalizado")

    # 3. 1_Pooling/config.json
    pooling_config = model_dir / "1_Pooling" / "config.json"
    if pooling_config.exists():
        with open(pooling_config, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "embedding_dimension" in data:
            data["word_embedding_dimension"] = data.pop("embedding_dimension")
        with open(pooling_config, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("   [OK] 1_Pooling/config.json normalizado (word_embedding_dimension)")


def rebuild_chroma_fts5(chroma_db_dir: Path) -> bool:
    """Reconstruye el índice invertido FTS5 de ChromaDB SQLite y valida integridad."""
    sqlite_file = chroma_db_dir / "chroma.sqlite3"
    if not sqlite_file.exists():
        print(f"   [ERROR] No se encontró {sqlite_file}")
        return False

    print("-> Verificando y reconstruyendo índice FTS5 en ChromaDB...")
    conn = sqlite3.connect(str(sqlite_file))
    cur = conn.cursor()
    cur.execute("INSERT INTO embedding_fulltext_search(embedding_fulltext_search) VALUES('rebuild');")
    conn.commit()
    cur.execute("PRAGMA integrity_check;")
    result = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM embeddings;")
    embeddings_count = cur.fetchone()[0]
    conn.close()

    if result == "ok":
        print(f"   [OK] SQLite PRAGMA integrity_check: {result}")
        print(f"   [OK] Total de embeddings en ChromaDB: {embeddings_count}")
        return True
    else:
        print(f"   [WARN] SQLite integridad: {result}")
        return False


def setup_artifacts(source_path: Path) -> bool:
    print("=" * 70)
    print(" ATENEO+ — APROVISIONAMIENTO AUTOMÁTICO DE ARTEFACTOS MLOps")
    print("=" * 70)
    print(f"Directorio de origen: {source_path}")
    print(f"Destino de datos:     {BACKEND_DATA_DIR}\n")

    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)

    # 1. Buscar archivos fuente
    tar_model = None
    zip_chroma = None

    if source_path.is_file():
        if "bge-m3" in source_path.name and source_path.name.endswith(".tar.gz"):
            tar_model = source_path
        elif "chroma" in source_path.name and source_path.name.endswith(".zip"):
            zip_chroma = source_path
    elif source_path.is_dir():
        for f in source_path.glob("*"):
            if "bge-m3" in f.name and f.name.endswith(".tar.gz"):
                tar_model = f
            elif "chroma" in f.name and f.name.endswith(".zip"):
                zip_chroma = f

    # 2. Descomprimir Modelo
    target_model_dir = MODELS_DIR / "ateneo-bge-m3-ecuador-v2"
    if tar_model and tar_model.exists():
        print(f"-> Descomprimiendo modelo desde {tar_model.name}...")
        with tarfile.open(tar_model, "r:gz") as tar:
            tar.extractall(path=BACKEND_DATA_DIR)
        print("   [OK] Modelo descomprimido con éxito.")
    elif target_model_dir.exists():
        print("-> Directorio de modelo ya existe. Procediendo a sanitización...")
    else:
        print("-> [INFO] No se encontró archivo .tar.gz de modelo para descomprimir.")

    if target_model_dir.exists():
        sanitize_model_configs(target_model_dir)

    # 3. Descomprimir ChromaDB
    if zip_chroma and zip_chroma.exists():
        print(f"\n-> Descomprimiendo base vectorial desde {zip_chroma.name}...")
        with zipfile.ZipFile(zip_chroma, "r") as z:
            z.extractall(path=BACKEND_DATA_DIR)
        print("   [OK] ChromaDB v2 descomprimido con éxito.")
    elif (CHROMA_DIR / "chroma.sqlite3").exists():
        print("\n-> ChromaDB ya existe en backend/data/chroma_db_v2.")
    else:
        print("\n-> [INFO] No se encontró archivo .zip de ChromaDB para descomprimir.")

    if (CHROMA_DIR / "chroma.sqlite3").exists():
        rebuild_chroma_fts5(CHROMA_DIR)

    # 4. Asegurar .gitkeep
    gitkeep = CHROMA_DIR / ".gitkeep"
    if not gitkeep.exists():
        with open(gitkeep, "w", encoding="utf-8") as f:
            f.write("# Mantener directorio en git\n")

    print("\n" + "=" * 70)
    print(" APROVISIONAMIENTO COMPLETADO EXITOSAMENTE")
    print(" El proyecto está listo para ejecutar: docker compose up -d")
    print("=" * 70)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aprovisionar artefactos MLOps en Ateneo+")
    parser.add_argument("source", nargs="?", default="", help="Ruta al directorio de descargas o archivo de artefacto")
    args = parser.parse_args()

    search_path = Path(args.source) if args.source else Path.home() / "Descargas"
    if not search_path.exists():
        search_path = Path.home() / "Downloads"
    if not search_path.exists():
        search_path = BACKEND_DATA_DIR

    setup_artifacts(search_path)
