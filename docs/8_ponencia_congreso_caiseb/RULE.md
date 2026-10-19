# Regla Estricta de Aislamiento y No Contaminación (Módulo Temporal CAISEB)

Este directorio es un **módulo temporal y aislado** exclusivo para la preparación y defensa de la ponencia en el congreso CAISEB.

---

## Directivas Obligatorias para el Agente y Desarrolladores

1. **Aislamiento Total (Zero-Spillover):**
   * Queda terminantemente prohibido crear, modificar o mover archivos fuera de este directorio (`docs/8_ponencia_congreso_caiseb/`) para tareas vinculadas a presentaciones, diapositivas, dossiers, reportes o scripts del congreso.
   * La raíz del proyecto (`clinical_rag/`), el directorio `backend/`, el directorio `frontend/` y el directorio `scripts/` principal deben permanecer intactos y limpios de artefactos temporales de exposición.

2. **Naturaleza Temporal y Eliminación Segura:**
   * Todo lo contenido en esta carpeta es autocontenido e independiente. Si en el futuro se decide archivar o eliminar este módulo (`docs/8_ponencia_congreso_caiseb/`), no debe existir ninguna dependencia que afecte el funcionamiento, despliegue o pruebas del simulador Ateneo+.

3. **Ejecución Localizada:**
   * Cualquier script o utilidad adicional requerida para esta ponencia debe residir y ejecutarse exclusivamente dentro de `docs/8_ponencia_congreso_caiseb/scripts/`.
