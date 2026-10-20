import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from auth.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    init_demo_users,
    DEMO_USERS_DB,
    UserRole
)

def test_password_hashing():
    raw_password = "PasswordSeguro123!"
    hashed = get_password_hash(raw_password)
    
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("PasswordErroneo", hashed) is False
    print("  [PASS] Hash y verificación de contraseñas (bcrypt/pbkdf2) validado.")

def test_jwt_token_lifecycle():
    from models.schemas import User
    user = User(
        id="usr_test_001",
        email="test@ateneo.edu.ec",
        nombre="Test Interno",
        rol=UserRole.ALUMNO,
        hashed_password="hash_simulado_test",
        activo=True
    )
    token = create_access_token(user)
    assert isinstance(token, str) and len(token) > 20
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test@ateneo.edu.ec"
    assert payload["id"] == "usr_test_001"
    assert payload["rol"] == UserRole.ALUMNO.value
    assert "exp" in payload
    print("  [PASS] Generación, firma criptográfica y decodificación de JWT validado.")

def test_demo_users_database():
    init_demo_users()
    assert len(DEMO_USERS_DB) >= 3
    
    admin = DEMO_USERS_DB.get("admin@ateneo.edu.ec")
    assert admin is not None
    assert admin.rol == UserRole.ADMINISTRADOR
    assert verify_password("Admin123!", admin.hashed_password) is True

    alumno = DEMO_USERS_DB.get("alumno@ateneo.edu.ec")
    assert alumno is not None
    assert alumno.rol == UserRole.ALUMNO
    assert verify_password("Alumno123!", alumno.hashed_password) is True
    print("  [PASS] Catálogo base RBAC (Admin, Docente, Alumno) validado.")

def test_brute_force_lockout_and_login_metrics():
    import pytest
    from core.database import SessionLocal
    from modules.auth.repository import UserRepository
    from modules.auth.service import AuthService
    from models.schemas import LoginRequest

    with SessionLocal() as db:
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)

        test_email = "alumno@ateneo.edu.ec"
        user_record = user_repo.get_by_email(test_email)
        assert user_record is not None, "El usuario demo alumno debe existir"

        # Restablecer estado inicial
        user_record.failed_login_attempts = 0
        user_record.locked_until = None
        user_record.login_count = 0
        user_repo.update(user_record)

        # 1. Cuatro intentos fallidos consecutivos
        for i in range(1, 5):
            res = auth_service.authenticate(LoginRequest(email=test_email, password="WrongPassword!"))
            assert res is None
            u_check = user_repo.get_by_email(test_email)
            assert u_check.failed_login_attempts == i
            assert u_check.locked_until is None

        # 2. Quinto intento fallido: bloqueo temporal
        with pytest.raises(PermissionError) as exc_info:
            auth_service.authenticate(LoginRequest(email=test_email, password="WrongPassword!"))
        assert "bloqueada temporalmente" in str(exc_info.value).lower()
        
        u_check = user_repo.get_by_email(test_email)
        assert u_check.failed_login_attempts >= 5
        assert u_check.locked_until is not None

        # 3. Intento durante bloqueo (incluso con password correcto)
        with pytest.raises(PermissionError) as exc_info:
            auth_service.authenticate(LoginRequest(email=test_email, password="Alumno123!"))
        assert "bloqueada temporalmente" in str(exc_info.value).lower()

        # 4. Desbloqueo y login exitoso: incremento de métricas
        u_check.locked_until = None
        u_check.failed_login_attempts = 0
        user_repo.update(u_check)

        res_ok = auth_service.authenticate(LoginRequest(email=test_email, password="Alumno123!"))
        assert res_ok is not None
        assert res_ok.user.login_count == 1
        assert res_ok.user.last_login_at is not None

        u_final = user_repo.get_by_email(test_email)
        assert u_final.failed_login_attempts == 0
        assert u_final.locked_until is None
        assert u_final.login_count == 1
        print("  [PASS] Bloqueo por fuerza bruta (5 fallos -> bloqueo 15m) y métricas de login validadas.")

def test_register_user_multi_tenant_flow():
    import uuid
    import pytest
    from core.database import SessionLocal
    from modules.auth.repository import UserRepository, TenantRepository
    from modules.auth.service import AuthService
    from models.schemas import RegisterRequest, UserRole

    with SessionLocal() as db:
        user_repo = UserRepository(db)
        tenant_repo = TenantRepository(db)
        auth_service = AuthService(user_repo, tenant_repo)

        # 1. Registro exitoso con dominio institucional UCE
        unique_suffix = uuid.uuid4().hex[:6]
        uce_email = f"estudiante_{unique_suffix}@uce.edu.ec"
        req = RegisterRequest(
            email=uce_email,
            password="PasswordSeguro2026!",
            nombre="Estudiante UCE Test",
            rol=UserRole.ALUMNO
        )
        res = auth_service.register_user(req)
        assert res.email == uce_email
        assert res.tenant_id == "tenant_uce"
        assert "Universidad Central del Ecuador" in res.mensaje

        # Verificar persistencia en base de datos
        saved = user_repo.get_by_email(uce_email)
        assert saved is not None
        assert saved.tenant_id == "tenant_uce"
        assert saved.activo is True
        assert saved.login_count == 0

        # 2. Intento de registro duplicado (debe lanzar ValueError)
        with pytest.raises(ValueError) as exc_dup:
            auth_service.register_user(req)
        assert "ya se encuentra registrado" in str(exc_dup.value).lower()

        # 3. Intento de registro con dominio no habilitado (debe lanzar LookupError)
        invalid_req = RegisterRequest(
            email="estudiante@gmail.com",
            password="PasswordSeguro2026!",
            nombre="Estudiante Gmail",
            rol=UserRole.ALUMNO
        )
        with pytest.raises(LookupError) as exc_tenant:
            auth_service.register_user(invalid_req)
        assert "no está habilitado" in str(exc_tenant.value).lower()

        # 4. Validación de contraseña débil en RegisterRequest (rechazo por Pydantic)
        with pytest.raises(Exception):
            RegisterRequest(
                email=f"debil_{unique_suffix}@uce.edu.ec",
                password="debil",  # Menos de 8 caracteres
                nombre="Usuario Débil"
            )

        print("  [PASS] Auto-registro multi-tenant, resolución por dominio y validaciones de unicidad validadas.")

