from decimal import Decimal

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente_model import Cliente
from app.models.hosting_model import Hosting
from app.schemas.hosting_schema import HostingCreate
from app.services.hosting_service import HostingService


async def seed_hostings(db: AsyncSession, cantidad: int = 10) -> int:
  """Genera hostings ficticios y los asocia a clientes existentes."""
  if cantidad < 0:
    raise ValueError("La cantidad de hostings no puede ser negativa")

  clientes = list((await db.scalars(select(Cliente).order_by(Cliente.id))).all())
  if cantidad and not clientes:
    raise ValueError("No hay clientes para asociar hostings; genera clientes primero")

  faker = Faker("es_ES")
  service = HostingService(db)
  creados = 0

  while creados < cantidad:
    nombre = faker.unique.domain_name().lower()
    existente = await db.scalar(
      select(Hosting.id).where(Hosting.nombre == nombre)
    )
    if existente is not None:
      continue

    fecha = faker.date_object()
    datos = HostingCreate(
      cliente_id=faker.random_element(clientes).id,
      nombre=nombre,
      dia_renovacion=fecha.day,
      mes_renovacion=fecha.month,
      precio=Decimal(str(faker.pydecimal(left_digits=3, right_digits=2, positive=True))),
      info_adicional=faker.text(max_nb_chars=300),
    )
    await service.crear(datos)
    creados += 1

  return creados
