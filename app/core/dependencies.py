from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.cliente_service import ClienteService
from app.services.dominio_service import DominioService
from app.services.hosting_service import HostingService
from app.services.auth_service import AuthService
from app.services.vps_service import VpsService
from app.models.usuario_model import Usuario
from app.core.exceptions import TokenInvalido
from app.core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

def get_cliente_service(db: AsyncSession = Depends(get_db_session)) -> ClienteService:
  return ClienteService(db)

def get_dominio_service(db: AsyncSession = Depends(get_db_session)) -> DominioService:
  return DominioService(db)

def get_hosting_service(db: AsyncSession = Depends(get_db_session)) -> HostingService:
  return HostingService(db)

def get_vps_service(db: AsyncSession = Depends(get_db_session)) -> VpsService:
  return VpsService(db)

def get_auth_service(db: AsyncSession = Depends(get_db_session)) -> AuthService:
  return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

async def usuario_actual(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    service: AuthServiceDep,
) -> Usuario:
    if credenciales is None:
      raise TokenInvalido()

    payload = decode_access_token(credenciales.credentials)
    if payload is None:
      raise TokenInvalido()

    try:
      usuario_id = int(payload["sub"])
    except (KeyError, ValueError):
      raise TokenInvalido()

    usuario = await service.obtener_por_id(usuario_id)
    if usuario is None:
      raise TokenInvalido()

    return usuario

ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]
DominioServiceDep = Annotated[DominioService, Depends(get_dominio_service)]
HostingServiceDep = Annotated[HostingService, Depends(get_hosting_service)]
VpsServiceDep = Annotated[VpsService, Depends(get_vps_service)]
UsuarioActualDep = Annotated[Usuario, Depends(usuario_actual)]