# Arquitectura y Modelado de la Base de Datos Relacional (Docs-as-Code)

Este documento especifica el modelo entidad-relación, restricciones relacionales, índices de rendimiento y mecanismos de transaccionalidad ACID implementados en la base de datos de la plataforma Ateneo+.

---

## 1. Justificación y Causa Raíz

Históricamente, la plataforma almacenaba el historial de evaluaciones en un módulo de persistencia directa en SQLite sin control de concurrencia (`history_db.py`), lo que generaba bloqueos de archivo durante evaluaciones simultáneas y carecía de llaves foráneas formales para vincular a los estudiantes con sus métricas psicométricas.

### 1.1 Decisiones Arquitectónicas Implementadas (Bloque 1)
1. **Migración a SQLAlchemy 2.0 con Tipado Estricto:** Toda entidad hereda de `DeclarativeBase` con mapeo explícito mediante `Mapped[]` y `mapped_column()`.
2. **Concurrencia con Write-Ahead Logging (WAL):** Se configuró el motor SQLite para operar con `PRAGMA journal_mode=WAL` y `PRAGMA synchronous=NORMAL`, permitiendo lectores concurrentes sin bloqueo ante escrituras.
3. **Persistencia Agnóstica Hacia PostgreSQL:** La capa de conexión (`backend/core/database.py`) conmuta transparentemente a PostgreSQL si la variable de entorno `DATABASE_URL` está configurada, utilizando pool de conexiones (`pool_size=10`, `max_overflow=20`).
4. **Activación de Llaves Foráneas:** Aplicación obligatoria de `PRAGMA foreign_keys=ON` en cada conexión SQLite mediante el evento `connect` de SQLAlchemy.
5. **Fechas con Zona Horaria UTC:** Todos los campos temporales emplean `DateTime(timezone=True)` con `server_default=func.now()`.

---

## 2. Diagrama Entidad-Relación (Mermaid ERD)

