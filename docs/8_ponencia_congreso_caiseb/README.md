# 8. Ponencia Oficial del Congreso CAISEB (40 Minutos)

Este directorio consolida todos los recursos, documentos oficiales, diapositivas y scripts de compilación para la defensa magistral de **Ateneo+** en el **Congreso Académico Internacional de Innovación en Salud, Educación y Bienestar (CAISEB)**.

---

## 1. Identificación de la Investigación

* **Título:** *Simulador clínico multimodal basado en inteligencia artificial y RAG para el entrenamiento formativo y analítica del aprendizaje médico en Ecuador*
* **Autores e Investigadores:**
  - **Tnlgo. Jorge Ismael Doicela Molina** (Investigador — Arquitectura de Software, MLOps e Inteligencia Artificial)
  - **Mgtr. Estefani Angélica Sánchez Morales** (Investigadora — Educación Médica, Metodología y Validación Clínica)
* **Filiación:** Ateneo+
* **Tiempo de Exposición:** 40 minutos + ronda de preguntas (Q&A)

---

## 2. Inventario de Archivos en este Módulo

| Archivo | Formato | Descripción |
| :--- | :---: | :--- |
| **`ATENEO_DOSSIER_TECNICO_Y_PONENCIA_CAISEB.docx`** | DOCX | Documento Word integral y exhaustivo de Ateneo+ (2.56 MB, 21 secciones completas, 10 tablas formales, 8 figuras a 300 DPI y más de 8,000 palabras). Contiene portada institucional con ambos autores como Investigadores (sin distinciones jerárquicas), antecedentes históricos y crisis formativa en Ecuador, cómo ayudar a los estudiantes de medicina e internos rotativos (seguridad psicológica, reducción del error de razonamiento, preparación EHEP/CACES, año de medicatura rural), límites de los LLMs comerciales y tasa de alucinación del 45.8%, teoría profunda de Transformers y embeddings BGE-M3 (auto-atención escalada, dense/sparse/ColBERT MaxSim), pipeline científico de ingesta y extracción con foliación física real en C++, minería de hard negatives en dos etapas con 6 filtros defensivos, fine-tuning supervisado con MNRL (tau=0.02) en GPU NVIDIA A100, motor RRF (k=60), persistencia vectorial ChromaDB v2 HNSW, caché en 2 niveles (0.05 ms), Clean Architecture, guía completa de despliegue de evaluadores locales on-premise (Ollama, vLLM y GGUF) con adaptador OpenAI-Compatible y soberanía de datos LOPDP, módulo de seguridad PromptSecurityGuard, visor DICOM volumétrico multicorte con presets de Hounsfield ACR, dictado por voz, simulación dinámica por fases, debriefing socrático SSE, salas colaborativas AteneoRoom, psicometría KST (DAG de 7 competencias) y BKT bayesiano continuo, algoritmo de recomendación en la Zona de Desarrollo Próximo (ZDP), tablas empíricas de benchmarks IR (+369% Hit@1, +274% MRR@5), prueba OOD de Wilcoxon (p < 0.001), fidelidad normativa del 100%, ganancia de Hake (g=0.74, d > 2.0 en N=25), catálogo canónico de 10 casos clínicos, protocolo formal de reproducibilidad científica y comandos CLI (semillas seed=42, hashes SHA-256, Docker y entorno local), cumplimiento ético LOPDP, firma criptográfica SHA-256, hoja de ruta de escalabilidad (HL7 FHIR, PACS, Federated Learning, cuantización ONNX INT8 / GGUF para centros rurales sin internet, ECOE / OSCE, postgrados médicos y universalidad temática clínica), guion cronometrado de 40 minutos para la ponencia magistral, banco extendido de 11 preguntas y respuestas de alta presión para la defensa ante el tribunal (Q&A con justificación de soberanía local on-premise), fichas de bolsillo y cue cards para el atril con las cifras y datos de oro memorizables, y protocolo formal de contingencia operativa (Planes A, B y C). |
| **`DOSSIER_PONENCIA_MAGISTRAL_CAISEB_40MIN.md`** | Markdown | Guía maestra en texto estructurado: cronograma minuto a minuto, guion narrativo para el orador, fórmulas de BKT/KST/Hake, tablas empíricas y banco de 11 preguntas de defensa (Q&A). |
| **`RULE.md`** | Markdown | Regla de aislamiento estricto para proteger el resto del repositorio. |
| **`scripts/build_full_word_dossier.py`** | Python | Script automatizado en Python (`python-docx`) para compilar y regenerar el documento Word oficial sin dependencias externas complejas. |
| **`scripts/build_caiseb_pptx.py`** | Python | Script automatizado en Python (`python-pptx`) para compilar la presentación oficial panorámica CAISEB.pptx (13 diapositivas exactas). |

---

## 3. Instrucciones de Regeneración y Mantenimiento

Para regenerar o actualizar el documento Word integral:
```powershell
py docs\8_ponencia_congreso_caiseb\scripts\build_full_word_dossier.py
```

---

## 4. Distribución del Tiempo de la Ponencia (40 Minutos)

1. **00:00 – 04:00 (4 min):** Apertura, justificación y problemática nacional en internado rotativo.
2. **04:00 – 09:00 (5 min):** Estado del arte, límites de la IA comercial y tasa de alucinación médica (45.8%).
3. **09:00 – 16:00 (7 min):** Arquitectura de software: Clean Architecture, PWA split-screen, visor DICOM multicorte y debriefing SSE.
4. **16:00 – 23:00 (7 min):** Pipeline MLOps & RAG: 42 GPCs (7,052 chunks), fine-tuning supervisado en GPU A100 y recuperación híbrida RRF ($k=60$).
5. **23:00 – 29:00 (6 min):** Modelado psicométrico: DAG de 7 competencias (KST), actualización bayesiana continua (BKT) y Zona de Desarrollo Próximo (ZDP).
6. **29:00 – 35:00 (6 min):** Resultados experimentales: IR ($+369\%$ Hit@1), Wilcoxon ($p < 0.001$), fidelidad (100%) y ganancia de Hake ($g=0.74$, $d > 2.0$).
7. **35:00 – 38:00 (3 min):** Discusión: Ética, trazabilidad criptográfica SHA-256 y costo de inferencia por evaluación.
8. **38:00 – 40:00 (2 min):** Conclusiones y transición formal a la sesión de Q&A.
