from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional

class EjeClinico(str, Enum):
    DIAGNOSTICO = "diagnóstico"
    TRATAMIENTO = "tratamiento"
    PREVENCION = "prevención"
    SEGUIMIENTO = "seguimiento"

class CitaNormativa(BaseModel):
    guia: str = Field(default="GPC Ecuador", description="Nombre de la Guía de Práctica Clínica (GPC Ecuador)")
    seccion: str = Field(default="General", description="Sección o capítulo relevante dentro de la norma")
    pagina: Optional[int] = Field(default=None, description="Número de página de la norma si está disponible")
    texto_relevante: str = Field(default="Guía de Práctica Clínica oficial de Ecuador.", description="Cita textual o fragmento normativo exacto de respaldo")

class CompetenciaDeficiente(BaseModel):
    eje: EjeClinico = Field(..., description="Eje clínico: diagnóstico, tratamiento, prevención o seguimiento")
    descripcion: str = Field(..., description="Breve detalle de la competencia deficiente o brecha respecto a la GPC")

    @field_validator("eje", mode="before")
    @classmethod
    def normalize_eje(cls, v: str) -> str:
        if not isinstance(v, str):
            return "tratamiento"
        val = v.lower().strip()
        # Mapeo de sinónimos y variaciones ortográficas
        if any(w in val for w in ["diag", "evalua", "sintom", "presun"]):
            return EjeClinico.DIAGNOSTICO.value
        elif any(w in val for w in ["trat", "terap", "farmac", "dosis", "manej", "medic"]):
            return EjeClinico.TRATAMIENTO.value
        elif any(w in val for w in ["prev", "profila", "promoc", "vacun"]):
            return EjeClinico.PREVENCION.value
        elif any(w in val for w in ["segui", "monit", "evoluc", "control", "alta"]):
            return EjeClinico.SEGUIMIENTO.value
        return EjeClinico.TRATAMIENTO.value

class EvaluationResult(BaseModel):
    score: float = Field(..., ge=0, le=10, description="Puntuación cualitativa/cuantitativa entre 0 y 10")
    score_max: int = Field(10, description="Puntuación máxima posible")
    aciertos: List[str] = Field(default_factory=list, description="Lista de aspectos clínicos acertados por el estudiante")
    omisiones: List[str] = Field(default_factory=list, description="Lista de Omisiones o elementos de la norma no abordados")
    competencias_deficientes: List[CompetenciaDeficiente] = Field(
        default_factory=list, 
        description="Lista de competencias deficientes categorizadas por eje clínico (diagnóstico, tratamiento, prevención, seguimiento)"
    )
    cita_normativa: CitaNormativa = Field(..., description="Referencia explícita a la norma MSP")
    citas_normativas: Optional[List[CitaNormativa]] = Field(default=None, description="Colección retrocompatible de citas normativas ancladas")
    retroalimentacion_general: str = Field(..., description="Retroalimentación formativa y constructiva para el estudiante")

    @model_validator(mode="after")
    def populate_citas_normativas(self):
        if not self.citas_normativas and self.cita_normativa:
            self.citas_normativas = [self.cita_normativa]
        return self
    # Faithfulness Score — Diferenciador Científico 3 (Anti-Alucinación Normativa)
    faithfulness_score: Optional[float] = Field(None, description="Proporción de afirmaciones clínicas respaldadas por el fragmento normativo recuperado")
    total_claims: Optional[int] = Field(None, description="Total de afirmaciones clínicas evaluadas")
    grounded_claims: Optional[int] = Field(None, description="Afirmaciones verificadas en el corpus normativo")
    grounding_level: Optional[str] = Field(None, description="Nivel de grounding normativo: Alto / Moderado / Bajo")
    # Telemetría de Inferencia IA y Observabilidad
    llm_latency_ms: Optional[float] = Field(None, description="Latencia de inferencia del LLM en milisegundos")
    llm_model_used: Optional[str] = Field("gemini-3.8-flash", description="Modelo LLM que generó el dictamen clínico")
    rag_tokens_used: Optional[int] = Field(0, description="Tokens consumidos en prompt y generación")
    paraclinical_studies_count: Optional[int] = Field(0, description="Cantidad de estudios paraclínicos (imágenes/labs) evaluados")

class EvaluationRequest(BaseModel):
    case_id: str = Field(..., description="ID del caso clínico evaluado")
    respuesta_estudiante: str = Field(..., description="Texto libre con el razonamiento del estudiante")

