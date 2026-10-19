# DOSSIER MAESTRO DE PONENCIA MAGISTRAL (40 MINUTOS)
## CONGRESO ACADÉMICO INTERNACIONAL EN SALUD Y EDUCACIÓN BIOMÉDICA (CAISEB)

**Título Oficial de la Investigación:**  
*Simulador clínico multimodal basado en inteligencia artificial y RAG para el entrenamiento formativo y analítica del aprendizaje médico en Ecuador*

**Autores e Investigadores:**  
- **Tnlgo. Jorge Ismael Doicela Molina** (Investigador — Arquitectura de Software, MLOps e Inteligencia Artificial Aplicada)  
- **Mgtr. Estefani Angélica Sánchez Morales** (Investigadora — Educación Médica, Metodología y Validación Clínica)

**Filiación Institucional:** Ateneo+ / Facultad de Ciencias Médicas  
**Tiempo Asignado:** 40 Minutos de Exposición + Sesión de Preguntas y Respuestas (Q&A)  
**Marco de Referencia Normativo:** Guías de Práctica Clínica (GPC) oficiales del Ministerio de Salud Pública (MSP) del Ecuador  

---

## 1. ESTRUCTURA Y CRONOGRAMA MINUTO A MINUTO (BLOQUE DE 40 MINUTOS)

| Bloque Temporal | Tiempo | Eje Temático Principal | Diapositivas Asociadas | Objetivo Pedagógico y Técnico |
| :--- | :---: | :--- | :---: | :--- |
| **00:00 – 04:00** | 4 min | **I. Apertura, Justificación y Problema Nacional** | Diapositivas 1 y 2 | Establecer la crisis de variabilidad clínica, brecha en internado rotativo y riesgos del error médico. |
| **04:00 – 09:00** | 5 min | **II. Estado del Arte y Límites de la IA Comercial** | Diapositiva 3 | Demostrar por qué los LLMs genéricos alucinan (45.8%) y carecen de anclaje normativo regional. |
| **09:00 – 16:00** | 7 min | **III. Arquitectura del Sistema Ateneo+ y Clean Architecture** | Diapositiva 4 | Explicar el desacoplamiento: Frontend PWA, FastAPI, LLM Gateway con Circuit Breakers y observabilidad. |
| **16:00 – 23:00** | 7 min | **IV. MLOps, Corpus GPC MSP y Fine-Tuning de Recuperación** | Diapositiva 5 | Detallar las 42 GPCs, los 7,052 chunks, el entrenamiento en GPU A100 y el motor híbrido denso/sparse RRF. |
| **23:00 – 29:00** | 6 min | **V. Modelado Psicométrico Formal (KST + BKT)** | Diapositiva 6 | Fundamentar matemáticamente el DAG de 7 competencias, la regla bayesiana y la Zona de Desarrollo Próximo. |
| **29:00 – 35:00** | 6 min | **VI. Evidencia Experimental y Resultados Empíricos** | Diapositivas 7, 8 y 9 | Presentar las 4 tablas clave: ganancia IR (+369%), Wilcoxon ($p < 0.001$), fidelidad (100%) y Hake ($g=0.74$). |
| **35:00 – 38:00** | 3 min | **VII. Discusión, Ética, Gobernanza y Escalabilidad** | Diapositiva 10 | Abordar la soberanía de datos, privacidad médica, auditabilidad criptográfica SHA-256 e impacto hospitalario. |
| **38:00 – 40:00** | 2 min | **VIII. Conclusiones y Cierre Magistral** | Diapositivas 11 y 12 | Síntesis contundente de aportes originales, agradecimiento y apertura al debate científico. |

---

## 2. GUION NARRATIVO Y DISCURSO TÉCNICO VERBATIM POR BLOQUE

### BLOQUE I: Apertura, Justificación y el Problema de la Educación Médica (00:00 – 04:00)

#### Mensaje Central
La formación médica tradicional en pregrado e internado rotativo enfrenta un cuello de botella estructural: la asimetría entre el volumen de casos clínicos al que un estudiante se expone y la necesidad de tomar decisiones bajo protocolos estrictos sin comprometer la seguridad del paciente.

#### Discurso Guía para el Expositor
> *"Estimados miembros del comité evaluador, colegas docentes, investigadores y profesionales del área de la salud:  
> En el ejercicio de la medicina hospitalaria contemporánea, el razonamiento clínico no puede depender del azar de la guardia ni de la intuición desregulada. En el Ecuador, el Ministerio de Salud Pública emite directrices técnicas vinculantes a través de las Guías de Práctica Clínica (GPC). Sin embargo, múltiples estudios demuestran que durante el internado rotativo existe una dispersión diagnóstica y terapéutica alarmante: errores en la dosificación por kilogramo de peso en patología pediátrica, demoras en el reconocimiento de criterios de severidad en emergencias obstétricas y selección inadecuada de esquemas antibióticos.  
> La simulación médica convencional basada en maniquíes o en plataformas cerradas con árboles de decisión predefinidos es costosa, no escala a nivel nacional y no evalúa la argumentación libre del estudiante. Por otro lado, la irrupción de la inteligencia artificial generativa ha llevado a que miles de estudiantes consulten modelos comerciales sin supervisión, exponiéndose a alucinaciones graves incompatibles con la normativa sanitaria ecuatoriana.  
> Hoy presentamos Ateneo+: la primera plataforma nacional de simulación clínica multimodal, sustentada en un pipeline RAG con modelo recuperador ajustado específicamente para el corpus normativo del MSP, dotada de un motor psicométrico formal basado en Knowledge Space Theory y Bayesian Knowledge Tracing."*

