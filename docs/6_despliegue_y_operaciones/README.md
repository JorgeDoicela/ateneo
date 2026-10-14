# Módulo 6: Despliegue y Operaciones — Ateneo+ v1.0.0

Este directorio contiene las guías técnicas, runbooks y procedimientos operativos para el despliegue, configuración de red y puesta en marcha de la plataforma **Ateneo+ (v1.0.0)**.

---

## Índice de Documentos

| Archivo | Descripción | Audiencia |
| :--- | :--- | :--- |
| [`GUIA_APROVISIONAMIENTO_MLOPS_Y_DESPLIEGUE_SERVIDOR.md`](./GUIA_APROVISIONAMIENTO_MLOPS_Y_DESPLIEGUE_SERVIDOR.md) | Procedimiento de aprovisionamiento de artefactos pesados (modelo BGE-M3 y ChromaDB v2), configuración de entorno y despliegue con Docker Compose en servidores y nuevas máquinas. | DevOps / SysAdmin / Investigadores |
| [`DESPLIEGUE_Y_ACCESO_CLOUDFLARE_TUNNEL.md`](./DESPLIEGUE_Y_ACCESO_CLOUDFLARE_TUNNEL.md) | Configuración de túnel cifrado Cloudflare Tunnel para acceso público seguro con SSL/TLS 1.3 sin exposición de puertos perimetrales. | DevOps / Redes |

---

## Procedimiento Rápido de Puesta en Marcha

```bash
# 1. Aprovisionar artefactos descargados
python scripts/setup_mlops_artifacts.py /ruta/a/Descargas

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar contenedores
docker compose up -d --build
```