def test_user_session_lifecycle_and_revocation():
    import pytest
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials
    from core.database import SessionLocal
    from modules.auth.repository import UserRepository, TenantRepository, UserSessionRepository
    from modules.auth.service import AuthService
    from models.schemas import LoginRequest
    from auth.security import get_current_user

    with SessionLocal() as db:
        user_repo = UserRepository(db)
        tenant_repo = TenantRepository(db)
        session_repo = UserSessionRepository(db)
        auth_service = AuthService(user_repo, tenant_repo, session_repo)

        # 1. Login institucional simulando IP y User-Agent
        client_ip = "192.168.10.50"
        client_ua = "AteneoMedicalClient/1.0 (Hospital General)"
        token_res = auth_service.authenticate(
            LoginRequest(email="alumno@ateneo.edu.ec", password="Alumno123!"),
            ip_address=client_ip,
            user_agent=client_ua
        )
        assert token_res is not None
        assert token_res.access_token is not None

        # 2. Decodificar token y comprobar claim jti
        payload = decode_access_token(token_res.access_token)
        jti = payload.get("jti")
        assert jti is not None, "El token debe incluir el claim jti"

        # 3. Comprobar persistencia de sesión activa en la base de datos
        session_record = session_repo.get_by_jti(jti)
        assert session_record is not None
        assert session_record.is_revoked is False
        assert session_record.ip_address == client_ip
        assert session_record.user_agent == client_ua

        # 4. Validar que get_current_user resuelve exitosamente con la sesión activa
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_res.access_token)
        resolved_user = get_current_user(credentials=creds, user_repo=user_repo, session_repo=session_repo)
        assert resolved_user.email == "alumno@ateneo.edu.ec"

        # 5. Ejecutar logout y revocar el jti
        revoked = auth_service.logout_session(jti)
        assert revoked is True
        assert session_repo.is_jti_revoked(jti) is True

        # 6. Intentar resolver usuario con el token revocado (debe disparar 401 Unauthorized)
        with pytest.raises(HTTPException) as exc_revoked:
            get_current_user(credentials=creds, user_repo=user_repo, session_repo=session_repo)
        assert exc_revoked.value.status_code == 401
        assert "revocada" in exc_revoked.value.detail.lower()

        print("  [PASS] Ciclo de vida de sesiones, persistencia JTI y revocación por logout validados.")

def test_accept_terms_and_legal_consent():
    """Valida la persistencia inmutable del consentimiento informado y LOPDP por usuario."""
    from core.database import SessionLocal
    from modules.auth.repository import UserRepository, TenantRepository, UserSessionRepository, MagicLinkRepository
    from modules.auth.service import AuthService
    from models.schemas import LoginRequest
    from fastapi.security import HTTPAuthorizationCredentials

    with SessionLocal() as db:
        user_repo = UserRepository(db)
        tenant_repo = TenantRepository(db)
        session_repo = UserSessionRepository(db)
        magic_repo = MagicLinkRepository(db)
        auth_service = AuthService(user_repo, tenant_repo, session_repo, magic_repo)
        auth_service.seed_demo_users_if_needed()

        # 1. Obtener usuario alumno y verificar aceptación de términos
        user_record = user_repo.get_by_email("alumno@ateneo.edu.ec")
        assert user_record is not None

        # 2. Registrar consentimiento informado
        version = "v1.0-test-investigacion-2026"
        res = auth_service.accept_terms(user_id=user_record.id, version_terminos=version)

        assert res.terminos_aceptados is True
        assert res.version_terminos == version
        assert res.fecha_terminos_aceptados is not None

        # 3. Validar persistencia real en base de datos
        db_user = user_repo.get_by_id(user_record.id)
        assert db_user.terminos_aceptados is True
        assert db_user.version_terminos == version
        assert db_user.fecha_terminos_aceptados is not None

        # 4. Validar resolución en get_current_user
        from auth.security import get_current_user
        token_res = auth_service.authenticate(
            LoginRequest(email="alumno@ateneo.edu.ec", password="Alumno123!")
        )
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_res.access_token)
        resolved = get_current_user(credentials=creds, user_repo=user_repo, session_repo=session_repo)
        assert resolved.terminos_aceptados is True
        assert resolved.version_terminos == version

        print("  [PASS] Persistencia de consentimiento legal e investigación validada.")

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" SUITE DE PRUEBAS UNITARIAS DE SEGURIDAD Y RBAC - ATENEO+")
    print("="*70)
    test_password_hashing()
    test_jwt_token_lifecycle()
    test_demo_users_database()
    test_brute_force_lockout_and_login_metrics()
    test_register_user_multi_tenant_flow()
    test_user_session_lifecycle_and_revocation()
    test_accept_terms_and_legal_consent()
    print("="*70)
    print(" TODAS LAS PRUEBAS DE SEGURIDAD PASARON (PASS)\n")