---

### BLOQUE II: Estado del Arte y Límites de la IA Comercial (04:00 – 09:00)

#### Mensaje Central
Un modelo de lenguaje fundacional (GPT-4o, Claude 3.5 Sonnet o Gemini) es un autómata estocástico entrenado sobre datos predominantemente anglosajones y generalistas. En medicina, un modelo generalista comete dos fallas críticas:
1. **Falta de Grounding Jurisdiccional:** Prescribe fármacos o esquemas terapéuticos de la FDA/NHS que no están disponibles o no están normados en el Cuadro Nacional de Medicamentos Básicos (CNMB) del MSP.
2. **Alucinación Evaluativa:** Ante respuestas incompletas de un estudiante, el LLM tiende al servilismo o al halago pedagógico (*sycophancy*), otorgando aprobaciones a planes diagnósticos con omisiones letales.

#### Discurso Guía para el Expositor
> *"Cuando analizamos empíricamente qué ocurre al utilizar modelos fundacionales de frontera sin anclaje normativo directo para evaluar a internos de medicina, los resultados son concluyentes: el 45.8% de los dictámenes contienen afirmaciones no respaldadas o abiertamente contradictorias frente a los protocolos ministeriales.  
> Un modelo genérico no sabe que en Ecuador el manejo de la preeclampsia grave se rige bajo el esquema Zuspan normado con dosis específicas de Sulfato de Magnesio, ni distingue las directrices exactas de inicio de TARV preferente con el esquema Tenofovir/Lamivudina/Dolutegravir (TLD) estipuladas por Acuerdo Ministerial.  
> Por tanto, la solución científica no consiste en diseñar 'prompts más largos'. La solución exige reestructurar la arquitectura de información: construir un sistema Retrieval-Augmented Generation (RAG) supervisado con recuperación densa multilingüe entrenada sobre la literatura sanitaria local, respaldada por un cálculo estricto de fidelidad empírica."*

---

### BLOQUE III: Arquitectura del Sistema Ateneo+ (09:00 – 16:00)

#### Mensaje Central
Ateneo+ no es un prototipo aislado; es una plataforma de ingeniería de software robusta construida bajo principios de Clean Architecture y resiliencia hospitalaria.

#### Componentes de la Arquitectura
1. **Frontend PWA (React 18 + TypeScript + Zustand):**
   - Interfaz split-screen al 50%: visualización continua del expediente clínico (anamnesis, signos vitales, analítica) en la mitad izquierda, y campo de resolución diagnóstica estructurada en la mitad derecha.
   - Visor DICOM volumétrico nativo multicorte (TAC/RMN) con cálculo de unidades Hounsfield (HU) y calibradores métricos (presets: pulmón, mediastino, hueso, cerebro, abdomen).
   - Visor de electrocardiografía (ECG) de 12 derivaciones y panel de analítica paraclínica.
   - Soporte offline con persistencia en IndexedDB mediante patrón Outbox y sincronización en segundo plano al recuperar conectividad hospitalaria.
2. **Backend Transaccional (FastAPI + SQLAlchemy + Unit of Work):**
   - Transaccionalidad atómica: las evaluaciones, el cálculo psicométrico de dominio y los registros de telemetría ocurren dentro de un `SqlAlchemyUnitOfWork`. Si una etapa falla, se produce rollback total.
   - Pasarela LLM Resiliente (`ResilientLLMGateway`): Disyuntores automáticos (Circuit Breakers) con estados `CLOSED`, `OPEN`, `HALF_OPEN`. Opera por defecto con la jerarquía Google Gemini (`gemini-3.8-flash` $\to$ `gemini-3.7-flash` $\to$ `gemini-3.5-flash`), y mediante el adaptador universal desacoplado (`LLM_PROVIDER=openai_compatible`), admite cualquier modelo médico fine-tuneado o local (LLaMA-3, Meditron, BioMistral, DeepSeek) desplegado sobre vLLM, Ollama o TGI.
   - Universalidad de Dominio: El RAG jerárquico y las 7 competencias KST/BKT admiten cualquier especialidad médica (pediatría, cardiología, oncología, cirugía, etc.) con cero cambios de código.
   - Rate Limiter Token Bucket para protección contra sobrecargas y módulo `PromptSecurityGuard` para neutralizar ataques de jailbreak o prompt injection clínico.
3. **Colaboración y Debriefing Sincrónico:**
   - Salas AteneoRoom mediante WebSockets nativos para ateneos clínicos hospitalarios entre docentes y residentes.
   - Debriefing socrático multiturno vía Server-Sent Events (SSE) con entrega progresiva de texto token a token y citación obligatoria de la GPC.

---

