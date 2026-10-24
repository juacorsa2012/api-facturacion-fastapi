from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET
from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.dominio_exceptions import (
  DominioFechaRenovacionInvalidaError,
  DominioNoEncontradoError,
  DominioYaExisteError,
)
from app.models.cliente_model import Cliente
from app.models.dominio_model import Dominio
from app.models.enums import Estado
from app.schemas.dominio_schema import DominioCreate, DominioUpdate, validar_dia_mes_renovacion

class DominioService:
  def __init__(self, db: AsyncSession) -> None:
    self.db = db

  async def obtener_por_id(self, dominio_id: int) -> Dominio:   
    dominio = await self.db.get(Dominio, dominio_id)
    
    if dominio is None:
      raise DominioNoEncontradoError(dominio_id)
    
    return dominio

  async def obtener_todos(self, *, offset: int = DEFAULT_OFFSET, limit: int = DEFAULT_LIMIT, estado: Estado | None = None) -> list[Dominio]:
    consulta = select(Dominio).order_by(Dominio.nombre).offset(offset).limit(limit)

    if estado is not None:
      consulta = consulta.where(Dominio.estado == estado)

    resultado = await self.db.scalars(consulta)
    return list(resultado.all())

  async def crear(self, datos: DominioCreate) -> Dominio:
    existe_cliente = await self.db.scalar(select(Cliente.id).where(Cliente.id == datos.cliente_id))

    if existe_cliente is None:
      raise ClienteNoEncontradoError(datos.cliente_id)

    existe = await self.db.scalar(select(Dominio.id).where(Dominio.nombre == datos.nombre))
                                  
    if existe is not None:
      raise DominioYaExisteError(datos.nombre)
  
    dominio = Dominio(**datos.model_dump())
    self.db.add(dominio)
  
    try:
      await self.db.commit()
    except IntegrityError as exc:
      await self.db.rollback()  
      diagnostico = getattr(exc.orig, "diag", None)
      restriccion = getattr(diagnostico, "constraint_name", None)
  
      if restriccion == "dominios_nombre_key":
        raise DominioYaExisteError(datos.nombre) from exc
  
      raise
      
    return dominio

  async def actualizar(self, dominio_id: int, datos: DominioUpdate) -> Dominio:
    dominio = await self.obtener_por_id(dominio_id)
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
      return dominio

    dia_renovacion = cambios.get("dia_renovacion", dominio.dia_renovacion)
    mes_renovacion = cambios.get("mes_renovacion", dominio.mes_renovacion)
    try:
      validar_dia_mes_renovacion(dia_renovacion, mes_renovacion)
    except ValueError as exc:
      raise DominioFechaRenovacionInvalidaError(dia_renovacion, mes_renovacion) from exc

    cliente_id = cambios.get("cliente_id", dominio.cliente_id)
    existe_cliente = await self.db.scalar(select(Cliente.id).where(Cliente.id == cliente_id))
    
    if existe_cliente is None:
      raise ClienteNoEncontradoError(cliente_id)

    nombre = cambios.get("nombre", dominio.nombre)
    if nombre != dominio.nombre:
      id_existente = await self.db.scalar(
        select(Dominio.id).where(
          Dominio.nombre == nombre,
          Dominio.id != dominio_id,
        )
      )
      if id_existente is not None:
        raise DominioYaExisteError(nombre)

    for campo, valor in cambios.items():
      setattr(dominio, campo, valor)

    try:
      await self.db.commit()
    except IntegrityError as exc:
      await self.db.rollback()

      diagnostico = getattr(exc.orig, "diag", None)
      restriccion = getattr(diagnostico, "constraint_name", None)

      if restriccion == "dominios_nombre_key":
        raise DominioYaExisteError(nombre) from exc

      raise

    return dominio

  async def dar_de_baja(self, dominio_id: int, motivo: str | None = None) -> Dominio:
    dominio = await self.obtener_por_id(dominio_id)

    if dominio.estado == Estado.BAJA:
      return dominio

    dominio.estado = Estado.BAJA
    dominio.fecha_baja = datetime.now(timezone.utc)
    dominio.motivo_baja = motivo

    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise

    return dominio

  async def dar_de_alta(self, dominio_id: int) -> Dominio:
    dominio = await self.obtener_por_id(dominio_id)

    if dominio.estado == Estado.ALTA:
      return dominio

    dominio.estado = Estado.ALTA
    dominio.fecha_baja = None
    dominio.motivo_baja = None

    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise

    return dominio