```mermaid
erDiagram
    TENANTS ||--o{ USERS : "alberga"
    TENANTS ||--o{ USER_SESSIONS : "restringe"
    TENANTS ||--o{ CLINICAL_CASES : "publica"
    TENANTS ||--o{ EVALUATION_HISTORY : "agrupa"
    TENANTS ||--o{ ATENEO_ROOMS : "hospeda"
    USERS ||--o{ USER_SESSIONS : "mantiene"
    USERS ||--o{ CLINICAL_CASES : "crea"
    USERS ||--o{ EVALUATION_HISTORY : "rinde"
    USERS ||--o| STUDENT_MASTERY : "consolida"
    USERS ||--o{ STUDENT_LEARNING_SNAPSHOTS : "registra"
    USERS ||--o{ ATENEO_ROOMS : "modera"


    TENANTS {
        string id PK "Identificador único (ej. tenant_default)"
        string codigo UK "Código alfanumérico institucional indexado"
        string nombre_institucional "Nombre oficial de la institución médica"
        string dominio_email "Dominio de correo para asignación automática"
        text gpc_activas_json "Lista de guías ministeriales activas (JSON)"
        boolean activo "Estado de operatividad institucional"
        datetime created_at "Registro de alta en UTC"
        datetime updated_at "Última modificación en UTC"
    }

    USERS {
        string id PK "Identificador único (ej. usr_alumno_001)"
        string email UK "Correo institucional único indexado"
        string nombre "Nombre y apellidos del facultativo"
        string rol "Rol RBAC: alumno, docente, administrador"
        string hashed_password "Hash seguro bcrypt"
        boolean activo "Estado de la cuenta"
        string tenant_id FK "Vínculo con TENANTS (ondelete RESTRICT)"
        datetime last_login_at "Último login exitoso registrado en UTC"
        int login_count "Contador acumulativo de accesos exitosos"
        int failed_login_attempts "Intentos fallidos consecutivos"
        datetime locked_until "Bloqueo temporal defensivo por fuerza bruta"
        boolean email_verified "Verificación de correo institucional"
        datetime created_at "Fecha de registro en UTC"
    }

    USER_SESSIONS {
        string id PK "Claim criptográfico JTI (UUID v4) indexado"
        string user_id FK "Identificador de USERS (ondelete CASCADE)"
        string tenant_id FK "Identificador de TENANTS (ondelete CASCADE)"
        string ip_address "Dirección IP de conexión del cliente"
        string user_agent "User-Agent del navegador o cliente clínico"
        boolean is_revoked "Indicador de lista negra / revocación indexado"
        datetime expires_at "Expiración absoluta del token JWT en UTC"
        datetime created_at "Apertura de la sesión en UTC"
    }

    CLINICAL_CASES {

        string id PK "Identificador del caso (ej. case_preeclampsia_01)"
        string guia_asociada "Guía de Práctica Clínica del MSP vinculada"
        string titulo "Título clínico del caso"
        text enunciado "Viñeta clínica estructurada"
        text pregunta "Interrogante diagnóstica o terapéutica"
        string imagen_url "Ruta de estudio paraclínico asociado"
        string nivel_esperado "Nivel académico (pregrado, internado)"
        string fragmento_gpc_ideal_id "ID del chunk normativo de referencia"
        string modo_simulacion "single_turn o multi_turn"
        json fases "Fases diagnósticas secuenciales (JSON)"
        json competencias_activadas "Competencias del grafo KST asociadas"
        string creado_por FK "Docente creador (ondelete SET NULL)"
        string tenant_id FK "Institución propietaria (ondelete SET NULL)"
        datetime created_at "Fecha de creación en UTC"
        datetime updated_at "Última actualización en UTC"
    }

    EVALUATION_HISTORY {
        int id PK "Autoincremental de resolución"
        string user_id FK "Vínculo con USERS (ondelete CASCADE)"
        string user_email "Correo del estudiante indexado"
        string case_id "Código del caso resuelto"
        string guia_asociada "GPC de referencia utilizada"
        string case_title "Título del caso resuelto"
        float score "Puntaje obtenido (0 a 10)"
        int score_max "Puntaje máximo estándar (10)"
        float faithfulness_score "Fidelidad normativa MSP (0 a 1)"
        string cohorte_id "Identificador de cohorte indexado"
        float tiempo_segundos "Latencia total de resolución"
        string tenant_id FK "Institución del estudiante (ondelete CASCADE)"
        text aciertos_json "Lista de aciertos clínicos detectados (JSON)"
        text omisiones_json "Lista de omisiones o errores letales (JSON)"
        text competencias_json "Deficiencias por eje clínico normativo (JSON)"
        text cita_normativa_json "Cita y foliación oficial de la GPC (JSON)"
        text retroalimentacion_general "Dictamen cualitativo estructurado"
        datetime timestamp "Marca temporal UTC con índice"
    }

    STUDENT_MASTERY {
        string user_id PK_FK "Identificador de USERS (ondelete CASCADE)"
        text state_json "Vector continuo P(L) de las 7 competencias (JSON)"
        datetime updated_at "Última actualización bayesiana"
    }

    STUDENT_LEARNING_SNAPSHOTS {
        int id PK "Autoincremental de trayectoria"
        string user_id FK "Identificador de USERS (ondelete CASCADE)"
        int session_num "Número secuencial de la sesión evaluativa"
        float score_obtained "Calificación obtenida en el intento"
        text state_json "Instantánea del vector P(L) en el momento T"
        datetime timestamp "Marca temporal del snapshot"
    }

    ATENEO_ROOMS {
        string room_code PK "Código alfanumérico único de sala indexado"
        string case_id "Caso clínico en discusión sincrónica"
        string docente_id FK "Docente moderador (ondelete RESTRICT)"
        string docente_nombre "Nombre del docente moderador"
        string estado "Estado de la sala (espera, discusion, cerrada)"
        string tenant_id FK "Institución organizadora (ondelete RESTRICT)"
        text data_json "Participantes, votos y consensos (JSON)"
        datetime created_at "Apertura de la sesión en UTC"
        datetime updated_at "Última actualización de presencia en UTC"
    }
```

---

## 3. Especificación Detallada de Tablas y Restricciones

### 3.1 Tabla `tenants` (Gobernanza Institucional Multi-Tenant)
* **Archivo de Definición:** `backend/modules/auth/models.py`.
* **Propósito:** Raíz de particionado lógico para universidades, hospitales y redes de salud públicas o privadas.