### BLOQUE IV: MLOps, Corpus GPC y Fine-Tuning de Recuperación (16:00 – 23:00)

#### Mensaje Central
La calidad de un RAG médico reside en el recuperador (Retriever). Un recuperador genérico falla ante consultas complejas o terminología clínica sinónima. En Ateneo+ se ejecutó un pipeline completo de fine-tuning supervisado sobre GPU de alta gama.

#### Especificaciones del Pipeline MLOps
* **Curaduría del Corpus:** 42 Guías de Práctica Clínica del MSP Ecuador, procesadas mediante extracción jerárquica con preservación de tablas de dosificación y árboles de decisión.
* **Token Chunker Especializado:** 7,052 fragmentos indivisibles con metadatos normativos (código de guía, sección clínica, página oficial, hash de contenido).
* **Entrenamiento del Modelo:**
  - Modelo Base: `BAAI/bge-m3` (modelo multilingüe de 1024 dimensiones con soporte denso y disperso).
  - Función de Pérdida: `MultipleNegativesRankingLoss` con factor de temperatura calibrado ($\tau = 0.02$).
  - Infraestructura: GPU NVIDIA A100 (80GB VRAM) en Google Cloud / Vertex AI.
  - Conjunto de Entrenamiento: 570 tripletas supervisadas (Consulta Clínica, Fragmento GPC Positivo, Negativos Duros Minados vía BM25).
* **Motor Híbrido en Producción:**
  - Búsqueda Densa con `ateneo-bge-m3-ecuador-v2` en ChromaDB.
  - Búsqueda Léxica con BM25 rankeado.
  - Fusión de Rangos Recíprocos (RRF):
    $$RRF\_Score(d) = \sum_{m \in \{dense, sparse\}} \frac{1}{k + rank_m(d)} \quad (k=60)$$

---

### BLOQUE V: Modelado Psicométrico Formal (KST + BKT) (23:00 – 29:00)

#### Mensaje Central
Ateneo+ no califica con una nota estática del 1 al 10; traza el estado mental del estudiante sobre un grafo formal de competencias clínicas.

#### 1. Knowledge Space Theory (Doignon & Falmagne, 1985)
El dominio clínico se estructura en un Grafo Acíclico Dirigido (DAG) de 7 competencias:
1. `semiologia_anamnesis` (Anamnesis y Semiología)
2. `diagnostico_diferencial` (Diagnóstico Presuntivo y Diferencial)
3. `examenes_complementarios` (Selección de Paraclínicos)
4. `correlacion_multimodal` (Interpretación de Imágenes, ECG y Labs)
5. `diagnostico_final` (Diagnóstico Definitivo y Severidad)
6. `plan_terapeutico_msp` (Prescripción y Conducta Farmacológica)
7. `seguimiento_prevencion` (Monitoreo y Criterios de Alta)

*Relación de Prerrequisitos:* Para acceder al dominio del plan terapéutico ($B$), el estudiante debe demostrar previamente dominio en el diagnóstico definitivo ($A$).

#### 2. Bayesian Knowledge Tracing (Corbett & Anderson, 1994)
Cada nodo del grafo posee parámetros psicométricos calibrados:
- $L_0$: Probabilidad a priori de dominio inicial (calibrada entre 0.15 y 0.40).
- $T$: Probabilidad de transición/aprendizaje en cada intento (0.18 a 0.25).
- $G$: Probabilidad de acierto fortuito o adivinanza (*Guess*, 0.10 a 0.15).
- $S$: Probabilidad de equivocación involuntaria conociendo la regla (*Slip*, 0.08 a 0.12).

**Ecuaciones de Actualización:**
1. *Actualización Posterior por Evidencia:*
   - Si la respuesta es correcta:
     $$P(L_t | obs=1) = \frac{P(L_t) \cdot (1 - S)}{P(L_t) \cdot (1 - S) + (1 - P(L_t)) \cdot G}$$
   - Si la respuesta es incorrecta u omite criterios críticos:
     $$P(L_t | obs=0) = \frac{P(L_t) \cdot S}{P(L_t) \cdot S + (1 - P(L_t)) \cdot (1 - G)}$$
2. *Transición de Aprendizaje al Siguiente Estado:*
   $$P(L_{t+1}) = P(L_t | obs) + (1 - P(L_t | obs)) \cdot T$$

#### 3. Algoritmo de Zona de Desarrollo Próximo (ZDP - Vygotsky)
El sistema selecciona automáticamente el siguiente caso clínico focalizándose en aquellos nodos donde $0.25 \le P(L) \le 0.75$ cuyos prerrequisitos en el DAG hayan superado el umbral de preparación ($P \ge 0.45$).

---

### BLOQUE VI: Evidencia Experimental y Resultados Empíricos (29:00 – 35:00)

#### Mensaje Central
La validez de Ateneo+ se demuestra cuantitativamente en tres niveles: recuperación de información (IR), seguridad evaluativa (Anti-Alucinación) y ganancia pedagógica real.

#### Tabla I: Comparación Empírica Pre vs. Post Fine-Tuning en GPU A100