class PhaseSchema(BaseModel):
    fase_numero: int = Field(..., description="Número ordinal de la fase (1, 2, 3...)")
    titulo: str = Field(..., description="Título del hito clínico (ej. Anamnesis & Sospecha)")
    descripcion: str = Field(..., description="Contexto del paciente revelado en esta fase")
    datos_revelados: Optional[str] = Field(None, description="Datos de anamnesis o paraclínicos que se desbloquean")
    estudios_adjuntos: Optional[List[str]] = Field(default_factory=list, description="Lista de URLs de imágenes o estudios disponibles")
    pregunta_evaluativa: str = Field(..., description="Pregunta específica a responder en esta fase")
    ejes_evaluados: List[str] = Field(default_factory=lambda: ["diagnóstico"], description="Ejes clínicos foco de la fase")

class PhaseEvaluationResult(BaseModel):
    fase_numero: int = Field(..., description="Número de fase evaluada")
    score_fase: float = Field(..., ge=0, le=10, description="Puntaje de la fase (0-10)")
    aciertos: List[str] = Field(default_factory=list, description="Aciertos en la fase")
    omisiones: List[str] = Field(default_factory=list, description="Omisiones en la fase")
    competencias_deficientes: List[CompetenciaDeficiente] = Field(default_factory=list)
    cita_normativa: CitaNormativa = Field(..., description="Cita de GPC relevante para esta fase")
    retroalimentacion_fase: str = Field(..., description="Retroalimentación formativa de la fase")
    desbloquea_siguiente: bool = Field(default=True, description="Indica si se aprueba avanzar a la siguiente fase")
    datos_fase_siguiente: Optional[dict] = Field(None, description="Datos adicionales revelados para la próxima fase")
    llm_latency_ms: Optional[float] = Field(None, description="Latencia de inferencia en milisegundos")
    llm_model_used: Optional[str] = Field("gemini-3.8-flash", description="Modelo LLM utilizado")
    rag_tokens_used: Optional[int] = Field(0, description="Tokens consumidos en prompt y generación")
    paraclinical_studies_count: Optional[int] = Field(0, description="Cantidad de estudios paraclínicos evaluados")


class ClinicalCaseSchema(BaseModel):
    id: str
    guia_asociada: str
    titulo: str
    enunciado: str
    pregunta: str
    imagen_url: Optional[str] = None
    nivel_esperado: Optional[str] = "pregrado_avanzado"
    fragmento_gpc_ideal_id: Optional[str] = None
    modo_simulacion: Optional[str] = "single_turn" # "single_turn" | "fases"
    fases: Optional[List[PhaseSchema]] = None
    competencias_activadas: Optional[List[str]] = None
    tenant_id: Optional[str] = "tenant_default"
    activo: bool = True


class TenantSchema(BaseModel):
    id: str
    codigo: str
    nombre_institucional: str
    dominio_email: str
    gpc_activas: List[str] = Field(default_factory=list)
    activo: bool = True


from enum import Enum


class UserRole(str, Enum):
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    ALUMNO = "alumno"


class User(BaseModel):
    id: str
    email: str
    nombre: str
    rol: UserRole
    hashed_password: str
    activo: bool = True
    tenant_id: str = "tenant_default"
    last_login_at: Optional[str] = None
    login_count: Optional[int] = 0
    failed_login_attempts: Optional[int] = 0
    locked_until: Optional[str] = None
    email_verified: Optional[bool] = False


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    nombre: str
    rol: UserRole
    tenant_id: str = "tenant_default"
    last_login_at: Optional[str] = None
    login_count: Optional[int] = 0
    email_verified: Optional[bool] = False
    activo: Optional[bool] = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterRequest(BaseModel):
    email: str = Field(..., description="Correo institucional universitario u hospitalario")
    password: str = Field(..., min_length=8, description="Contraseña de al menos 8 caracteres con números y símbolos")
    nombre: str = Field(..., min_length=3, description="Nombres y apellidos completos del facultativo")
    rol: Optional[UserRole] = Field(default=UserRole.ALUMNO, description="Rol institucional")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError("El correo electrónico debe ser una dirección institucional válida.")
        return clean

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        has_digit = any(c.isdigit() for c in v)
        has_upper_or_symbol = any(c.isupper() or not c.isalnum() for c in v)
        if not (has_digit and has_upper_or_symbol):
            raise ValueError("La contraseña debe contener al menos un número y una letra mayúscula o símbolo especial.")
        return v


