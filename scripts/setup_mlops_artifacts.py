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

# Resolver raíz del repositorio y almacenamiento de datos
if Path("/app/data").exists():
    BACKEND_DATA_DIR = Path("/app/data")
else:
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


def download_file_http(url: str, dest_path: Path, desc: str = "") -> bool:
    """Descarga un archivo con streaming y reporte de progreso sin dependencias externas."""
    import urllib.request
    import time

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Ateneo-MLOps/1.0 (Linux; x86_64)"}
    )

    try:
        with urllib.request.urlopen(req) as resp, open(temp_path, "wb") as f_out:
            total_size = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 2 * 1024 * 1024  # 2 MB
            start_time = time.time()
            last_print = 0

            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f_out.write(chunk)
                downloaded += len(chunk)

                now = time.time()
                if now - last_print >= 1.5 or (total_size > 0 and downloaded == total_size):
                    last_print = now
                    elapsed = now - start_time
                    speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        mb_done = downloaded / (1024 * 1024)
                        mb_tot = total_size / (1024 * 1024)
                        print(f"   [{desc}] {pct:.1f}% ({mb_done:.1f}/{mb_tot:.1f} MB) a {speed:.2f} MB/s", end="\r", flush=True)
                    else:
                        mb_done = downloaded / (1024 * 1024)
                        print(f"   [{desc}] {mb_done:.1f} MB descargados a {speed:.2f} MB/s", end="\r", flush=True)
            print()
        temp_path.replace(dest_path)
        return True
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        print(f"\n   [ERROR] Error descargando {url}: {e}")
        return False