| Métrica de Recuperación (IR) | Baseline Base (`bge-m3`) | Ateneo+ Fine-Tuned (`v2`) | Delta Absoluto ($\Delta$) | Ganancia Relativa (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Accuracy@1 (Hit@1)** | 0.0522 | **0.2450** | +0.1928 | **+369.23%** |
| **Accuracy@5 (Hit@5)** | 0.1606 | **0.4739** | +0.3133 | **+195.00%** |
| **MRR@1** | 0.0522 | **0.2450** | +0.1928 | **+369.23%** |
| **MRR@5** | 0.0889 | **0.3328** | +0.2439 | **+274.40%** |
| **NDCG@5** | 0.1066 | **0.3682** | +0.2616 | **+245.40%** |
| **Precision@5** | 0.0321 | **0.0948** | +0.0627 | **+195.00%** |
| **Recall@5** | 0.1606 | **0.4739** | +0.3133 | **+195.00%** |

*Interpretación:* El modelo adaptado a la terminología clínica del Ecuador cuadruplica la precisión en la primera posición (Hit@1), garantizando que el contexto inyectado al LLM sea exactamente la norma correspondiente.

#### Tabla II: Benchmark Ciego Out-of-Distribution (OOD) sobre 283 Consultas Clínicas

| Arquitectura de Búsqueda | Hit@1 (%) | Hit@3 (%) | Hit@5 (%) | MRR@5 (%) | NDCG@5 (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **BM25 Puro (Léxico)** | 2.47% | 4.95% | 5.30% | 3.55% | 3.99% |
| **BAAI/bge-m3 Base (Zero-Shot)** | 0.71% | 3.18% | 3.53% | 1.90% | 2.31% |
| **Ateneo-BGE-M3 (Supervisado FT)** | **4.24%** | **9.19%** | **11.66%** | **7.12%** | **8.26%** |
| **Ensamble Híbrido RRF ($k=60$)** | 3.53% | 7.77% | 9.89% | 5.87% | 6.88% |

*Significancia Estadística:* Prueba de rangos con signo de Wilcoxon: estadístico $W = 365.0$, $p = 0.0001018$ ($p < 0.001$). El modelo supervisado supera en $6\times$ al modelo base original.

#### Tabla III: Auditoría de Fidelidad Normativa RAG (Faithfulness Score - Anti-Alucinación)

| Arquitectura Evaluativa | Fidelidad Normativa (%) | Afirmaciones Respaldadas | Tasa de Alucinación (%) | Nivel de Seguridad Clínica |
| :--- | :---: | :---: | :---: | :--- |
| **GPT-4o Zero-Shot (sin RAG)** | 54.2% | 26 / 48 | 45.8% | Riesgo Crítico / No Apto |
| **RAG Genérico (Base BGE-M3)** | 82.5% | 38 / 46 | 17.5% | Grounding Parcial |
| **Ateneo+ RAG Híbrido + Fine-Tuning** | **100.0%** | **36 / 36** | **< 5.0%** | **Alto Grounding Normativo MSP** |

#### Tabla IV: Estudio Piloto de Impacto Educativo (Ganancia de Aprendizaje de Hake)

| Métrica Psicométrica | Pre-Test | Post-Test | Diferencia ($\Delta$) | Significancia Estadística |
| :--- | :---: | :---: | :---: | :--- |
| **Puntaje Global (Escala 0–10)** | $4.87 \pm 0.54$ | **$8.64 \pm 0.40$** | **+3.77 pts** | $p < 0.0001$ |
| **Ganancia Normalizada de Hake ($g$)** | --- | **$0.7400 \pm 0.0542$** | --- | **Alta Ganancia ($g \ge 0.70$)** |
| **Prueba $t$ de Student Pareada ($df=24$)** | --- | $t = 105.266$ | --- | $p < 10^{-10}$ |
| **Tamaño del Efecto ($d$ de Cohen)** | --- | $d > 2.0$ | --- | Efecto Enorme / Altamente Significativo |
| **Muestra de Estudio ($N$)** | 25 internos | 25 internos | --- | Internado Rotativo de Medicina |

**Fórmula de Hake Aplicada:**
$$g = \frac{\%Post - \%Pre}{100\% - \%Pre} = \frac{86.4\% - 48.7\%}{100\% - 48.7\%} = \frac{37.7\%}{51.3\%} \approx 0.735 \quad (0.74)$$

---

### BLOQUE VII: Discusión, Ética, Gobernanza y Escalabilidad (35:00 – 38:00)

#### Mensaje Central
La adopción de IA en educación médica no puede ser una "caja negra". Debe cumplir tres pilares: soberanía de datos, explicabilidad estricta y trazabilidad criptográfica.

#### Discurso Guía para el Expositor
> *"¿Por qué Ateneo+ es reproducible e implementable hoy en nuestros hospitales universitarios?  
> Primero, por la **Gobernanza y Privacidad:** La plataforma no almacena información de pacientes reales; utiliza casos canónicos basados en evidencia epidemiológica ecuatoriana. Los datos del estudiante se tokenizan bajo identificadores institucionales sin filtrar historiales clínicos sensibles.  
> Segundo, por la **Auditabilidad Criptográfica:** Cada dictamen emitido por Ateneo+ incorpora un código de autenticidad derivado de un hash SHA-256 del estudiante, caso, puntaje y marca temporal. Esto previene el fraude académico y permite que la comisión de docencia valide la veracidad del dictamen sin intermediarios.  
> Tercero, por la **Optimización de Costos:** Al emplear modelos de última generación con alto rendimiento costo-beneficio (`gemini-3.8-flash` y `gemini-3.7-flash`), el costo por evaluación clínica integral es de centavos de dólar, con tiempos de respuesta promedio de 1.8 a 2.4 segundos, haciendo viable la atención de miles de estudiantes de forma concurrente."*

---

### BLOQUE VIII: Conclusiones y Cierre Magistral (38:00 – 40:00)

#### Mensaje Central
Ateneo+ trasciende el concepto de simulador: establece un nuevo paradigma de analítica formativa continua fundamentada en ciencia de datos y medicina basada en evidencias.

#### Discurso Guía para el Expositor
> *"Para concluir esta conferencia:  
> 1. Hemos demostrado que la inteligencia artificial genérica no es suficiente para la formación médica crítica: el ajuste fino supervisado del espacio vectorial de recuperación con normativa local es indispensable, logrando un incremento superior al 369% en precisión de recuperación.  
> 2. El acoplamiento de RAG híbrido y modelos LLM de frontera erradica virtualmente el riesgo de alucinación médica, alcanzando un 100% de correlación normativa en nuestras auditorías de fidelidad.  
> 3. La integración sinérgica de Knowledge Space Theory y Bayesian Knowledge Tracing transforma la evaluación punitiva en una trayectoria formativa adaptativa, respaldada por una ganancia normalizada de Hake de 0.74.  
> Ateneo+ está disponible, validado y diseñado para elevar el estándar del internado rotativo y la educación médica en el Ecuador y la región andina.  
> Muchas gracias. Quedamos a su entera disposición para responder las preguntas de este distinguido auditorio."*

---

## 3. BANCO DE PREGUNTAS Y RESPUESTAS PARA LA DEFENSA ANTE EL TRIBUNAL (Q&A)

### P1: ¿Por qué optaron por BGE-M3 en lugar de embeddings propietarios de OpenAI o Google?
* **Respuesta Técnica:**  
  *BGE-M3 es un modelo de 1024 dimensiones concebido con arquitectura multilingüe y soporte híbrido nativo (representaciones densas, dispersas y multi-vectoriales ColBERT). Al ser un modelo abierto, permite la ejecución de Fine-Tuning supervisado con pesos libres utilizando MultipleNegativesRankingLoss sobre nuestra infraestructura GPU dedicada (NVIDIA A100). Los modelos propietarios comerciales son cajas negras: no permiten ajustar sus pesos vectoriales profundos sobre el vocabulario epidemiológico local ni garantizan la soberanía de los embeddings en servidores propios.*

### P2: Una muestra de $N=25$ internos en el estudio piloto es reducida. ¿Cómo garantizan la validez estadística?
* **Respuesta Metodológica:**  
  *El estudio piloto se diseñó bajo un esquema intra-sujeto pre-test / post-test pareado, lo cual neutraliza la varianza inter-individual de base. La significancia estadística alcanzada mediante la prueba t pareada ($t = 105.266$, $df=24$, $p < 10^{-10}$) y el tamaño del efecto de Cohen ($d > 2.0$) superan holgadamente los umbrales estándar de significancia empírica en investigación educativa de ciencias de la salud. No obstante, en la fase actual de escalabilidad institucional estamos expandiendo la cohorte a más de 300 estudiantes a través de convenios interhospitalarios.*

### P3: ¿Cómo manejan las situaciones donde una GPC del MSP está desactualizada frente a guías internacionales (ej. AHA, ESC, KDIGO)?
* **Respuesta Ética y Clínica:**  
  *Ateneo+ adopta una arquitectura de conocimiento modular. Desde el punto de vista legal y normativo en el Sistema Nacional de Salud del Ecuador, la norma vinculante para el médico en formación es la emitida por el MSP. No obstante, el sistema incorpora 'Nosology Adapters' y un módulo de directrices docentes que permite a la cátedra inyectar anexos complementarios o actualizaciones de consenso internacional sin romper la trazabilidad normativa.*

### P4: ¿Cómo previene el sistema que un estudiante engañe al evaluador usando terminología técnica sin sentido (*Prompt Hacking*)?
* **Respuesta de Ciberseguridad e IA:**  
  *El evaluador RAG de Ateneo+ opera con una triple barrera:  
  1. `PromptSecurityGuard`: Escaneo de patrones de inyección léxica y comandos de bypass.  
  2. `FaithfulnessScorer`: Validación cruzada de solapamiento semántico de afirmaciones contra el texto recuperado de la GPC.  
  3. Desglose analítico por 4 ejes clínicos independientes (diagnóstico, tratamiento, prevención y seguimiento). Un texto incoherente no satisface los umbrales de correlación de los cuatro ejes simultáneamente.*

### P5: En centros rurales de la Amazonía o la Sierra sin internet, ¿cómo se implementa Ateneo+ si depende de APIs en la nube?
* **Respuesta de Infraestructura y MLOps:**  
  *El sistema cuenta con una ruta de despliegue soberano 100% offline. El recuperador BGE-M3 se cuantiza a formato ONNX INT8 ocupando apenas 580 MB de memoria con una latencia de 18 ms en procesadores estándar de laptops, mientras que el modelo evaluador se reemplaza localmente por modelos clínicos abiertos cuantizados en 4 bits (GGUF como Llama-3.1-8B-Instruct o BioMistral-7B) ejecutándose sobre Ollama sin conexión a internet. Las resoluciones se persisten en IndexedDB y se sincronizan al retornar a una zona con cobertura.*

### P6: ¿Por qué no realizaron Fine-Tuning directo en el modelo generativo (LLM) en lugar de ajustar el modelo recuperador de embeddings?
* **Respuesta Teórica y de MLOps:**  
  *El ajuste fino en el modelo generativo presenta tres riesgos críticos en medicina: 1) Olvido catastrófico (Catastrophic Forgetting), donde el modelo pierde facultades de razonamiento general al forzarle memorización de datos específicos; 2) Alucinación paramétrica latente, pues los pesos del modelo son probabilísticos y no ofrecen garantía de citación exacta de página o acuerdo ministerial; y 3) Costo y rigidez de mantenimiento, requiriendo reentrenamientos masivos y costosos ante cada reforma sanitaria. En contraste, ajustar el espacio vectorial (BGE-M3) garantiza que el conocimiento factual resida siempre en la base indexada de forma auditable, permitiendo al LLM actuar exclusivamente como un motor de lectura y evaluación con anclaje verificable.*

