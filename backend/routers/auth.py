from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from fastapi.security import HTTPAuthorizationCredentials
from typing import List
from models.schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    UserRole,
    RegisterRequest,
    RegisterResponse,
    MagicLinkCreateRequest,
    MagicLinkBatchCreateRequest,
    MagicLinkResponse,
    MagicLinkConsumeRequest,
    MagicLinkConsumeResponse,
    MagicLinkVerifyResponse,
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


@router.post("/magic-links", response_model=MagicLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_magic_link(
    req: MagicLinkCreateRequest,
    request: Request,
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Genera un Magic Link de acceso seguro e invitación configurable con hash SHA-256.
    Exclusivo para el rol de Administrador.
    """
    try:
        # Resolver base URL del frontend desde req.base_url, headers o fallback
        origin = request.headers.get("origin") or request.headers.get("referer")
        detected_url = origin.split("?")[0].rstrip("/") if origin else "http://localhost:5174"
        effective_base_url = req.base_url.rstrip("/") if req.base_url else detected_url

        return auth_service.create_magic_link(
            admin_user_id=current_user.id,
            admin_tenant_id=current_user.tenant_id,
            req=req,
            base_frontend_url=effective_base_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al generar el Magic Link: {str(e)}"
        )


@router.post("/magic-links/batch", response_model=List[MagicLinkResponse], status_code=status.HTTP_201_CREATED)
async def create_magic_links_batch(
    req: MagicLinkBatchCreateRequest,
    request: Request,
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Genera atómicamente un lote completo de Magic Links con nombres correlativos e identidades provisionadas.
    """
    try:
        origin = request.headers.get("origin") or request.headers.get("referer")
        detected_url = origin.split("?")[0].rstrip("/") if origin else "http://localhost:5174"
        effective_base_url = req.base_url.rstrip("/") if req.base_url else detected_url

        return auth_service.create_magic_links_batch(
            admin_user_id=current_user.id,
            admin_tenant_id=current_user.tenant_id,
            req=req,
            base_frontend_url=effective_base_url
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al generar el lote de Magic Links: {str(e)}"
        )


@router.get("/magic-links", response_model=List[MagicLinkResponse])
async def list_magic_links(
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Lista los Magic Links generados en el tenant para auditoría y control de vigencia.
    """
    return auth_service.list_magic_links(tenant_id=current_user.tenant_id)


@router.delete("/magic-links/{link_id}", status_code=status.HTTP_200_OK)
async def revoke_magic_link(
    link_id: str,
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Invalida un Magic Link en caliente impidiendo futuros canjes.
    """
    success = auth_service.revoke_magic_link(link_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Magic Link no encontrado para revocación."
        )
    return {"mensaje": "Magic Link revocado exitosamente"}


@router.delete("/magic-links/{link_id}/purge", status_code=status.HTTP_200_OK)
async def purge_magic_link(
    link_id: str,
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Elimina físicamente un Magic Link revocado o agotado de la base de datos para mantener el historial limpio.
    """
    success = auth_service.delete_magic_link(link_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Magic Link no encontrado para eliminación."
        )
    return {"mensaje": "Magic Link eliminado definitivamente"}


@router.post("/magic-links/purge-revoked", status_code=status.HTTP_200_OK)
async def purge_revoked_magic_links(
    current_user: UserResponse = Depends(require_roles([UserRole.ADMINISTRADOR])),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Limpia en lote todos los Magic Links revocados en el tenant.
    """
    deleted_count = auth_service.purge_revoked_magic_links(tenant_id=current_user.tenant_id)
    return {"mensaje": f"Se eliminaron {deleted_count} enlaces revocados", "eliminados": deleted_count}


@router.get("/magic-links/verify", response_model=MagicLinkVerifyResponse)
async def verify_magic_link(
    token: str = Query(..., description="Token del Magic Link para verificación previa"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verifica los metadatos y validez de un Magic Link antes de su canje para mostrar la pantalla de confirmación.
    """
    try:
        return auth_service.verify_magic_link(token)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar el enlace: {str(e)}"
        )


@router.post("/magic-links/consume", response_model=MagicLinkConsumeResponse)
async def consume_magic_link(
    req: MagicLinkConsumeRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Canjea un Magic Link público, autentica o aprovisiona al participante y emite un token JWT.
    """
    try:
        forwarded = request.headers.get("x-forwarded-for")
        cf_ip = request.headers.get("cf-connecting-ip")
        real_ip = request.headers.get("x-real-ip")
        raw_ip = cf_ip or (forwarded.split(",")[0].strip() if forwarded else None) or real_ip or (request.client.host if request.client else None)
        client_ip = raw_ip[:45] if raw_ip else None
        user_agent = request.headers.get("user-agent")

        return auth_service.consume_magic_link(
            req=req,
            ip_address=client_ip,
            user_agent=user_agent
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al canjear el Magic Link: {str(e)}"
        )

