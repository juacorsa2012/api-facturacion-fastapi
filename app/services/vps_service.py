from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET
from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.vps_exceptions import VpsNoEncontradoError
from app.models.cliente_model import Cliente
from app.models.enums import Estado
from app.models.vps_model import Vps
from app.schemas.vps_schema import VpsCreate, VpsUpdate


class VpsService:
  def __init__(self, db: AsyncSession) -> None:
    self.db = db

  async def obtener_por_id(self, vps_id: int) -> Vps:
    vps = await self.db.get(Vps, vps_id)
    if vps is None:
      raise VpsNoEncontradoError(vps_id)
    return vps

  async def obtener_todos(self, *, offset: int = DEFAULT_OFFSET, limit: int = DEFAULT_LIMIT, estado: Estado | None = None) -> list[Vps]:
    consulta = select(Vps).order_by(Vps.descripcion).offset(offset).limit(limit)
    if estado is not None:
      consulta = consulta.where(Vps.estado == estado)

    resultado = await self.db.scalars(consulta)
    return list(resultado.all())

  async def crear(self, datos: VpsCreate) -> Vps:
    existe_cliente = await self.db.scalar(select(Cliente.id).where(Cliente.id == datos.cliente_id))
    if existe_cliente is None:
      raise ClienteNoEncontradoError(datos.cliente_id)

    vps = Vps(**datos.model_dump())
    self.db.add(vps)
    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    return vps

  async def actualizar(self, vps_id: int, datos: VpsUpdate) -> Vps:
    vps = await self.obtener_por_id(vps_id)
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
      return vps

    cliente_id = cambios.get("cliente_id", vps.cliente_id)
    existe_cliente = await self.db.scalar(select(Cliente.id).where(Cliente.id == cliente_id))
    if existe_cliente is None:
      raise ClienteNoEncontradoError(cliente_id)

    for campo, valor in cambios.items():
      setattr(vps, campo, valor)

    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    return vps

  async def dar_de_baja(self, vps_id: int, motivo: str | None = None) -> Vps:
    vps = await self.obtener_por_id(vps_id)
    if vps.estado == Estado.BAJA:
      return vps

    vps.estado = Estado.BAJA
    vps.fecha_baja = datetime.now(timezone.utc)
    vps.motivo_baja = motivo
    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    return vps

  async def dar_de_alta(self, vps_id: int) -> Vps:
    vps = await self.obtener_por_id(vps_id)
    if vps.estado == Estado.ALTA:
      return vps

    vps.estado = Estado.ALTA
    vps.fecha_baja = None
    vps.motivo_baja = None
    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    return vps