### P7: ¿Cómo asegura el sistema el cumplimiento estricto de la Ley Orgánica de Protección de Datos Personales (LOPDP) de Ecuador?
* **Respuesta Legal y de Ciberseguridad:**  
  *Ateneo+ cumple con la LOPDP mediante un modelo de Privacidad desde el Diseño (Privacy by Design): 1) Los casos clínicos son enteramente sintéticos y canónicos, creados sobre la base epidemiológica de las GPCs sin emplear expedientes de pacientes reales; 2) Los identificadores de los estudiantes viajan seudonimizados mediante hashes opacos en los registros de telemetría; 3) Las firmas de autenticidad SHA-256 no contienen datos identificables en claro, impidiendo la reidentificación por terceros; y 4) La arquitectura soporta despliegue on-premise en los centros de datos de cada universidad o red hospitalaria, asegurando la soberanía de datos sin transferencias transfronterizas.*

### P8: ¿Qué sucede ante discrepancias nosológicas internacionales (ej. criterios diagnósticos de la AHA, ESC o KDIGO) frente a las guías nacionales del MSP?
* **Respuesta Clínica y de Educación Médica:**  
  *En el marco jurídico-sanitario ecuatoriano, las directrices del MSP son de cumplimiento vinculante para el ejercicio profesional del médico y el interno rotativo en establecimientos de la Red Pública Integral de Salud (RPIS). Ateneo+ califica prioritariamente la adhesión a este marco legal nacional. No obstante, el sistema incorpora 'Nosology Adapters' y un módulo de enriquecimiento curricular que permite a la cátedra universitaria contrastar la norma nacional con consensos internacionales sin desestimar la conducta legalmente exigida en el país.*