| Columna | Tipo de Dato | Nulo | Restricciones / Índices | Descripción Técnica |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `VARCHAR(50)` | NO | `PRIMARY KEY`, `INDEX` | Identificador institucional (ej. `tenant_default`). |
| `codigo` | `VARCHAR(50)` | NO | `UNIQUE`, `INDEX` | Código nemotécnico institucional (ej. `ateneo_central`). |
| `nombre_institucional` | `VARCHAR(200)` | NO | — | Nombre formal de la facultad u hospital. |
| `dominio_email` | `VARCHAR(100)` | NO | `INDEX` | Dominio de correo para asignación automática institucional. |
| `gpc_activas_json` | `TEXT` | NO | `DEFAULT '[]'` | Guías ministeriales habilitadas para la institución. |
| `activo` | `BOOLEAN` | NO | `DEFAULT TRUE` | Estado operativo del tenant. |
| `created_at` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP` | Alta de la institución en UTC. |
| `updated_at` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP` | Modificación institucional en UTC. |

### 3.2 Tabla `users` (Gestión de Identidades y RBAC)
* **Archivo de Definición:** `backend/modules/auth/models.py`.
* **Propósito:** Almacena usuarios autenticados, credenciales cifradas y roles de acceso vinculados a un tenant.

| Columna | Tipo de Dato | Nulo | Restricciones / Índices | Descripción Técnica |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `VARCHAR(100)` | NO | `PRIMARY KEY`, `INDEX` | Identificador alfanumérico (ej. `usr_alumno_001`). |
| `email` | `VARCHAR(150)` | NO | `UNIQUE`, `INDEX` | Correo electrónico de acceso institucional. |
| `nombre` | `VARCHAR(200)` | NO | — | Nombre y apellidos del usuario. |
| `rol` | `VARCHAR(50)` | NO | — | Rol RBAC: `alumno`, `docente` o `administrador`. |
| `hashed_password` | `VARCHAR(255)` | NO | — | Hash criptográfico generado mediante Bcrypt ($cost=12$). |
| `activo` | `BOOLEAN` | NO | `DEFAULT TRUE` | Indicador de cuenta habilitada. |
| `tenant_id` | `VARCHAR(50)` | NO | `FOREIGN KEY (tenants.id) ON DELETE RESTRICT`, `INDEX` | Sede universitaria u hospitalaria asociada. |
| `last_login_at` | `SafeDateTime` | SÍ | `DEFAULT NULL` | Marca temporal UTC del último acceso exitoso. |
| `login_count` | `INTEGER` | NO | `DEFAULT 0` | Contador acumulativo de inicios de sesión exitosos. |
| `failed_login_attempts` | `INTEGER` | NO | `DEFAULT 0` | Contador de fallos consecutivos para bloqueo defensivo. |
| `locked_until` | `SafeDateTime` | SÍ | `DEFAULT NULL` | Expiración del bloqueo temporal por fuerza bruta (15 min tras 5 fallos). |
| `email_verified` | `BOOLEAN` | NO | `DEFAULT FALSE` | Verificación de correo institucional. |
| `created_at` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP` | Registro de alta en UTC. |

### 3.3 Tabla `user_sessions` (Control de Sesiones Activas y Revocación JTI)
* **Archivo de Definición:** `backend/modules/auth/models.py`.
* **Propósito:** Registro persistente de sesiones activas y lista negra de tokens revocados (Token Blacklist / JTI), mitigando ataques de reutilización y permitiendo cierre de sesión real y auditoría forense de IP/User-Agent.

| Columna | Tipo de Dato | Nulo | Restricciones / Índices | Descripción Técnica |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `VARCHAR(64)` | NO | `PRIMARY KEY`, `INDEX` | Identificador criptográfico único del token JWT (`jti` UUID v4). |
| `user_id` | `VARCHAR(100)` | NO | `FOREIGN KEY (users.id) ON DELETE CASCADE`, `INDEX` | Usuario titular de la sesión. |
| `tenant_id` | `VARCHAR(50)` | NO | `FOREIGN KEY (tenants.id) ON DELETE CASCADE`, `INDEX` | Institución vinculada a la sesión. |
| `ip_address` | `VARCHAR(45)` | SÍ | — | Dirección IP de conexión (IPv4 o IPv6). |
| `user_agent` | `VARCHAR(255)` | SÍ | — | Cadena identificadora del agente de usuario. |
| `is_revoked` | `BOOLEAN` | NO | `DEFAULT FALSE`, `INDEX` | Indicador de revocación activa tras logout o bloqueo. |
| `expires_at` | `SafeDateTime` | NO | — | Expiración programada del JWT en UTC. |
| `created_at` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP` | Apertura de la sesión en UTC. |

