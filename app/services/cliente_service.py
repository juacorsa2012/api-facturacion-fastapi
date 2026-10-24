from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET
from app.exceptions.cliente_exceptions import ClienteYaExisteError, ClienteNoEncontradoError
from app.models.cliente_model import Cliente
from app.models.enums import Estado
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate


class ClienteService:
  def __init__(self, db: AsyncSession) -> None:
    self.db = db

  async def obtener_por_id(self, cliente_id: int) -> Cliente:   
    cliente = await self.db.get(Cliente, cliente_id)
  
    if cliente is None:
      raise ClienteNoEncontradoError(cliente_id)
  
    return cliente

  
  async def obtener_todos(self, *, offset: int = DEFAULT_OFFSET, limit: int = DEFAULT_LIMIT, estado: Estado | None = None) -> list[Cliente]:
    consulta = select(Cliente).order_by(Cliente.nombre_corto).offset(offset).limit(limit)

    if estado is not None:
      consulta = consulta.where(Cliente.estado == estado)

    resultado = await self.db.scalars(consulta)
    return list(resultado.all())

  
  async def crear(self, datos: ClienteCreate) -> Cliente:
    existe = await self.db.scalar(
      select(Cliente.id).where(
        Cliente.nombre_corto == datos.nombre_corto
      )
    )

    if existe is not None:
      raise ClienteYaExisteError(datos.nombre_corto)

    cliente = Cliente(**datos.model_dump())
    self.db.add(cliente)

    try:
      await self.db.commit()
    except IntegrityError as exc:
      await self.db.rollback()

      diagnostico = getattr(exc.orig, "diag", None)
      restriccion = getattr(diagnostico, "constraint_name", None)

      if restriccion == "clientes_nombre_corto_key":
        raise ClienteYaExisteError(datos.nombre_corto) from exc

      raise
    
    return cliente

  async def actualizar(self, cliente_id: int, datos: ClienteUpdate) -> Cliente:
    cliente = await self.obtener_por_id(cliente_id)
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
      return cliente

    nombre_corto = cambios.get("nombre_corto", cliente.nombre_corto)

    if nombre_corto != cliente.nombre_corto:
      id_existente = await self.db.scalar(
        select(Cliente.id).where(
          Cliente.nombre_corto == nombre_corto,
          Cliente.id != cliente_id,
        )
      )

      if id_existente is not None:
        raise ClienteYaExisteError(nombre_corto)

    for campo, valor in cambios.items():
      setattr(cliente, campo, valor)

    try:
      await self.db.commit()
    except IntegrityError as exc:
      await self.db.rollback()

      diagnostico = getattr(exc.orig, "diag", None)
      nombre_restriccion = getattr(diagnostico, "constraint_name", None)

      if nombre_restriccion == "clientes_nombre_corto_key":
        raise ClienteYaExisteError(nombre_corto) from exc

      raise

    return cliente

  async def dar_de_baja(self, cliente_id: int, motivo: str | None = None) -> Cliente:
    cliente = await self.obtener_por_id(cliente_id)

    if cliente.estado == Estado.BAJA:
      return cliente

    cliente.estado = Estado.BAJA
    cliente.fecha_baja = datetime.now(timezone.utc)
    cliente.motivo_baja = motivo

    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    
    return cliente

  async def dar_de_alta(self, cliente_id: int) -> Cliente:
    cliente = await self.obtener_por_id(cliente_id)

    if cliente.estado == Estado.ALTA:
      return cliente

    cliente.estado = Estado.ALTA
    cliente.fecha_baja = None
    cliente.motivo_baja = None

    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise

    return cliente