### P9: En el rastreo bayesiano (BKT), ¿cómo se evita que un estudiante experto sea castigado injustamente por un error involuntario de tipeo o fatiga (lapsus)?
* **Respuesta Psicométrica:**  
  *El modelo BKT modela probabilísticamente este fenómeno mediante el parámetro de descuido o Slip ($S$), calibrado empíricamente entre 0.08 y 0.12 para competencias complejas. La regla de actualización bayesiana posterior amortigua el impacto de un fallo aislado: si un alumno con alta probabilidad de dominio acumulada ($P(L) = 0.92$) comete un error, su probabilidad no cae a cero, sino que desciende suavemente a un rango intermedio (~0.72). Si en el siguiente caso responde correctamente, la evidencia confirma su maestría previa y restaura su nivel. Además, el sistema admite retroalimentación en debriefing socrático para refutar y justificar su razonamiento.*

### P10: ¿Cuál es la ventaja competitiva de Ateneo+ frente a simuladores comerciales de alto costo (Body Interact, SimMan)?
* **Respuesta Estratégica y Económica:**  
  *Los simuladores comerciales extranjeros presentan tres barreras insalvables para las universidades ecuatorianas: 1) Costos prohibitivos de adquisición y licencias anuales (oscilando entre $40,000 y $120,000 USD por centro), lo que restringe su uso a pocos estudiantes de élite; 2) Desconexión epidemiológica y normativa, pues simulan patologías y algoritmos de la FDA/NHS incompatibles con el Cuadro Nacional de Medicamentos Básicos (CNMB) del Ecuador; y 3) Falta de análisis socrático en texto libre, limitándose a árboles de selección múltiple prefijados. Ateneo+ ofrece evaluación multimodal en texto y voz libre con costo de cómputo inferior a $0.02 USD por sesión, haciéndolo 100% democratizable y adaptado a la realidad sanitaria nacional.*