### 3.4 Tabla `evaluation_history` (Historial Transaccional Clínico)
* **Archivo de Definición:** `backend/modules/analytics_history/models.py`.

* **Propósito:** Registro inmutable de cada intento de resolución clínica por parte del estudiante con citas normativas y métricas psicométricas.

| Columna | Tipo de Dato | Nulo | Restricciones / Índices | Descripción Técnica |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | NO | `PRIMARY KEY AUTOINCREMENT` | Identificador de intento. |
| `user_id` | `VARCHAR(100)` | NO | `FOREIGN KEY (users.id) ON DELETE CASCADE`, `INDEX` | Identificador del estudiante evaluado. |
| `user_email` | `VARCHAR(150)` | NO | `INDEX` | Correo institucional del estudiante. |
| `case_id` | `VARCHAR(100)` | NO | `INDEX` | Código del caso clínico resuelto. |
| `guia_asociada` | `VARCHAR(150)` | NO | — | Guía de Práctica Clínica de referencia. |
| `case_title` | `VARCHAR(255)` | NO | — | Título del caso clínico evaluado. |
| `score` | `FLOAT` | NO | — | Puntuación obtenida (0.0 a 10.0). |
| `score_max` | `INTEGER` | NO | `DEFAULT 10` | Escala estándar máxima. |
| `faithfulness_score`| `FLOAT` | SÍ | `DEFAULT 0.0` | Medida de fidelidad frente a GPC MSP (0.0 a 1.0). |
| `cohorte_id` | `VARCHAR(50)` | SÍ | `DEFAULT 'general'`, `INDEX` | Identificador de grupo o paralelo académico. |
| `tiempo_segundos` | `FLOAT` | SÍ | `DEFAULT 0.0` | Tiempo de resolución invertido. |
| `llm_latency_ms` | `FLOAT` | SÍ | `DEFAULT 0.0` | Latencia exacta de inferencia en milisegundos (`time.perf_counter`). |
| `llm_model_used` | `VARCHAR(100)` | SÍ | `DEFAULT 'gemini-3.8-flash'` | Modelo LLM empleado en la evaluación diagnóstica. |
| `rag_tokens_used` | `INTEGER` | SÍ | `DEFAULT 0` | Estimación o conteo de tokens consumidos en el contexto RAG. |
| `paraclinical_studies_count` | `INTEGER` | SÍ | `DEFAULT 0` | Cantidad de estudios paraclínicos (DICOM/PDF) integrados en el caso. |
| `tenant_id` | `VARCHAR(50)` | NO | `FOREIGN KEY (tenants.id) ON DELETE CASCADE`, `INDEX` | Discriminador multi-inquilino para analítica B2B. |
| `aciertos_json` | `TEXT` | NO | `DEFAULT '[]'` | Aciertos clínicos estructurados (JSON). |
| `omisiones_json` | `TEXT` | NO | `DEFAULT '[]'` | Omisiones y alertas de letalidad detectadas (JSON). |
| `competencias_json` | `TEXT` | NO | `DEFAULT '[]'` | Deficiencias por competencia clínica (JSON). |
| `cita_normativa_json` | `TEXT` | NO | `DEFAULT '{}'` | Cita de la GPC con página y sección oficial (JSON). |
| `retroalimentacion_general` | `TEXT` | NO | `DEFAULT ''` | Dictamen cualitativo y formativo emitido por IA. |
| `timestamp` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP`, `INDEX` | Marca temporal UTC de la evaluación. |

* **Índices Compuestos de Rendimiento:**
  1. `ix_eval_tenant_cohort`: `(tenant_id, cohorte_id)` para acelerar reportes agregados institucionales.
  2. `ix_eval_cohort_guide`: `(cohorte_id, guia_asociada)` para el cálculo del Índice de Brecha Formativa (IBF).
  3. `ix_eval_user_created`: `(user_id, timestamp)` para series temporales y visualización de progreso del alumno.

### 3.5 Tablas de Psicometría y Modelado del Estudiante (`student_mastery` y `student_snapshots`)
* **Archivo de Definición:** `backend/modules/adaptive/models.py`.
* **Propósito:** Mantiene el estado bayesiano actual y las trayectorias longitudinales del estudiante a lo largo del Espacio de Conocimiento (KST).

| Tabla | Columna Clave | Tipo | Restricción FK | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `student_mastery` | `user_id` | `VARCHAR(100) PK` | `FOREIGN KEY (users.id) ON DELETE CASCADE` | Vector continuo actual $P(L)$ de las 7 competencias tras cada evaluación. |
| `student_learning_snapshots` | `id` | `INTEGER PK AUTO` | `FOREIGN KEY (users.id) ON DELETE CASCADE` | Snapshots periódicos para reconstruir curvas de aprendizaje y ganancia de Hake ($g=0.74$). |

### 3.6 Tabla `learning_activity_events` (Telemetría de Actividad y Navegación)
* **Archivo de Definición:** `backend/modules/analytics_history/models.py`.
* **Propósito:** Registro granular y cronológico de la interacción del alumno con el simulador (apertura de casos, inspección en negatoscopio/ECG y apertura de debate socrático) para auditoría formativa.

| Columna | Tipo de Dato | Nulo | Restricciones / Índices | Descripción Técnica |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `INTEGER` | NO | `PRIMARY KEY AUTOINCREMENT` | Identificador único de evento. |
| `user_id` | `VARCHAR(100)` | NO | `FOREIGN KEY (users.id) ON DELETE CASCADE`, `INDEX` | Usuario que ejecutó la acción formativa. |
| `tenant_id` | `VARCHAR(50)` | NO | `FOREIGN KEY (tenants.id) ON DELETE CASCADE`, `INDEX` | Institución médica vinculada. |
| `case_id` | `VARCHAR(100)` | NO | `INDEX` | Caso clínico objeto de la interacción. |
| `event_type` | `VARCHAR(50)` | NO | `INDEX` | Tipo de evento (`case_opened`, `paraclinical_inspected`, `socratic_debrief_opened`). |
| `metadata_json` | `TEXT` | NO | `DEFAULT '{}'` | Metadata contextual estructurada (zoom, estudio inspeccionado, omisión debatida). |
| `timestamp` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP`, `INDEX` | Marca temporal UTC del evento. |

