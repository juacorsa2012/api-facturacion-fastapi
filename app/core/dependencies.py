from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.cliente_service import ClienteService
from app.services.dominio_service import DominioService
from app.services.hosting_service import HostingService
from app.services.vps_service import VpsService

def get_cliente_service(db: AsyncSession = Depends(get_db_session)) -> ClienteService:
  return ClienteService(db)

def get_dominio_service(db: AsyncSession = Depends(get_db_session)) -> DominioService:
  return DominioService(db)

def get_hosting_service(db: AsyncSession = Depends(get_db_session)) -> HostingService:
  return HostingService(db)

def get_vps_service(db: AsyncSession = Depends(get_db_session)) -> VpsService:
  return VpsService(db)

ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]
DominioServiceDep = Annotated[DominioService, Depends(get_dominio_service)]
HostingServiceDep = Annotated[HostingService, Depends(get_hosting_service)]
VpsServiceDep = Annotated[VpsService, Depends(get_vps_service)]