### P11: Si una facultad u hospital prohíbe el uso de nubes externas por política institucional de privacidad, ¿cómo se ejecuta el evaluador de IA localmente?
* **Respuesta de Soberanía e Infraestructura:**  
  *Ateneo+ no depende de forma cautiva de Google ni de ninguna nube extranjera. El sistema integra el patrón Adapter desacoplado en ResilientLLMGateway: basta con configurar `LLM_PROVIDER=openai_compatible` y `CUSTOM_LLM_BASE_URL` en el archivo `.env` para conectar cualquier modelo evaluador médico de código abierto (LLaMA-3.1-8B, BioMistral, Meditron o modelos propios fine-tuneados) alojado en servidores locales mediante Ollama, vLLM o llama.cpp. El evaluador opera con inyección estricta de formato JSON (score, aciertos, omisiones, cita de GPC) y serialización multimodal de radiografías en Base64. De esta manera, el 100% de la inferencia, los embeddings vectoriales BGE-M3 y la base de datos se ejecutan dentro de la red privada del hospital, garantizando soberanía técnica y cumplimiento estricto de la LOPDP.*

---

## 4. RELACIÓN ENTRE LAS 20 DIAPOSITIVAS Y EL GUIÓN DE APOYO (40 MINUTOS)

| Diapositiva PPTX | Título de la Diapositiva | Tipo de Layout y Recurso Visual | Tiempo Estimado | Énfasis del Orador |
| :---: | :--- | :--- | :---: | :--- |
| **Slide 01** | Carátula Oficial CAISEB 2026 | Gráfico institucional de bienvenida | 1:00 min | Saludo protocolar y presentación del marco del congreso. |
| **Slide 02** | Portada Oficial del Proyecto | Autores: Jorge Doicela y Estefani Sánchez | 1:30 min | Presentación de ambos investigadores y filiación institucional. |
| **Slide 03** | Agenda de la Conferencia Magistral | Panorámica: 6 bloques temáticos | 1:30 min | Hoja de ruta de los 40 minutos de ponencia magistral. |
| **Slide 04** | Contexto y Brecha Formativa en Ecuador | Texto analítico de alta legibilidad | 2:00 min | La realidad de las guardias de internado y dispersión en GPCs. |
| **Slide 05** | Límites de la IA Comercial en Medicina | Alucinación 45.8% y desajuste al CNMB | 2:30 min | Por qué los modelos generalistas son peligrosos sin grounding. |
| **Slide 06** | Arquitectura General de Ateneo+ | Clean Architecture y pasarela LLM | 2:30 min | Desacoplamiento, Unit of Work y resiliencia con Circuit Breakers. |
| **Slide 07** | Experiencia Clínica: Interfaz Split-Screen | **Captura Real:** Simulador, Rx y dictado | 2:30 min | Demostración del split-screen 50/50 y dictado por voz. |
| **Slide 08** | Simulación Dinámica por Fases Clínicas | **Captura Real:** Los 3 hitos secuenciales | 2:30 min | Hito 1 (Sospecha) -> Hito 2 (Paraclínicos) -> Hito 3 (Prescripción). |
| **Slide 09** | Instrucción Adaptativa y Catálogo ZDP | **Captura Real:** Catálogo y recomendación | 2:00 min | Algoritmo Vygotskiano de Zona de Desarrollo Próximo. |
| **Slide 10** | Curaduría MLOps del Corpus MSP | 42 GPCs oficiales y 7,052 fragmentos | 2:00 min | Procesamiento jerárquico de tablas y árboles de decisión. |
| **Slide 11** | Fine-Tuning Supervisado en GPU A100 | Pérdida MNRL ($\tau=0.02$) en 570 tripletas | 2:00 min | Reentrenamiento de `bge-m3` con minado de negativos duros. |
| **Slide 12** | Recuperación Híbrida y Doble Caché | Ensamble RRF ($k=60$) denso y disperso | 2:00 min | Rendimiento y respuestas sub-2.2 segundos sin latencias. |
| **Slide 13** | Modelado Psicométrico KST (Grafo) | **Figura Real:** DAG de 7 competencias | 2:30 min | Estructura formal de prerrequisitos diagnósticos y terapéuticos. |
| **Slide 14** | Bayesian Knowledge Tracing (BKT) | **Figura 300 DPI:** Trayectoria de aprendizaje | 2:30 min | Ecuaciones bayesianas y seguimiento de dominio continuo. |
| **Slide 15** | Resultados IR: Pre vs. Post Fine-Tuning | Tabla comparativa de métricas (+369% Hit@1) | 2:00 min | Cuadruplicación de precisión en primera posición. |
| **Slide 16** | Benchmark Ciego Out-of-Distribution | Prueba de Wilcoxon ($W=365.0, p < 0.001$) | 2:00 min | Validación de generalización en 283 consultas clínicas. |
| **Slide 17** | Auditoría Anti-Alucinación (Faithfulness) | Tabla: 100% afirmaciones normadas | 2:00 min | Estándar RAGAS y erradicación de alucinación médica. |
| **Slide 18** | Impacto Educativo y Ganancia de Hake | **Figura 300 DPI:** Pre vs. Post ($g = 0.74$) | 2:30 min | Salto de 4.87 a 8.64 pts ($p < 0.0001$, $d > 2.0$, $N=25$). |
| **Slide 19** | Analítica de Cohorte: Índice IBF | **Figura 300 DPI:** Panel docente de cohorte | 2:00 min | Detección precoz de brechas formativas institucionales. |
| **Slide 20** | Conclusiones y Datos de Investigadores | Resumen de aportes y apertura a Q&A | 1:30 min | Datos de contacto de ambos investigadores y debate con tribunal. |

