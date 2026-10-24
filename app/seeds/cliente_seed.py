from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteCreate
from app.services.cliente_service import ClienteService


async def seed_clientes(db: AsyncSession, cantidad: int = 10) -> int:
  """Genera e inserta la cantidad indicada de clientes ficticios."""
  if cantidad < 0:
    raise ValueError("La cantidad de clientes no puede ser negativa")

  faker = Faker("es_ES")
  service = ClienteService(db)
  creados = 0

  while creados < cantidad:
    nombre_corto = f"CLIENTE-{faker.unique.random_number(digits=8, fix_len=True)}"
    existente = await db.scalar(
      select(Cliente.id).where(Cliente.nombre_corto == nombre_corto)
    )
    if existente is not None:
      continue

    datos = ClienteCreate(
      nombre_corto=nombre_corto,
      nombre_largo=faker.company(),
      direccion=faker.street_address(),
      codigo_postal=faker.postcode(),
      poblacion=faker.city(),
      cif=faker.bothify(text="B########"),
      email=faker.safe_email(),
    )
    await service.crear(datos)
    creados += 1

  return creados


# uv run python -m app.seeds --cantidad 50