def download_from_hf(repo_id: str, target_dir: Path, repo_type: str = "model") -> bool:
    """Descarga automáticamente artefactos de Hugging Face Hub (usando huggingface_hub o HTTP directo)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import snapshot_download
        print(f"-> Descargando {repo_id} ({repo_type}) desde Hugging Face Hub...")
        snapshot_download(
            repo_id=repo_id,
            repo_type=repo_type,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False
        )
        print(f"   [OK] Descarga completada en {target_dir}")
        return True
    except ImportError:
        pass
    except Exception as hf_err:
        print(f"   [WARN] snapshot_download reportó: {hf_err}. Alternando a cliente HTTP nativo...")

    print(f"-> Consultando API de Hugging Face para {repo_type}/{repo_id}...")
    import urllib.request
    api_type = "models" if repo_type == "model" else "datasets"
    api_url = f"https://huggingface.co/api/{api_type}/{repo_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Ateneo-MLOps/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"   [ERROR] No se pudo consultar la API de Hugging Face ({repo_id}): {e}")
        return False

    siblings = data.get("siblings", [])
    if not siblings:
        print(f"   [ERROR] No se encontraron archivos en el repositorio {repo_id}")
        return False

    url_prefix = f"https://huggingface.co/datasets/{repo_id}/resolve/main" if repo_type == "dataset" else f"https://huggingface.co/{repo_id}/resolve/main"

    print(f"-> Descargando {len(siblings)} archivo(s) desde {repo_id} hacia {target_dir.name}...")
    for s in siblings:
        rfilename = s.get("rfilename")
        if not rfilename or rfilename.startswith(".git"):
            continue
        dest_file = target_dir / rfilename
        if dest_file.exists():
            print(f"   [SKIP] {rfilename} ya existe localmente.")
            continue
        file_url = f"{url_prefix}/{rfilename}"
        ok = download_file_http(file_url, dest_file, desc=rfilename)
        if not ok:
            return False
    return True


def extract_chroma_zip(zip_file: Path, backend_data_dir: Path, chroma_dir: Path) -> bool:
    """Descomprime el zip de ChromaDB detectando automáticamente la raíz."""
    print(f"\n-> Descomprimiendo {zip_file.name}...")
    with zipfile.ZipFile(zip_file, "r") as z:
        names = z.namelist()
        has_folder_prefix = any(n.startswith("chroma_db_v2/") for n in names)
        if has_folder_prefix:
            z.extractall(path=backend_data_dir)
        else:
            chroma_dir.mkdir(parents=True, exist_ok=True)
            z.extractall(path=chroma_dir)
    print("   [OK] ChromaDB v2 descomprimido con éxito.")
    return True


def setup_artifacts(source_path: Path, hf_model: str = "", hf_chroma: str = "", force: bool = False) -> bool:
    print("=" * 70)
    print(" ATENEO+ — APROVISIONAMIENTO AUTOMÁTICO DE ARTEFACTOS MLOps")
    print("=" * 70)
    if hf_model:
        print(f"Modelo Hugging Face:    {hf_model}")
    if hf_chroma:
        print(f"ChromaDB Hugging Face:  {hf_chroma}")
    print(f"Directorio de origen:   {source_path}")
    print(f"Destino de datos:       {BACKEND_DATA_DIR}\n")

    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)

    target_model_dir = MODELS_DIR / "ateneo-bge-m3-ecuador-v2"

    # 1. Modelo: Hugging Face o Archivo Local
    if target_model_dir.exists() and (target_model_dir / "model.safetensors").exists() and not force:
        print("-> Modelo BGE-M3 ya existe localmente. Omitiendo descarga...")
    elif hf_model:
        download_from_hf(hf_model, target_model_dir, repo_type="model")
    else:
        tar_model = None
        if source_path.is_file() and "bge-m3" in source_path.name and source_path.name.endswith(".tar.gz"):
            tar_model = source_path
        elif source_path.is_dir():
            for f in source_path.glob("*"):
                if "bge-m3" in f.name and f.name.endswith(".tar.gz"):
                    tar_model = f
                    break

        if tar_model and tar_model.exists():
            print(f"-> Descomprimiendo modelo desde {tar_model.name}...")
            with tarfile.open(tar_model, "r:gz") as tar:
                tar.extractall(path=BACKEND_DATA_DIR)
            print("   [OK] Modelo descomprimido con éxito.")
        elif target_model_dir.exists():
            print("-> Directorio de modelo ya existe. Procediendo a sanitización...")
        else:
            print("-> [INFO] No se encontró modelo local ni especificación Hugging Face.")

    if target_model_dir.exists():
        sanitize_model_configs(target_model_dir)

    # 2. ChromaDB: Hugging Face o Archivo Local
    if (CHROMA_DIR / "chroma.sqlite3").exists() and not force:
        print("-> ChromaDB v2 ya existe localmente. Omitiendo descarga...")
    elif hf_chroma:
        download_target = BACKEND_DATA_DIR / "hf_chroma_tmp"
        if download_from_hf(hf_chroma, download_target, repo_type="dataset"):
            found_zip = list(download_target.glob("*.zip"))
            if found_zip:
                for zf in found_zip:
                    extract_chroma_zip(zf, BACKEND_DATA_DIR, CHROMA_DIR)
            elif (download_target / "chroma.sqlite3").exists():
                import shutil
                for item in download_target.iterdir():
                    shutil.move(str(item), str(CHROMA_DIR / item.name))
            # Limpiar temporal
            import shutil
            shutil.rmtree(download_target, ignore_errors=True)
    else:
        zip_chroma = None
        if source_path.is_file() and "chroma" in source_path.name and source_path.name.endswith(".zip"):
            zip_chroma = source_path
        elif source_path.is_dir():
            for f in source_path.glob("*"):
                if "chroma" in f.name and f.name.endswith(".zip"):
                    zip_chroma = f
                    break

        if zip_chroma and zip_chroma.exists():
            extract_chroma_zip(zip_chroma, BACKEND_DATA_DIR, CHROMA_DIR)
        elif (CHROMA_DIR / "chroma.sqlite3").exists():
            print("\n-> ChromaDB ya existe en backend/data/chroma_db_v2.")
        else:
            print("\n-> [INFO] No se encontró archivo .zip de ChromaDB para descomprimir.")

    if (CHROMA_DIR / "chroma.sqlite3").exists():
        rebuild_chroma_fts5(CHROMA_DIR)

    # 3. Asegurar .gitkeep
    gitkeep = CHROMA_DIR / ".gitkeep"
    if not gitkeep.exists():
        with open(gitkeep, "w", encoding="utf-8") as f:
            f.write("# Mantener directorio en git\n")

    print("\n" + "=" * 70)
    print(" APROVISIONAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aprovisionar artefactos MLOps en Ateneo+")
    parser.add_argument("source", nargs="?", default="", help="Ruta al directorio de descargas o archivo de artefacto")
    parser.add_argument("--hf-model", default="doiceladev/ateneo-bge-m3-ecuador-v2", help="Repo ID de Hugging Face para el modelo")
    parser.add_argument("--hf-chroma", default="doiceladev/ateneo-chroma-v2", help="Repo ID de Hugging Face para la base ChromaDB v2")
    parser.add_argument("--force", action="store_true", help="Forzar re-descarga aunque los archivos existan")
    args = parser.parse_args()

    search_path = Path(args.source) if args.source else Path.home() / "Descargas"
    if not search_path.exists():
        search_path = Path.home() / "Downloads"
    if not search_path.exists():
        search_path = BACKEND_DATA_DIR

    setup_artifacts(search_path, hf_model=args.hf_model, hf_chroma=args.hf_chroma, force=args.force)