class RegisterResponse(BaseModel):
    id: str
    email: str
    nombre: str
    rol: UserRole
    tenant_id: str
    mensaje: str


class LearningActivityEventCreate(BaseModel):
    case_id: str = Field(..., description="ID del caso clínico en interacción")
    event_type: str = Field(..., description="Tipo de evento: case_opened, paraclinical_inspected, socratic_debrief_opened, etc.")
    metadata: Optional[dict] = Field(default_factory=dict, description="Metadata contextual del evento")
    tenant_id: Optional[str] = Field(None, description="ID del tenant o institución médica")


class LearningActivityEventResponse(BaseModel):
    id: int
    user_id: str
    tenant_id: str
    case_id: str
    event_type: str
    metadata: dict
    timestamp: str


class MagicLinkCreateRequest(BaseModel):
    rol: str = Field(default="alumno", description="Rol asignado: alumno, docente, administrador")
    email: Optional[str] = Field(None, description="Email nominativo opcional")
    recipient_name: Optional[str] = Field(None, description="Nombre referencial o etiqueta de la cohorte")
    tenant_id: Optional[str] = Field(None, description="ID del tenant. Si es None se toma el del administrador emisor")
    duracion_horas: int = Field(default=72, ge=1, le=720, description="Ventana de vigencia en horas (1 a 720)")
    max_uses: int = Field(default=1, ge=1, le=500, description="Límite máximo de canjes (1 a 500)")
    target_path: str = Field(default="/cases", description="Ruta de redirección clínica tras canjear el link")
    cohorte_id: Optional[str] = Field(default="general", description="Cohorte académica para analítica")
    restrict_domain: bool = Field(default=False, description="Exigir coincidencia con el dominio institucional del tenant")
    base_url: Optional[str] = Field(None, description="URL base pública del frontend para construir el link")
    es_reutilizable: bool = Field(default=False, description="Permite múltiples accesos a la misma cuenta del participante durante la vigencia")

    @field_validator("email")
    @classmethod
    def validate_email_syntax(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError("El correo electrónico del destinatario no tiene un formato válido.")
        return clean


class MagicLinkBatchCreateRequest(BaseModel):
    rol: str = Field(default="alumno", description="Rol asignado: alumno, docente, administrador")
    base_name: str = Field(default="Estudiante", description="Prefijo o nombre base para los enlaces")
    start_index: int = Field(default=1, ge=1, le=9999, description="Número inicial de la secuencia (ej: 1)")
    count: int = Field(default=3, ge=1, le=50, description="Cantidad de enlaces a generar en el lote (1 a 50)")
    tenant_id: Optional[str] = Field(None, description="ID del tenant emisor")
    duracion_horas: int = Field(default=168, ge=1, le=720, description="Ventana de vigencia en horas")
    max_uses: int = Field(default=100, ge=1, le=500, description="Límite máximo de usos")
    target_path: str = Field(default="/cases", description="Destino clínico tras ingresar")
    cohorte_id: Optional[str] = Field(default="general", description="Cohorte de analítica")
    restrict_domain: bool = Field(default=False, description="Exigir correo institucional del tenant")
    base_url: Optional[str] = Field(None, description="URL pública del frontend")
    es_reutilizable: bool = Field(default=True, description="Multi-ingreso continuo conservando la misma cuenta de usuario")


class MagicLinkResponse(BaseModel):
    id: str
    magic_link_url: str
    email: Optional[str] = None
    recipient_name: Optional[str] = None
    rol: str
    tenant_id: str
    target_path: str
    cohorte_id: Optional[str] = "general"
    restrict_domain: bool = False
    expires_at: str
    max_uses: int
    used_count: int
    is_revoked: bool
    created_at: str


class MagicLinkConsumeRequest(BaseModel):
    token: str = Field(..., description="Token opaco criptográfico del Magic Link")
    email: Optional[str] = Field(None, description="Email del participante (requerido si el enlace es de cohorte anónima)")
    nombre: Optional[str] = Field(None, description="Nombre del participante (requerido si es nuevo registro de cohorte)")

    @field_validator("email")
    @classmethod
    def validate_consume_email_syntax(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError("El correo electrónico del participante no tiene un formato válido.")
        return clean


class MagicLinkConsumeResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    target_path: str
    user: UserResponse


class MagicLinkVerifyResponse(BaseModel):
    is_valid: bool
    rol: str
    recipient_name: Optional[str] = None
    target_path: str
    requires_identity: bool
    email: Optional[str] = None
    expires_at: str
    tenant_name: Optional[str] = None