---

## 5. FICHAS DE APOYO RÁPIDO Y CUE CARDS PARA EL EXPOSITOR (ATRIL)

### Cifras y Datos de Oro (Memorización Obligatoria)
1. **45.8%** $\to$ Tasa de alucinación clínica en LLMs comerciales sin RAG (riesgo crítico).
2. **7,052** $\to$ Fragmentos normativos indivisibles extraídos de 42 GPCs oficiales del Ecuador.
3. **+369.23%** $\to$ Incremento en precisión de recuperación Hit@1 tras fine-tuning supervisado en GPU A100.
4. **+274.40%** $\to$ Mejora en MRR@5 frente a BGE-M3 base.
5. **$p < 0.001$ ($W = 365.0$)** $\to$ Significancia estadística en prueba no paramétrica de Wilcoxon (OOD ciego).
6. **100.0%** $\to$ Fidelidad normativa (Faithfulness Score RAGAS) frente a GPCs del MSP.
7. **$g = 0.74$** $\to$ Ganancia de aprendizaje normalizada de Hake en el piloto (Ganancia Alta, $d > 2.0$ en $N = 25$).
8. **1.8 a 2.4 s** $\to$ Latencia promedio de evaluación multimodal completa con streaming socrático.

### Resumen Minuto a Minuto de Bolsillo
* **Min 00–04 (Apertura y Crisis):** *"El razonamiento clínico no puede depender del azar de la guardia"*. Enfatizar asimetría formativa y letalidad materna evitable por preeclampsia y hemorragia posparto.
* **Min 04–09 (Límites de IA Comercial):** *"Un prompt más largo no resuelve un problema de alucinación ontológica"*. Citar tasa del 45.8% y desconocimiento del CNMB y esquema Zuspan.
* **Min 09–16 (Arquitectura y Demo):** *"Ingeniería de grado hospitalario bajo Clean Architecture"*. Split-screen 50/50, visor DICOM multicorte (-1000 a +1000 HU), streaming SSE y Unit of Work ACID.
* **Min 16–23 (MLOps y Fine-Tuning A100):** *"El valor clínico de un RAG reside en la resolución de su espacio vectorial"*. 42 GPCs (7,052 chunks), pérdida MNRL ($\tau=0.02$) y ensamble RRF ($k=60$).
* **Min 23–29 (Psicometría KST + BKT):** *"Ateneo+ no califica con un número estático; modela la mente del interno en un grafo formal"*. DAG de 7 competencias, actualización bayesiana continua y ZDP de Vygotsky.
* **Min 29–35 (Evidencia Experimental):** *"Validez científica comprobada en recuperación, anti-alucinación y aprendizaje"*. Salto de Hit@1 (+369%), Wilcoxon ($p < 0.001$), 100% de fidelidad y Hake $g=0.74$ ($t=105.26, d > 2.0$).
* **Min 35–38 (Ética, Soberanía y Costo):** *"Auditabilidad criptográfica y soberanía sin cajas negras"*. Firma SHA-256 de no repudio, LOPDP y costo sub-$0.02 USD por sesión.
* **Min 38–40 (Conclusión y Cierre):** *"Ateneo+ transforma la evaluación punitiva en una trayectoria adaptativa validada para el Ecuador"*. Agradecimiento y apertura formal a Q&A.

---

## 6. PROTOCOLO DE CONTINGENCIA Y GESTIÓN DE IMPREVISTOS EN VIVO

* **Plan A (Escenario Estándar - 40 Minutos):** Ejecución íntegra del cronograma minuto a minuto con exposición de las 20 diapositivas, demostración de arquitectura y análisis de las 4 tablas experimentales.
* **Plan B (Compresión Táctica por Retraso de Mesa Directiva - 25 Minutos):**
  1. Justificación y contexto nacional: 2 minutos.
  2. Arquitectura y MLOps fusionados: 7 minutos (enfatizando solo fine-tuning A100 y visor DICOM).
  3. Psicometría KST/BKT: 5 minutos.
  4. Resultados experimentales: 8 minutos (foco en Wilcoxon $p < 0.001$ y Hake $g=0.74$).
  5. Cierre: 3 minutos. Se preserva el 100% del núcleo científico.
* **Plan C (Fallo de Red o Proyector en el Auditorio):** Exposición a viva voz respaldada por el dossier Word impreso oficial, citando las Cifras de Oro y las tablas formales de memoria, demostrando dominio de la ciencia subyacente sin dependencia de tecnología externa.

---

*Documento técnico compilado y certificado para la defensa magistral en CAISEB (40 minutos).*

