from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET
from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.hosting_exceptions import (
  HostingFechaRenovacionInvalidaError,
  HostingNoEncontradoError,
  HostingYaExisteError,
)
from app.models.cliente_model import Cliente
from app.models.enums import Estado
from app.models.hosting_model import Hosting
from app.schemas.hosting_schema import (
  HostingCreate,
  HostingUpdate,
  validar_dia_mes_renovacion,
)


def _constraint_name(exc: IntegrityError) -> str | None:
  """Obtiene el nombre de la restricción con asyncpg o psycopg."""
  original = exc.orig
  diagnostic = getattr(original, "diag", None)
  return (
    getattr(diagnostic, "constraint_name", None)
    or getattr(original, "constraint_name", None)
  )


class HostingService:
  def __init__(self, db: AsyncSession) -> None:
    self.db = db

  async def obtener_por_id(self, hosting_id: int) -> Hosting:
    hosting = await self.db.get(Hosting, hosting_id)
    if hosting is None:
      raise HostingNoEncontradoError(hosting_id)
    return hosting

  async def obtener_todos(
    self,
    *,
    offset: int = DEFAULT_OFFSET,
    limit: int = DEFAULT_LIMIT,
    estado: Estado | None = None,
  ) -> list[Hosting]:
    consulta = select(Hosting).order_by(Hosting.nombre).offset(offset).limit(limit)
    if estado is not None:
      consulta = consulta.where(Hosting.estado == estado)

    resultado = await self.db.scalars(consulta)
    return list(resultado.all())

  async def crear(self, datos: HostingCreate) -> Hosting:
    existe_cliente = await self.db.scalar(
      select(Cliente.id).where(Cliente.id == datos.cliente_id)
    )
    if existe_cliente is None:
      raise ClienteNoEncontradoError(datos.cliente_id)

    existe = await self.db.scalar(
      select(Hosting.id).where(Hosting.nombre == datos.nombre)
    )
    if existe is not None:
      raise HostingYaExisteError(datos.nombre)

    hosting = Hosting(**datos.model_dump())
    self.db.add(hosting)

    try:
      await self.db.commit()
    except IntegrityError as exc:
      await self.db.rollback()
      if _constraint_name(exc) == "hostings_nombre_key":
        raise HostingYaExisteError(datos.nombre) from exc
      raise

    return hosting

  async def actualizar(self, hosting_id: int, datos: HostingUpdate) -> Hosting:
    hosting = await self.obtener_por_id(hosting_id)
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
      return hosting

    dia_renovacion = cambios.get("dia_renovacion", hosting.dia_renovacion)
    mes_renovacion = cambios.get("mes_renovacion", hosting.mes_renovacion)
    try:
      validar_dia_mes_renovacion(dia_renovacion, mes_renovacion)
    except ValueError as exc:
      raise HostingFechaRenovacionInvalidaError(dia_renovacion, mes_renovacion) from exc

    cliente_id = cambios.get("cliente_id", hosting.cliente_id)
    existe_cliente = await self.db.scalar(
      select(Cliente.id).where(Cliente.id == cliente_id)
    )
    if existe_cliente is None:
      raise ClienteNoEncontradoError(cliente_id)

    nombre = cambios.get("nombre", hosting.nombre)
    if nombre != hosting.nombre:
      id_existente = await self.db.scalar(
        select(Hosting.id).where(
          Hosting.nombre == nombre,
          Hosting.id != hosting_id,
        )
      )
      if id_existente is not None:
        raise HostingYaExisteError(nombre)

    for campo, valor in cambios.items():
      setattr(hosting, campo, valor)

    try:
      await self.db.commit()
    except IntegrityError as exc:
      await self.db.rollback()
      if _constraint_name(exc) == "hostings_nombre_key":
        raise HostingYaExisteError(nombre) from exc
      raise

    return hosting

  async def dar_de_baja(self, hosting_id: int, motivo: str | None = None) -> Hosting:
    hosting = await self.obtener_por_id(hosting_id)
    if hosting.estado == Estado.BAJA:
      return hosting

    hosting.estado = Estado.BAJA
    hosting.fecha_baja = datetime.now(timezone.utc)
    hosting.motivo_baja = motivo
    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    return hosting

  async def dar_de_alta(self, hosting_id: int) -> Hosting:
    hosting = await self.obtener_por_id(hosting_id)
    if hosting.estado == Estado.ALTA:
      return hosting

    hosting.estado = Estado.ALTA
    hosting.fecha_baja = None
    hosting.motivo_baja = None
    try:
      await self.db.commit()
    except Exception:
      await self.db.rollback()
      raise
    return hosting
