# Índice Maestro de Documentación Técnica — Ateneo+

Este repositorio de documentación contiene los dosieres metodológicos, especificaciones de arquitectura de software, planes de escalabilidad, protocolos de reproducibilidad científica y manuales de operaciones de la plataforma **Ateneo+** (Simulador Clínico y Evaluación Médica basada en Guías de Práctica Clínica con IA RAG).

---

## 1. Estructura Jerárquica del Repositorio de Documentación

```text
docs/
├── 1_tablas_latex/                          # Tablas académicas formateadas para publicación científica
├── 2_figuras_300dpi/                        # Diagramas vectoriales y figuras de alta resolución
├── 3_documentacion_metodologica/            # Dosieres técnicos, arquitectura y protocolos experimentales
│   ├── ARQUITECTURA_MODULAR_FRONTEND.md     # Feature-Driven Vertical Slices, ViewModels y Estado
│   ├── ARQUITECTURA_MODULAR_MONOLITO_BACKEND.md # FastAPI, Repositorios, Unit of Work y Schemas
│   ├── ARQUITECTURA_RAG_Y_FINE_TUNING.md    # Pipeline RAG híbrido (denso + disperso), BGE-M3 y GPC
│   ├── ARQUITECTURA_RESILIENTE_LLM_Y_CONFIGURACION.md # Circuit breakers, reintentos y fallback defensivo
│   ├── ARQUITECTURA_Y_MODELADO_BASE_DE_DATOS.md # Esquema relacional SQLite, índices y migraciones
│   ├── DOSIER_TECNICO_MARKDOWN_CLINICO_Y_SEGURIDAD_DEEP_LINKING.md # AST Pipeline y Deep-Linking JWT
│   ├── CURRICULO_ADAPTATIVO_KST_Y_LEARNING_ANALYTICS.md # Knowledge Space Theory y modelos bayesianos
│   ├── MANUAL_DE_PRUEBAS_Y_BENCHMARKS.md    # Suites automatizadas de backend y frontend
│   └── METODOLOGIA_Y_REPRODUCIBILIDAD_EXPERIMENTALES.md # Protocolo de investigación y validación
├── 4_pdf_compilado/                         # Documentos y artículos científicos compilados
├── 5_capturas_sistema/                      # Evidencias visuales de la interfaz de usuario
├── 6_despliegue_y_operaciones/              # Infraestructura Docker, túneles y variables de entorno
├── 7_planes_de_escalabilidad_y_hoja_de_ruta/ # Hojas de ruta de evolución técnica
│   └── PLAN_PROFESIONALIZACION_AUTH_Y_TELEMETRIA_DB.md # Especificación de persistencia y telemetría
└── 8_ponencia_congreso_caiseb/               # Dossier técnico Word, teleprompter de discurso y scripts para CAISEB 2026
```

---

## 2. Documentos Metodológicos Principales

### 2.1 Arquitectura e Ingeniería de Software
* [ARQUITECTURA_MODULAR_FRONTEND.md](./3_documentacion_metodologica/ARQUITECTURA_MODULAR_FRONTEND.md): Detalla la partición del cliente React + Vite PWA en módulos de dominio clínico (`cases`, `evaluation`, `collaboration`, `analytics`, `teacher`, `admin`), ViewModels desacoplados mediante custom hooks, y el sistema de diseño clínico normativo (Material 3 Canvas `#f0f4f9`, sin emojis, iconos planos transparentes).
* [ARQUITECTURA_MODULAR_MONOLITO_BACKEND.md](./3_documentacion_metodologica/ARQUITECTURA_MODULAR_MONOLITO_BACKEND.md): Especifica el monolito modular en FastAPI, la inyección de dependencias, repositorios relacionales y el patrón Unit of Work.
* [ARQUITECTURA_Y_MODELADO_BASE_DE_DATOS.md](./3_documentacion_metodologica/ARQUITECTURA_Y_MODELADO_BASE_DE_DATOS.md): Detalla el modelo relacional ACID en `ateneo_clinical.db`, tablas maestras (`users`, `tenants`, `user_sessions`, `evaluation_history`), claves foráneas e integridad referencial.
* [DOSIER_TECNICO_MARKDOWN_CLINICO_Y_SEGURIDAD_DEEP_LINKING.md](./3_documentacion_metodologica/DOSIER_TECNICO_MARKDOWN_CLINICO_Y_SEGURIDAD_DEEP_LINKING.md): Especifica el motor de compilación AST de Markdown clínico (`ClinicalMarkdownRenderer.tsx`), los modos visuales (`standard`, `dense`, `academic`), la preservación de deep-linking con mitigación de Open Redirect (CWE-601), y el ciclo de captura reactiva de errores HTTP 401 en tiempo real.

