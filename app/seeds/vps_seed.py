from decimal import Decimal

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente_model import Cliente
from app.models.vps_model import Vps
from app.schemas.vps_schema import VpsCreate
from app.services.vps_service import VpsService


async def seed_vps(db: AsyncSession, cantidad: int = 10) -> int:
  """Genera VPS ficticios y los asocia a clientes existentes."""
  if cantidad < 0:
    raise ValueError("La cantidad de VPS no puede ser negativa")

  clientes = list((await db.scalars(select(Cliente).order_by(Cliente.id))).all())
  if cantidad and not clientes:
    raise ValueError("No hay clientes para asociar VPS; genera clientes primero")

  faker = Faker("es_ES")
  service = VpsService(db)

  for _ in range(cantidad):
    datos = VpsCreate(
      cliente_id=faker.random_element(clientes).id,
      descripcion=faker.sentence(nb_words=4).rstrip(".")[:100],
      dia_renovacion=faker.random_int(min=1, max=31),
      precio=Decimal(str(faker.pydecimal(left_digits=3, right_digits=2, positive=True))),
      domiciliacion=faker.iban(),
      info_adicional=faker.text(max_nb_chars=300),
    )
    await service.crear(datos)

  return cantidad
