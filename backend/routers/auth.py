from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
from models.schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserRole,
    RegisterRequest,
    RegisterResponse,
)
from auth.security import get_current_user, require_roles, security_scheme, decode_access_token
from modules.auth.dependencies import get_auth_service
from modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.register_user(req)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado en el registro: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest, 
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        # Resolución robusta y agnóstica de proxy para IP del cliente
        forwarded = request.headers.get("x-forwarded-for")
        cf_ip = request.headers.get("cf-connecting-ip")
        real_ip = request.headers.get("x-real-ip")
        raw_ip = cf_ip or (forwarded.split(",")[0].strip() if forwarded else None) or real_ip or (request.client.host if request.client else None)
        client_ip = raw_ip[:45] if raw_ip else None

        user_agent = request.headers.get("user-agent")
        result = auth_service.authenticate(req, ip_address=client_ip, user_agent=user_agent)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo electrónico o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return result
    except PermissionError as e:
        error_msg = str(e)
        if "bloqueada" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_msg
        )

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Revoca la sesión activa en el servidor marcando el claim criptográfico JTI como revocado,
    impidiendo cualquier reutilización del token JWT portador.
    Tolera tokens expirados para garantizar revocación idempotente y limpia en el cliente.
    """
    payload = decode_access_token(credentials.credentials, verify_exp=False)
    jti = payload.get("jti")
    if jti:
        auth_service.logout_session(jti)
    return {"mensaje": "Sesión cerrada y token revocado exitosamente"}



@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.list_users()
