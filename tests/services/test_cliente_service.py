import pytest

from app.exceptions.cliente_exceptions import ClienteNoEncontradoError, ClienteYaExisteError
from app.models.enums import Estado
from app.schemas.cliente_schema import ClienteCreate, ClienteUpdate
from app.services.cliente_service import ClienteService

# cls; pytest tests -v

def datos(nombre_corto: str = "A", **extra) -> ClienteCreate:
  base = dict(
    nombre_corto=nombre_corto,
    nombre_largo=f"{nombre_corto} S.L.",
    direccion="Calle Mayor 1",
    codigo_postal="46001",
    poblacion="Valencia",
    cif="B12345678",
  )
  return ClienteCreate(**{**base, **extra})

@pytest.fixture
def service(db):
  return ClienteService(db)

async def test_crear_asigna_valores_por_defecto(service):
  cliente = await service.crear(datos())

  assert cliente.id is not None
  assert cliente.estado == Estado.ALTA
  assert cliente.created_at is not None
  assert cliente.updated_at is not None

async def test_crear_duplicado_lanza_error_de_dominio(service):
  await service.crear(datos("A"))

  with pytest.raises(ClienteYaExisteError):
    await service.crear(datos("A"))

async def test_obtener_por_id_inexistente(service):
  with pytest.raises(ClienteNoEncontradoError):
    await service.obtener_por_id(999_999)


async def test_actualizar_cambia_solo_lo_enviado(service):
  cliente = await service.crear(datos())

  actualizado = await service.actualizar(cliente.id, ClienteUpdate(poblacion="Sagunto"))

  assert actualizado.poblacion == "Sagunto"
  assert actualizado.direccion == "Calle Mayor 1"


async def test_actualizar_sin_cambios_no_toca_nada(service):
  cliente = await service.crear(datos())
  antes = cliente.updated_at

  resultado = await service.actualizar(cliente.id, ClienteUpdate())

  assert resultado.updated_at == antes


async def test_actualizar_a_nombre_corto_existente(service):
  await service.crear(datos("a"))
  otro = await service.crear(datos("otro"))

  with pytest.raises(ClienteYaExisteError):
    await service.actualizar(otro.id, ClienteUpdate(nombre_corto="a"))


async def test_actualizar_mismo_nombre_corto_no_es_conflicto(service):
  cliente = await service.crear(datos("a"))

  resultado = await service.actualizar(cliente.id, ClienteUpdate(nombre_corto="a"))

  assert resultado.nombre_corto == cliente.nombre_corto


async def test_dar_de_baja_y_alta(service):
  cliente = await service.crear(datos())

  baja = await service.dar_de_baja(cliente.id, motivo="impago")
  assert baja.estado == Estado.BAJA
  assert baja.fecha_baja is not None
  assert baja.motivo_baja == "impago"

  alta = await service.dar_de_alta(cliente.id)
  assert alta.estado == Estado.ALTA
  assert alta.fecha_baja is None
  assert alta.motivo_baja is None


async def test_dar_de_baja_es_idempotente(service):
  cliente = await service.crear(datos())
  primera = await service.dar_de_baja(cliente.id, motivo="impago")
  fecha = primera.fecha_baja

  segunda = await service.dar_de_baja(cliente.id, motivo="otro motivo")

  assert segunda.fecha_baja == fecha
  assert segunda.motivo_baja == "impago"


async def test_obtener_todos_filtra_ordena_y_pagina(service):
  for nombre in ("c", "a", "b"):
    await service.crear(datos(nombre))
  
  await service.dar_de_baja((await service.obtener_todos())[0].id)  # baja a "a"

  todos = await service.obtener_todos()
  assert [c.nombre_corto for c in todos] == ["A", "B", "C"]

  en_alta = await service.obtener_todos(estado=Estado.ALTA)
  assert [c.nombre_corto for c in en_alta] == ["B", "C"]

  pagina = await service.obtener_todos(offset=1, limit=1)
  assert [c.nombre_corto for c in pagina] == ["B"]