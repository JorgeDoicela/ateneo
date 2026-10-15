import os
import uuid
import secrets
import hashlib
import datetime
from typing import List, Optional, Tuple, Dict, Any
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from models.schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserRole,
    User,
    RegisterRequest,
    RegisterResponse,
    MagicLinkCreateRequest,
    MagicLinkBatchCreateRequest,
    MagicLinkResponse,
    MagicLinkConsumeRequest,
    MagicLinkConsumeResponse,
    MagicLinkVerifyResponse,
)
from modules.auth.models import UserModel, UserSessionModel, MagicLinkTokenModel
from modules.auth.repository import (
    UserRepository,
    TenantRepository,
    UserSessionRepository,
    MagicLinkRepository,
)


class AuthService:
    """
    Servicio de Dominio para Autenticación e Identidad.
    Centraliza el login, verificación de credenciales, registro institucional y emisión de tokens JWT,
    apoyado en un repositorio de persistencia durable.
    """
    def __init__(
        self, 
        repository: UserRepository, 
        tenant_repository: Optional[TenantRepository] = None,
        session_repository: Optional[UserSessionRepository] = None,
        magic_link_repository: Optional[MagicLinkRepository] = None
    ):
        self.repository = repository
        self.tenant_repository = tenant_repository or TenantRepository(repository.db)
        self.session_repository = session_repository
        self.magic_link_repository = magic_link_repository or MagicLinkRepository(repository.db)

    def seed_demo_users_if_needed(self) -> None:
        """Siembra los 3 perfiles demo institucionales si la base de datos de usuarios está vacía."""
        if self.repository.count() > 0:
            return

        demo_users = [
            {
                "id": "usr_admin_001",
                "email": "admin@ateneo.edu.ec",
                "nombre": "Dra. Valeria Gómez (Administradora)",
                "rol": UserRole.ADMINISTRADOR.value,
                "password": os.getenv("DEMO_ADMIN_PASSWORD", "Admin123!")
            },
            {
                "id": "usr_docente_001",
                "email": "docente@ateneo.edu.ec",
                "nombre": "Dr. Carlos Andrade (Docente de Medicina)",
                "rol": UserRole.DOCENTE.value,
                "password": os.getenv("DEMO_DOCENTE_PASSWORD", "Docente123!")
            },
            {
                "id": "usr_alumno_001",
                "email": "alumno@ateneo.edu.ec",
                "nombre": "Estudiante María José Silva",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            },
            {
                "id": "usr_estudiante_002",
                "email": "juan.perez@ateneo.edu.ec",
                "nombre": "Estudiante Juan Pérez",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            },
            {
                "id": "usr_estudiante_003",
                "email": "carolina.mendoza@ateneo.edu.ec",
                "nombre": "Estudiante Carolina Mendoza",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            },
            {
                "id": "usr_estudiante_004",
                "email": "mateo.torres@ateneo.edu.ec",
                "nombre": "Estudiante Mateo Torres",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            },
            {
                "id": "usr_estudiante_005",
                "email": "sofia.gallegos@ateneo.edu.ec",
                "nombre": "Estudiante Sofía Gallegos",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            },
            {
                "id": "usr_estudiante_006",
                "email": "david.moreno@ateneo.edu.ec",
                "nombre": "Estudiante David Moreno",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            },
            {
                "id": "usr_estudiante_007",
                "email": "valeria.castro@ateneo.edu.ec",
                "nombre": "Estudiante Valeria Castro",
                "rol": UserRole.ALUMNO.value,
                "password": os.getenv("DEMO_ALUMNO_PASSWORD", "Alumno123!")
            }
        ]

        now = datetime.datetime.utcnow().isoformat()
        for u in demo_users:
            record = UserModel(
                id=u["id"],
                email=u["email"].lower(),
                nombre=u["nombre"],
                rol=u["rol"],
                hashed_password=get_password_hash(u["password"]),
                activo=True,
                tenant_id="tenant_default",
                created_at=now
            )
            self.repository.create(record)

    def authenticate(
        self, 
        req: LoginRequest, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None
    ) -> Optional[TokenResponse]:
        email_clean = req.email.strip().lower()
        user_record = self.repository.get_by_email(email_clean)

        if not user_record:
            return None

        # 1. Comprobación de bloqueo temporal defensivo por fuerza bruta
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        if getattr(user_record, "locked_until", None):
            locked_dt = user_record.locked_until
            if locked_dt.tzinfo is None:
                locked_dt = locked_dt.replace(tzinfo=datetime.timezone.utc)
            if locked_dt > now_utc:
                minutos_restantes = max(1, int((locked_dt - now_utc).total_seconds() / 60))
                raise PermissionError(
                    f"Cuenta bloqueada temporalmente por múltiples intentos fallidos. Intente nuevamente en {minutos_restantes} minutos."
                )
            else:
                user_record.locked_until = None
                user_record.failed_login_attempts = 0
                self.repository.update(user_record)

        # 2. Verificación de credenciales
        if not verify_password(req.password, user_record.hashed_password):
            user_record.failed_login_attempts = (getattr(user_record, "failed_login_attempts", 0) or 0) + 1
            if user_record.failed_login_attempts >= 5:
                user_record.locked_until = now_utc + datetime.timedelta(minutes=15)
                self.repository.update(user_record)
                if self.session_repository:
                    self.session_repository.revoke_all_for_user(user_record.id)
                raise PermissionError(
                    "Cuenta bloqueada temporalmente por 5 intentos fallidos consecutivos. Intente nuevamente en 15 minutos."
                )
            self.repository.update(user_record)
            return None


        if not user_record.activo:
            raise PermissionError("La cuenta de usuario está desactivada")

        # 3. Acceso exitoso: reiniciar contadores y registrar auditoría
        user_record.failed_login_attempts = 0
        user_record.locked_until = None
        user_record.login_count = (getattr(user_record, "login_count", 0) or 0) + 1
        user_record.last_login_at = now_utc
        self.repository.update(user_record)

        role_enum = UserRole(user_record.rol)
        resolved_tenant = getattr(user_record, "tenant_id", "tenant_default") or "tenant_default"
        last_login_str = user_record.last_login_at.isoformat() if user_record.last_login_at else None

        user_domain = User(
            id=user_record.id,
            email=user_record.email,
            nombre=user_record.nombre,
            rol=role_enum,
            hashed_password=user_record.hashed_password,
            activo=user_record.activo,
            tenant_id=resolved_tenant,
            last_login_at=last_login_str,
            login_count=user_record.login_count,
            email_verified=bool(getattr(user_record, "email_verified", False))
        )

        token_jti = str(uuid.uuid4())
        expire_dt = now_utc + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user_domain, jti=token_jti)

        # 4. Registrar sesión institucional activa con claim jti criptográfico
        if self.session_repository:
            session_record = UserSessionModel(
                id=token_jti,
                user_id=user_record.id,
                tenant_id=resolved_tenant,
                ip_address=ip_address,
                user_agent=(user_agent[:255] if user_agent else None),
                is_revoked=False,
                expires_at=expire_dt,
                created_at=now_utc
            )
            self.session_repository.create(session_record)

        user_res = UserResponse(
            id=user_record.id,
            email=user_record.email,
            nombre=user_record.nombre,
            rol=role_enum,
            tenant_id=resolved_tenant,
            last_login_at=last_login_str,
            login_count=user_record.login_count,
            email_verified=bool(getattr(user_record, "email_verified", False)),
            activo=user_record.activo
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_res
        )

    def logout_session(self, jti: str) -> bool:
        """Revoca inmediatamente la sesión identificada por su claim criptográfico JTI."""
        if not jti:
            return False
        if self.session_repository:
            return self.session_repository.revoke(jti)
        return True

    def is_session_revoked(self, jti: str) -> bool:
        """Determina si el token JWT con identificador JTI ha sido revocado en el servidor."""
        if not jti or not self.session_repository:
            return False
        return self.session_repository.is_jti_revoked(jti)

    def revoke_all_user_sessions(self, user_id: str) -> int:
        """Invalida masivamente todas las sesiones activas asociadas al identificador de usuario."""
        if not user_id or not self.session_repository:
            return 0
        return self.session_repository.revoke_all_for_user(user_id)



    def list_users(self, tenant_id: Optional[str] = None) -> List[UserResponse]:
        records = self.repository.get_all(tenant_id=tenant_id)
        return [
            UserResponse(
                id=u.id,
                email=u.email,
                nombre=u.nombre,
                rol=UserRole(u.rol),
                tenant_id=getattr(u, "tenant_id", "tenant_default") or "tenant_default",
                last_login_at=u.last_login_at.isoformat() if getattr(u, "last_login_at", None) else None,
                login_count=getattr(u, "login_count", 0) or 0,
                email_verified=bool(getattr(u, "email_verified", False)),
                activo=u.activo
            )
            for u in records
        ]

    def register_user(self, req: RegisterRequest) -> RegisterResponse:
        """
        Registra un nuevo facultativo o estudiante en la plataforma Ateneo+.
        Resuelve determinísticamente el tenant por dominio institucional,
        verifica que no exista duplicidad y aplica hash criptográfico Bcrypt.
        """
        email_clean = req.email.strip().lower()

        # 1. Comprobar duplicidad de correo electrónico
        existing_user = self.repository.get_by_email(email_clean)
        if existing_user:
            raise ValueError(f"El correo electrónico '{email_clean}' ya se encuentra registrado en el sistema.")

        # 2. Resolver tenant institucional por dominio
        domain = email_clean.split("@")[-1]
        tenant = self.tenant_repository.get_by_dominio(domain)
        if not tenant or not tenant.activo:
            raise LookupError(
                f"El dominio institucional '@{domain}' no está habilitado para auto-registro. Contacte a la coordinación académica de su facultad."
            )

        # 3. Generar identificador determinístico y fecha UTC
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        role_value = req.rol.value if isinstance(req.rol, UserRole) else str(req.rol)

        # 4. Crear y persistir nuevo usuario
        new_user = UserModel(
            id=user_id,
            email=email_clean,
            nombre=req.nombre.strip(),
            rol=role_value,
            hashed_password=get_password_hash(req.password),
            activo=True,
            tenant_id=tenant.id,
            last_login_at=None,
            login_count=0,
            failed_login_attempts=0,
            locked_until=None,
            email_verified=False,
            created_at=now_utc
        )
        self.repository.create(new_user)

        return RegisterResponse(
            id=new_user.id,
            email=new_user.email,
            nombre=new_user.nombre,
            rol=UserRole(new_user.rol),
            tenant_id=new_user.tenant_id,
            mensaje=f"Usuario registrado exitosamente en {tenant.nombre_institucional.replace(' (MSP Ecuador)', '').replace(' (GPC Ecuador)', '').strip()}."
        )

    def create_magic_link(
        self,
        admin_user_id: str,
        admin_tenant_id: str,
        req: MagicLinkCreateRequest,
        base_frontend_url: str = "http://localhost:5174"
    ) -> MagicLinkResponse:
        """
        Genera un Magic Link seguro con token opaco, persiste exclusivamente su hash SHA-256
        y retorna el contrato completo con URL de acceso directo.
        """
        target_tenant_id = req.tenant_id or admin_tenant_id
        tenant = self.tenant_repository.get_by_id(target_tenant_id)
        if not tenant:
            raise ValueError(f"Institución médica con ID '{target_tenant_id}' no encontrada.")

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now_utc + datetime.timedelta(hours=req.duracion_horas)

        email_clean = req.email.strip().lower() if req.email else None

        # Si no se envió un correo externo y es un enlace para una persona nominativa o reutilizable (ej: "Estudiante 1"),
        # se auto-aprovisiona una identidad institucional fija para que todos sus reingresos preserven la misma cuenta
        is_cohort_group = (req.max_uses > 1) and (not req.es_reutilizable) and (
            (req.cohorte_id and req.cohorte_id != "general") or (req.recipient_name and req.recipient_name.lower().startswith("cohorte"))
        )

        if not email_clean and not is_cohort_group:
            label = req.recipient_name if req.recipient_name else req.rol
            clean_slug = "".join(c for c in label.lower() if c.isalnum())[:15] or req.rol.lower()
            tenant_domain = tenant.dominio_email or "ateneo.edu.ec"
            email_clean = f"{clean_slug}.{uuid.uuid4().hex[:6]}@{tenant_domain}"

        link_record = MagicLinkTokenModel(
            id=str(uuid.uuid4()),
            token_hash=token_hash,
            email=email_clean,
            recipient_name=req.recipient_name.strip() if req.recipient_name else None,
            rol=req.rol.strip().lower(),
            tenant_id=target_tenant_id,
            target_path=req.target_path.strip() or "/cases",
            cohorte_id=req.cohorte_id.strip() if req.cohorte_id else "general",
            restrict_domain=bool(req.restrict_domain),
            expires_at=expires_at,
            max_uses=req.max_uses,
            used_count=0,
            is_revoked=False,
            created_by_user_id=admin_user_id,
            created_at=now_utc
        )

        created = self.magic_link_repository.create(link_record)
        magic_url = f"{base_frontend_url.rstrip('/')}/auth/magic-login?token={raw_token}"

        return MagicLinkResponse(
            id=created.id,
            magic_link_url=magic_url,
            email=created.email,
            recipient_name=created.recipient_name,
            rol=created.rol,
            tenant_id=created.tenant_id,
            target_path=created.target_path,
            cohorte_id=created.cohorte_id,
            restrict_domain=created.restrict_domain,
            expires_at=created.expires_at.isoformat() if hasattr(created.expires_at, "isoformat") else str(created.expires_at),
            max_uses=created.max_uses,
            used_count=created.used_count,
            is_revoked=created.is_revoked,
            created_at=created.created_at.isoformat() if hasattr(created.created_at, "isoformat") else str(created.created_at)
        )

    def create_magic_links_batch(
        self,
        admin_user_id: str,
        admin_tenant_id: str,
        req: MagicLinkBatchCreateRequest,
        base_frontend_url: str = "http://localhost:5174"
    ) -> List[MagicLinkResponse]:
        """
        Genera atómicamente un lote de Magic Links configurables con tokens independientes,
        nombres correlativos y persistencia en una sola transacción.
        """
        target_tenant_id = req.tenant_id or admin_tenant_id
        tenant = self.tenant_repository.get_by_id(target_tenant_id)
        if not tenant:
            raise ValueError(f"Institución médica con ID '{target_tenant_id}' no encontrada.")

        tenant_domain = tenant.dominio_email or "ateneo.edu.ec"
        clean_prefix = req.base_name.strip() if req.base_name else (
            "Estudiante" if req.rol == "alumno" else "Docente" if req.rol == "docente" else "Administrador"
        )

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now_utc + datetime.timedelta(hours=req.duracion_horas)

        tokens_to_create: List[MagicLinkTokenModel] = []
        raw_tokens_map: dict = {}

        for i in range(req.count):
            current_num = req.start_index + i
            recipient_name = f"{clean_prefix} {current_num}"

            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            link_id = str(uuid.uuid4())
            raw_tokens_map[link_id] = raw_token

            clean_slug = "".join(c for c in clean_prefix.lower() if c.isalnum())[:12] or req.rol.lower()
            email_clean = f"{clean_slug}{current_num}.{uuid.uuid4().hex[:5]}@{tenant_domain}"

            tokens_to_create.append(
                MagicLinkTokenModel(
                    id=link_id,
                    token_hash=token_hash,
                    email=email_clean,
                    recipient_name=recipient_name,
                    rol=req.rol.strip().lower(),
                    tenant_id=target_tenant_id,
                    target_path=req.target_path.strip() or ("/teacher/cases" if req.rol == "docente" else "/cases"),
                    cohorte_id=req.cohorte_id.strip() if req.cohorte_id else "general",
                    restrict_domain=bool(req.restrict_domain),
                    expires_at=expires_at,
                    max_uses=req.max_uses,
                    used_count=0,
                    is_revoked=False,
                    created_by_user_id=admin_user_id,
                    created_at=now_utc
                )
            )

        created_links = self.magic_link_repository.create_batch(tokens_to_create)

        results: List[MagicLinkResponse] = []
        for created in created_links:
            raw_tok = raw_tokens_map.get(created.id, "")
            magic_url = f"{base_frontend_url.rstrip('/')}/auth/magic-login?token={raw_tok}"
            results.append(
                MagicLinkResponse(
                    id=created.id,
                    magic_link_url=magic_url,
                    email=created.email,
                    recipient_name=created.recipient_name,
                    rol=created.rol,
                    tenant_id=created.tenant_id,
                    target_path=created.target_path,
                    cohorte_id=created.cohorte_id,
                    restrict_domain=created.restrict_domain,
                    expires_at=created.expires_at.isoformat() if hasattr(created.expires_at, "isoformat") else str(created.expires_at),
                    max_uses=created.max_uses,
                    used_count=created.used_count,
                    is_revoked=created.is_revoked,
                    created_at=created.created_at.isoformat() if hasattr(created.created_at, "isoformat") else str(created.created_at)
                )
            )
        return results

    def verify_magic_link(self, token: str) -> MagicLinkVerifyResponse:
        """
        Verifica criptográficamente un Magic Link sin consumirlo ni incrementar su contador de usos.
        Permite mostrar al usuario la información del acceso (rol, destino, invitación) antes de confirmar el ingreso.
        """
        token_clean = token.strip()
        if not token_clean:
            raise ValueError("El token de acceso es obligatorio.")

        token_hash = hashlib.sha256(token_clean.encode("utf-8")).hexdigest()
        link_record = self.magic_link_repository.get_by_hash(token_hash)

        if not link_record:
            raise PermissionError("Enlace de acceso no válido o inexistente.")

        if link_record.is_revoked:
            raise PermissionError("Este enlace de acceso ha sido revocado por un administrador.")

        if link_record.used_count >= link_record.max_uses:
            raise PermissionError("Este enlace ha alcanzado el límite máximo de usos permitidos.")

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        exp = link_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=datetime.timezone.utc)

        if exp < now_utc:
            raise PermissionError("El enlace de acceso ha expirado.")

        is_cohort = (link_record.max_uses > 1) and (
            (link_record.cohorte_id and link_record.cohorte_id != "general") or
            (link_record.recipient_name and link_record.recipient_name.lower().startswith("cohorte"))
        )
        requires_identity = (not link_record.email) and is_cohort
        tenant = self.tenant_repository.get_by_id(link_record.tenant_id)
        tenant_name = tenant.nombre_institucional if tenant else None

        return MagicLinkVerifyResponse(
            is_valid=True,
            rol=link_record.rol,
            recipient_name=link_record.recipient_name,
            target_path=link_record.target_path,
            requires_identity=requires_identity,
            email=link_record.email,
            expires_at=link_record.expires_at.isoformat() if hasattr(link_record.expires_at, "isoformat") else str(link_record.expires_at),
            tenant_name=tenant_name
        )

    def consume_magic_link(
        self,
        req: MagicLinkConsumeRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> MagicLinkConsumeResponse:
        """
        Canjea un Magic Link verificando criptográficamente su validez, vigencia y límite de usos.
        Aprovisiona al usuario en el tenant si es nuevo y emite un token JWT oficial con sesión persistida (JTI).
        """
        token_clean = req.token.strip()
        if not token_clean:
            raise ValueError("El token de acceso es obligatorio.")

        token_hash = hashlib.sha256(token_clean.encode("utf-8")).hexdigest()
        link_record = self.magic_link_repository.get_by_hash(token_hash)

        if not link_record:
            raise PermissionError("Enlace de acceso no válido o inexistente.")

        if link_record.is_revoked:
            raise PermissionError("Este enlace de acceso ha sido revocado por un administrador.")

        if link_record.used_count >= link_record.max_uses:
            raise PermissionError("Este enlace ha alcanzado el límite máximo de usos permitidos.")

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        exp = link_record.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=datetime.timezone.utc)

        if exp < now_utc:
            raise PermissionError("El enlace de acceso ha expirado.")

        # Resolución o provisión del usuario
        resolved_email = link_record.email
        resolved_name = link_record.recipient_name

        if not resolved_email:
            if req.email:
                resolved_email = str(req.email).strip().lower()
                if req.nombre:
                    resolved_name = req.nombre.strip()
            elif link_record.max_uses == 1 or (link_record.recipient_name and not link_record.recipient_name.lower().startswith("cohorte")):
                tenant = self.tenant_repository.get_by_id(link_record.tenant_id)
                domain = tenant.dominio_email if tenant and tenant.dominio_email else "ateneo.edu.ec"
                label = link_record.recipient_name or link_record.rol
                clean_slug = "".join(c for c in label.lower() if c.isalnum())[:15] or link_record.rol.lower()
                resolved_name = link_record.recipient_name or f"{link_record.rol.capitalize()} Invitado"
                resolved_email = f"{clean_slug}.{link_record.id[:6]}@{domain}"
                # Persistimos para garantizar que futuros reingresos al mismo enlace reutilicen la misma cuenta
                link_record.email = resolved_email
                self.magic_link_repository.update(link_record)
            else:
                # Enlace grupal de cohorte (max_uses > 1): requiere email del participante para diferenciar evaluaciones
                raise ValueError("Este enlace de cohorte requiere ingresar su correo electrónico.")

        # Validación opcional de restricción de dominio institucional
        if link_record.restrict_domain:
            tenant = self.tenant_repository.get_by_id(link_record.tenant_id)
            if tenant and tenant.dominio_email:
                if not resolved_email.endswith(f"@{tenant.dominio_email.lower()}"):
                    raise PermissionError(
                        f"Este enlace institucional requiere un correo con dominio @{tenant.dominio_email}."
                    )

        # Buscar usuario existente o crear nuevo registro
        user_record = self.repository.get_by_email(resolved_email)
        if not user_record:
            user_id = f"usr_{uuid.uuid4().hex[:12]}"
            # Contraseña temporal fuerte e inactiva para registro express
            random_pwd = secrets.token_urlsafe(24)
            user_record = UserModel(
                id=user_id,
                email=resolved_email,
                nombre=resolved_name or resolved_email.split("@")[0].capitalize(),
                rol=link_record.rol,
                hashed_password=get_password_hash(random_pwd),
                activo=True,
                tenant_id=link_record.tenant_id,
                last_login_at=now_utc,
                login_count=1,
                failed_login_attempts=0,
                locked_until=None,
                email_verified=True,
                created_at=now_utc
            )
            self.repository.create(user_record)
        else:
            user_record.last_login_at = now_utc
            user_record.login_count = (getattr(user_record, "login_count", 0) or 0) + 1
            if link_record.rol and user_record.rol != link_record.rol:
                user_record.rol = link_record.rol
            if link_record.tenant_id and user_record.tenant_id != link_record.tenant_id:
                user_record.tenant_id = link_record.tenant_id
            self.repository.update(user_record)

        # Incrementar contador de usos del Magic Link
        link_record.used_count += 1
        self.magic_link_repository.update(link_record)

        # Generar JTI criptográfico para la sesión
        session_jti = str(uuid.uuid4())
        session_expires = now_utc + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        if self.session_repository:
            session_model = UserSessionModel(
                id=session_jti,
                user_id=user_record.id,
                tenant_id=user_record.tenant_id,
                ip_address=ip_address,
                user_agent=user_agent,
                is_revoked=False,
                expires_at=session_expires,
                created_at=now_utc
            )
            self.session_repository.create(session_model)

        access_token = create_access_token(
            user=user_record,
            jti=session_jti
        )

        user_profile = UserResponse(
            id=user_record.id,
            email=user_record.email,
            nombre=user_record.nombre,
            rol=UserRole(user_record.rol),
            tenant_id=user_record.tenant_id,
            last_login_at=user_record.last_login_at.isoformat() if getattr(user_record, "last_login_at", None) else None,
            login_count=getattr(user_record, "login_count", 1) or 1,
            email_verified=getattr(user_record, "email_verified", False) or False,
            activo=getattr(user_record, "activo", True)
        )

        return MagicLinkConsumeResponse(
            access_token=access_token,
            token_type="bearer",
            target_path=link_record.target_path,
            user=user_profile
        )

    def list_magic_links(self, tenant_id: str, limit: int = 100) -> List[MagicLinkResponse]:
        links = self.magic_link_repository.list_by_tenant(tenant_id, limit=limit)
        return [
            MagicLinkResponse(
                id=l.id,
                magic_link_url="",  # La URL sólo se expone en la creación para evitar filtraciones
                email=l.email,
                recipient_name=l.recipient_name,
                rol=l.rol,
                tenant_id=l.tenant_id,
                target_path=l.target_path,
                cohorte_id=l.cohorte_id,
                restrict_domain=l.restrict_domain,
                expires_at=l.expires_at.isoformat() if hasattr(l.expires_at, "isoformat") else str(l.expires_at),
                max_uses=l.max_uses,
                used_count=l.used_count,
                is_revoked=l.is_revoked,
                created_at=l.created_at.isoformat() if hasattr(l.created_at, "isoformat") else str(l.created_at)
            )
            for l in links
        ]

    def revoke_magic_link(self, link_id: str) -> bool:
        return self.magic_link_repository.revoke(link_id)

    def delete_magic_link(self, link_id: str) -> bool:
        return self.magic_link_repository.delete(link_id)

    def purge_revoked_magic_links(self, tenant_id: str) -> int:
        return self.magic_link_repository.purge_revoked(tenant_id)


