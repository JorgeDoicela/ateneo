import os
import uuid
import datetime
from typing import List, Optional
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
)
from modules.auth.models import UserModel, UserSessionModel
from modules.auth.repository import UserRepository, TenantRepository, UserSessionRepository


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
        session_repository: Optional[UserSessionRepository] = None
    ):
        self.repository = repository
        self.tenant_repository = tenant_repository or TenantRepository(repository.db)
        self.session_repository = session_repository

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
            mensaje=f"Usuario registrado exitosamente en {tenant.nombre_institucional}."
        )