### 2.2 Inteligencia Artificial y RAG
* [ARQUITECTURA_RAG_Y_FINE_TUNING.md](./3_documentacion_metodologica/ARQUITECTURA_RAG_Y_FINE_TUNING.md): Pipeline de recuperación híbrida, indexación vectorial con ChromaDB v2 y BGE-M3, fine-tuning y evaluación contra Guías de Práctica Clínica del MSP Ecuador.
* [ARQUITECTURA_RESILIENTE_LLM_Y_CONFIGURACION.md](./3_documentacion_metodologica/ARQUITECTURA_RESILIENTE_LLM_Y_CONFIGURACION.md): Estrategia de resiliencia ante contingencias de cuota o caídas de API con conmutación por error (*fallback*) a modelos alternativos.

### 2.3 Analítica del Aprendizaje y Educación Médica
* [CURRICULO_ADAPTATIVO_KST_Y_LEARNING_ANALYTICS.md](./3_documentacion_metodologica/CURRICULO_ADAPTATIVO_KST_Y_LEARNING_ANALYTICS.md): Formalización matemática de la Teoría de Espacios del Conocimiento (*Knowledge Space Theory - KST*) aplicada a la navegación curricular adaptativa de casos clínicos según maestría diagnóstica.
* [DOSIER_POST_TEST_Y_PLAN_ESTUDIOS_HEURISTICO.md](./3_documentacion_metodologica/DOSIER_POST_TEST_Y_PLAN_ESTUDIOS_HEURISTICO.md): Especificación técnica del sistema de Pre-Test / Post-Test con IA y motor heurístico de planes de estudio prescriptivos basados en brechas clínicas GPC y ganancia de Hake.

### 2.4 Ponencia Magistral y Congreso CAISEB 2026
* [ATENEO_DOSSIER_TECNICO_Y_PONENCIA_CAISEB.docx](./8_ponencia_congreso_caiseb/ATENEO_DOSSIER_TECNICO_Y_PONENCIA_CAISEB.docx): Dossier técnico integral de 2.55 MB con la totalidad de la arquitectura, RAG híbrido denso/disperso con 7,052 fragmentos GPC, modelo KST/BKT, salas colaborativas sincrónicas AteneoRoom, ciclo formativo cerrado CACES, carrera formativa médica y catálogo de 10 casos clínicos canónicos con estudios paraclínicos 2D.
* [DISCURSO_PONENCIA_VIRTUAL_CAISEB.docx](./8_ponencia_congreso_caiseb/DISCURSO_PONENCIA_VIRTUAL_CAISEB.docx): Guion y teleprompter para la ponencia virtual de 40 minutos (y Plan B de 15 minutos), con desglose por diapositiva y banco de 16 preguntas de defensa oral ante el tribunal.
* [DOSSIER_PONENCIA_MAGISTRAL_CAISEB_40MIN.md](./8_ponencia_congreso_caiseb/DOSSIER_PONENCIA_MAGISTRAL_CAISEB_40MIN.md): Versión Markdown estructurada del guion y defensa oral.

---

## 3. Estado de Certificación Automatizada

| Batería de Pruebas | Entorno | Casos de Prueba | Resultado |
| :--- | :--- | :---: | :---: |
| **Frontend Unit & Integration** | Vitest 5 + React Testing Library | 156 / 156 | **100% PASS** |
| **Backend Total Suite (Pytest)** | Pytest 9 + FastAPI TestClient | 108 / 108 | **100% PASS** |
| **Seguridad de Autenticación & RBAC** | Pytest (RBAC, JTI, Lockout) | 6 / 6 | **100% PASS** |
| **Verificación de Tipos Estricta** | TypeScript 5 (`tsc --noEmit`) | 0 errores | **100% PASS** |
| **Compilación de Producción PWA** | Vite 6 + Rollup | 0 errores | **100% PASS** |
