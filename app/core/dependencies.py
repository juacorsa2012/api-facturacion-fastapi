from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.cliente_service import ClienteService

def get_cliente_service(db: AsyncSession = Depends(get_db_session)) -> ClienteService:
  return ClienteService(db)


ClienteServiceDep = Annotated[ClienteService, Depends(get_cliente_service)]

