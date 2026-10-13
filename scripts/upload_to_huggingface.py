#!/usr/bin/env python3
"""
Ateneo+ — Script Automatizado de Publicación en Hugging Face Hub.

Sube a Hugging Face:
1. El modelo denso BGE-M3 fine-tuned (backend/data/models/ateneo-bge-m3-ecuador-v2) a un Model Repo.
2. La base vectorial ChromaDB v2 (backend/data/chroma_db_v2) empaquetada a un Dataset Repo.

Uso:
  python3 scripts/upload_to_huggingface.py --username TU_USUARIO_HF [--token TU_TOKEN_HF]

Ejemplo:
  python3 scripts/upload_to_huggingface.py --username JorgeDoicela
"""

import os
import sys
import tarfile
import zipfile
import argparse
from pathlib import Path

if Path("/app/data").exists() and (Path("/app/data/chroma_db_v2").exists() or Path("/app/data/models").exists()):
    BACKEND_DATA_DIR = Path("/app/data")
else:
    ROOT_DIR = Path(__file__).resolve().parent.parent
    BACKEND_DATA_DIR = ROOT_DIR / "backend" / "data"

MODEL_DIR = BACKEND_DATA_DIR / "models" / "ateneo-bge-m3-ecuador-v2"
CHROMA_DIR = BACKEND_DATA_DIR / "chroma_db_v2"


def compress_chroma_db(output_zip: Path) -> Path:
    """Comprime ChromaDB v2 en un archivo zip optimizado para publicación."""
    print(f"-> Empaquetando ChromaDB v2 en {output_zip.name}...")
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for file_path in CHROMA_DIR.rglob("*"):
            if file_path.is_file() and not file_path.name.endswith((".db-wal", ".db-shm")):
                arcname = file_path.relative_to(BACKEND_DATA_DIR)
                z.write(file_path, arcname)
    size_mb = output_zip.stat().st_size / (1024 * 1024)
    print(f"   [OK] ChromaDB v2 empaquetado: {size_mb:.2f} MB")
    return output_zip


def upload_artifacts(username: str, token: str = None, upload_model: bool = True, upload_chroma: bool = True):
    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("[ERROR] huggingface_hub no esta instalado. Instalar con: pip install huggingface_hub")
        sys.exit(1)

    hf_token = token or os.getenv("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
    
    api = HfApi(token=hf_token)

    # Validar autenticación
    try:
        user_info = api.whoami()
        authenticated_user = user_info.get("name", username)
        print(f"[OK] Sesión autenticada en Hugging Face como: {authenticated_user}")
    except Exception as e:
        print(f"[ERROR] No se pudo autenticar en Hugging Face: {e}")
        print("Por favor proporcione --token o ejecute 'huggingface-cli login'.")
        sys.exit(1)

    # 1. Subir Modelo Fine-Tuned BGE-M3
    if upload_model:
        if not MODEL_DIR.exists():
            print(f"[ERROR] No se encontró el directorio del modelo en {MODEL_DIR}")
        else:
            model_repo_id = f"{authenticated_user}/ateneo-bge-m3-ecuador-v2"
            print(f"\n=======================================================")
            print(f" 1. SUBIENDO MODELO A HUGGING FACE: {model_repo_id}")
            print(f"=======================================================")
            print(f"Directorio local: {MODEL_DIR}")
            
            api.create_repo(repo_id=model_repo_id, repo_type="model", exist_ok=True, private=False)
            api.upload_folder(
                folder_path=str(MODEL_DIR),
                repo_id=model_repo_id,
                repo_type="model",
                commit_message="feat(model): publicar ateneo-bge-m3-ecuador-v2 fine-tuned en GPC MSP Ecuador"
            )
            print(f"   [OK] Modelo publicado exitosamente: https://huggingface.co/{model_repo_id}")

    # 2. Subir ChromaDB v2
    if upload_chroma:
        if not CHROMA_DIR.exists():
            print(f"[ERROR] No se encontró el directorio de ChromaDB en {CHROMA_DIR}")
        else:
            chroma_repo_id = f"{authenticated_user}/ateneo-chroma-v2"
            print(f"\n=======================================================")
            print(f" 2. SUBIENDO CHROMADB V2 A HUGGING FACE: {chroma_repo_id}")
            print(f"=======================================================")
            
            zip_dest = BACKEND_DATA_DIR / "chroma_db_v2.zip"
            compress_chroma_db(zip_dest)
            
            api.create_repo(repo_id=chroma_repo_id, repo_type="dataset", exist_ok=True, private=False)
            
            # Subir archivo zip empaquetado
            api.upload_file(
                path_or_fileobj=str(zip_dest),
                path_in_repo="chroma_db_v2.zip",
                repo_id=chroma_repo_id,
                repo_type="dataset",
                commit_message="feat(dataset): base vectorial ChromaDB v2 con 7052 fragmentos GPC MSP Ecuador"
            )
            
            # Crear y subir README dataset card
            dataset_readme = f"""---
license: apache-2.0
task_categories:
- question-answering
- information-retrieval
language:
- es
tags:
- clinical
- rag
- ec-msp
- chromadb
size_categories:
- 1K<n<10K
---

# Ateneo+ — Base Vectorial ChromaDB v2 (GPC MSP Ecuador)

Base de datos vectorial persistente SQLite/HNSW con **7,052 fragmentos normativos indivisibles** extraídos de 42 Guías de Práctica Clínica oficiales del Ministerio de Salud Pública del Ecuador.

## Contenido:
- `chroma_db_v2.zip`: Archivo con la colección `gpc_msp_v2` indexada con BGE-M3 y foliación física validada.

## Despliegue en Ateneo+:
```bash
python3 scripts/setup_mlops_artifacts.py --hf-chroma {chroma_repo_id}
```
"""
            api.upload_file(
                path_or_fileobj=dataset_readme.encode("utf-8"),
                path_in_repo="README.md",
                repo_id=chroma_repo_id,
                repo_type="dataset",
                commit_message="docs: agregar dataset card para ChromaDB v2"
            )
            
            print(f"   [OK] ChromaDB v2 publicado exitosamente: https://huggingface.co/{chroma_repo_id}")

    print("\n" + "=" * 70)
    print(" PUBLICACIÓN EN HUGGING FACE HUB COMPLETADA EXITOSAMENTE")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publicar artefactos de Ateneo+ en Hugging Face Hub")
    parser.add_argument("--username", default="JorgeDoicela", help="Nombre de usuario o institución en Hugging Face")
    parser.add_argument("--token", default="", help="Token de acceso con permisos de escritura de Hugging Face")
    parser.add_argument("--skip-model", action="store_true", help="Omitir subida del modelo BGE-M3")
    parser.add_argument("--skip-chroma", action="store_true", help="Omitir subida de ChromaDB v2")
    args = parser.parse_args()

    upload_artifacts(
        username=args.username,
        token=args.token,
        upload_model=not args.skip_model,
        upload_chroma=not args.skip_chroma
    )
