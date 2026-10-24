from decimal import Decimal

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente_model import Cliente
from app.models.dominio_model import Dominio
from app.schemas.dominio_schema import DominioCreate
from app.services.dominio_service import DominioService


async def seed_dominios(db: AsyncSession, cantidad: int = 10) -> int:
  """Genera dominios ficticios y los asocia a clientes existentes."""
  if cantidad < 0:
    raise ValueError("La cantidad de dominios no puede ser negativa")

  clientes = list((await db.scalars(select(Cliente).order_by(Cliente.id))).all())
  if cantidad and not clientes:
    raise ValueError("No hay clientes para asociar dominios; genera clientes primero")

  faker = Faker("es_ES")
  service = DominioService(db)
  creados = 0

  while creados < cantidad:
    nombre = faker.unique.domain_name().lower()
    existente = await db.scalar(
      select(Dominio.id).where(Dominio.nombre == nombre)
    )
    if existente is not None:
      continue

    fecha = faker.date_object()
    datos = DominioCreate(
      cliente_id=faker.random_element(clientes).id,
      nombre=nombre,
      dia_renovacion=fecha.day,
      mes_renovacion=fecha.month,
      precio=Decimal(str(faker.pydecimal(left_digits=3, right_digits=2, positive=True))),
    )
    await service.crear(datos)
    creados += 1

  return creados