* **Índices Compuestos de Rendimiento:**
  1. `ix_event_user_case_time`: `(user_id, case_id, timestamp)` para reconstruir la cronología de resolución del caso por alumno.
  2. `ix_event_tenant_type`: `(tenant_id, event_type)` para métricas institucionales de adopción pedagógica.

### 3.7 Tabla `magic_link_tokens` (Control de Enlaces e Invitaciones Configurables)
* **Archivo de Definición:** `backend/modules/auth/models.py`.
* **Propósito:** Persistencia, control de expiración, auditoría y canje de enlaces de acceso directo sin contraseña. Almacena exclusivamente el hash criptográfico `SHA-256` para evitar la exposición de tokens activos en volcados de datos.

| Columna | Tipo de Dato | Nulo | Restricciones / Índices | Descripción Técnica |
| :--- | :--- | :---: | :--- | :--- |
| `id` | `VARCHAR(64)` | NO | `PRIMARY KEY` | Identificador único del enlace (UUID v4). |
| `token_hash` | `VARCHAR(64)` | NO | `UNIQUE`, `INDEX` | Resumen SHA-256 del token opaco emitido. |
| `email` | `VARCHAR(150)` | SÍ | `INDEX` | Correo del destinatario si el enlace es nominativo. |
| `recipient_name` | `VARCHAR(150)` | SÍ | — | Nombre referencial o etiqueta de la cohorte invitada. |
| `rol` | `VARCHAR(50)` | NO | `DEFAULT 'alumno'` | Rol RBAC concedido (`alumno`, `docente`, `administrador`). |
| `tenant_id` | `VARCHAR(50)` | NO | `FOREIGN KEY (tenants.id) ON DELETE CASCADE`, `INDEX` | Institución vinculada para aislamiento de datos. |
| `target_path` | `VARCHAR(255)` | NO | `DEFAULT '/cases'` | Ruta clínica de destino tras canjear el token. |
| `cohorte_id` | `VARCHAR(50)` | SÍ | `DEFAULT 'general'` | Cohorte académica de asignación pedagógica. |
| `restrict_domain`| `BOOLEAN` | NO | `DEFAULT 0` | Si exige que el dominio del correo coincida con el tenant. |
| `expires_at` | `SafeDateTime` | NO | `INDEX` | Marca temporal UTC en la que expira la validez del link. |
| `max_uses` | `INTEGER` | NO | `DEFAULT 1` | Número máximo de canjes admitidos (1 para uso único o $N$ para cohorte). |
| `used_count` | `INTEGER` | NO | `DEFAULT 0` | Conteo de veces que ha sido canjeado exitosamente. |
| `is_revoked` | `BOOLEAN` | NO | `DEFAULT 0`, `INDEX` | Bandera de revocación manual inmediata por el administrador. |
| `created_by_user_id`| `VARCHAR(100)`| NO | `FOREIGN KEY (users.id) ON DELETE CASCADE` | Administrador emisor del enlace para auditoría. |
| `created_at` | `SafeDateTime` | NO | `DEFAULT CURRENT_TIMESTAMP` | Marca temporal UTC de creación. |

* **Índices de Rendimiento y Seguridad:**
  1. `ix_magic_token_hash`: Búsqueda instantánea $O(1)$ durante el canje público.
  2. `ix_magic_tenant_active`: `(tenant_id, is_revoked)` para listados ágiles en consola administrativa.
  3. `ix_magic_expires`: `(expires_at)` para depuración y descarte de tokens vencidos.

---

## 4. Scripts Determinísticos de Migración y Validación de Esquema

Para garantizar la evolución continua sin pérdida de datos ni regresiones, la plataforma cuenta con scripts de migración transaccional:
1. `scripts/migrate_history_to_ateneo_clinical.py`:
   - Migración inicial de JSON hacia SQLite relacional, desglosando fases y Faithfulness Scores con deduplicación.
2. `scripts/migrate_auth_telemetry_v2.py`:
   - Migración idempotente integral (Fases 1 a 5): valida columnas de auditoría en `users`, tabla `user_sessions`, columnas de inferencia en `evaluation_history` y tabla `learning_activity_events`.
   - Ejecuta `PRAGMA foreign_key_check` y `PRAGMA integrity_check`, garantizando la retención íntegra de las evaluaciones preexistentes y salas colaborativas.
3. `scripts/migrate_magic_links.py`:
   - Migración idempotente de la Fase 1 de Magic Links: crea la tabla `magic_link_tokens` y sus índices criptográficos, validando la integridad física y retención absoluta de registros.

---

## 5. Pruebas Automatizadas de Integridad de Datos

La arquitectura de persistencia está respaldada por suites unitarias de base de datos en `backend/tests/`:
* `test_auth_security.py`: Valida unicidad de correo, integridad de FKs, ciclo de vida JTI y revocación por logout.
* `test_telemetry.py`: Valida contratos Pydantic de telemetría de inferencia, persistencia física de latencia y métricas institucionales en `AnalyticsHistoryService`.
* `test_learning_events.py`: Valida el ciclo de vida de `LearningActivityEventModel`, operaciones en `LearningEventRepository` y contratos Pydantic.
* `test_api_endpoints.py`: Valida transacciones ACID de inserción y consulta en `evaluation_history`, `user_sessions`, `learning_activity_events` y `ateneo_rooms`.
* `test_paper_differentiators.py`: Valida agregaciones SQL nativas (`AVG`, `COUNT`, agrupamiento por cohorte y cálculo de IBF).
