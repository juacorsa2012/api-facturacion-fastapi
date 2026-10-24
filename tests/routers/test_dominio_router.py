from decimal import Decimal

import pytest

from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.dominio_exceptions import (
  DominioFechaRenovacionInvalidaError,
  DominioNoEncontradoError,
  DominioYaExisteError,
)
from app.models.enums import Ciclo, Estado, FormaPago, Vencimiento
from app.schemas.cliente_schema import ClienteCreate
from app.schemas.dominio_schema import DominioCreate, DominioUpdate
from app.services.cliente_service import ClienteService
from app.services.dominio_service import DominioService


def datos_cliente(nombre_corto: str = "CLIENTE") -> ClienteCreate:
  return ClienteCreate(
    nombre_corto=nombre_corto,
    nombre_largo=f"{nombre_corto} S.L.",
    direccion="Calle Mayor 1",
    codigo_postal="46001",
    poblacion="Valencia",
    cif="B12345678",
  )


async def crear_cliente(db, nombre_corto: str = "CLIENTE"):
  return await ClienteService(db).crear(datos_cliente(nombre_corto))


def datos_dominio(cliente_id: int, nombre: str = "ejemplo.com", **extra) -> DominioCreate:
  valores = {
    "cliente_id": cliente_id,
    "nombre": nombre,
    "dia_renovacion": 15,
    "mes_renovacion": 6,
  }
  return DominioCreate(**{**valores, **extra})


@pytest.fixture
def service(db):
  return DominioService(db)


async def test_crear_asigna_valores_por_defecto(service, db):
  cliente = await crear_cliente(db)

  dominio = await service.crear(datos_dominio(cliente.id, nombre="WWW.EJEMPLO.COM"))

  assert dominio.id is not None
  assert dominio.cliente_id == cliente.id
  assert dominio.nombre == "www.ejemplo.com"
  assert dominio.precio == Decimal("19.90")
  assert dominio.ciclo == Ciclo.ANUAL
  assert dominio.forma_pago == FormaPago.RECIBO
  assert dominio.vencimiento == Vencimiento.UN_MES
  assert dominio.estado == Estado.ALTA
  assert dominio.created_at is not None
  assert dominio.updated_at is not None


async def test_crear_cliente_inexistente(service):
  with pytest.raises(ClienteNoEncontradoError):
    await service.crear(datos_dominio(999999))


async def test_crear_dominio_duplicado(service, db):
  cliente = await crear_cliente(db)
  await service.crear(datos_dominio(cliente.id, nombre="ejemplo.com"))

  with pytest.raises(DominioYaExisteError):
    await service.crear(datos_dominio(cliente.id, nombre="EJEMPLO.COM"))


async def test_obtener_por_id_inexistente(service):
  with pytest.raises(DominioNoEncontradoError):
    await service.obtener_por_id(999999)


async def test_obtener_todos_filtra_ordena_y_pagina(service, db):
  cliente = await crear_cliente(db)
  for nombre in ("c.ejemplo.com", "a.ejemplo.com", "b.ejemplo.com"):
    await service.crear(datos_dominio(cliente.id, nombre=nombre))

  dominio_a = (await service.obtener_todos())[0]
  await service.dar_de_baja(dominio_a.id)

  todos = await service.obtener_todos()
  assert [dominio.nombre for dominio in todos] == [
    "a.ejemplo.com",
    "b.ejemplo.com",
    "c.ejemplo.com",
  ]

  en_alta = await service.obtener_todos(estado=Estado.ALTA)
  assert [dominio.nombre for dominio in en_alta] == ["b.ejemplo.com", "c.ejemplo.com"]

  pagina = await service.obtener_todos(offset=1, limit=1)
  assert [dominio.nombre for dominio in pagina] == ["b.ejemplo.com"]


async def test_actualizar_cambia_solo_lo_enviado(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))

  actualizado = await service.actualizar(dominio.id, DominioUpdate(precio=Decimal("25.00")))

  assert actualizado.precio == Decimal("25.00")
  assert actualizado.nombre == "ejemplo.com"
  assert actualizado.dia_renovacion == 15
  assert actualizado.mes_renovacion == 6


async def test_actualizar_sin_cambios_no_modifica_dominio(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))
  fecha_actualizacion = dominio.updated_at

  resultado = await service.actualizar(dominio.id, DominioUpdate())

  assert resultado.updated_at == fecha_actualizacion


async def test_actualizar_a_nombre_existente_lanza_error(service, db):
  cliente = await crear_cliente(db)
  await service.crear(datos_dominio(cliente.id, nombre="existente.com"))
  otro = await service.crear(datos_dominio(cliente.id, nombre="otro.com"))

  with pytest.raises(DominioYaExisteError):
    await service.actualizar(otro.id, DominioUpdate(nombre="existente.com"))


async def test_actualizar_a_mismo_nombre_no_es_conflicto(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))

  actualizado = await service.actualizar(dominio.id, DominioUpdate(nombre="EJEMPLO.COM"))

  assert actualizado.nombre == "ejemplo.com"


async def test_actualizar_cliente_inexistente_lanza_error(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))

  with pytest.raises(ClienteNoEncontradoError):
    await service.actualizar(dominio.id, DominioUpdate(cliente_id=999999))


async def test_actualizar_fecha_renovacion_invalida_lanza_error(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id, mes_renovacion=4))

  with pytest.raises(DominioFechaRenovacionInvalidaError):
    await service.actualizar(dominio.id, DominioUpdate(dia_renovacion=31))


async def test_dar_de_baja_y_alta(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))

  baja = await service.dar_de_baja(dominio.id, motivo="impago")
  assert baja.estado == Estado.BAJA
  assert baja.fecha_baja is not None
  assert baja.motivo_baja == "impago"

  alta = await service.dar_de_alta(dominio.id)
  assert alta.estado == Estado.ALTA
  assert alta.fecha_baja is None
  assert alta.motivo_baja is None


async def test_dar_de_baja_es_idempotente(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))
  primera = await service.dar_de_baja(dominio.id, motivo="impago")
  fecha_baja = primera.fecha_baja

  segunda = await service.dar_de_baja(dominio.id, motivo="otro motivo")

  assert segunda.fecha_baja == fecha_baja
  assert segunda.motivo_baja == "impago"


async def test_dar_de_alta_es_idempotente(service, db):
  cliente = await crear_cliente(db)
  dominio = await service.crear(datos_dominio(cliente.id))

  resultado = await service.dar_de_alta(dominio.id)

  assert resultado.estado == Estado.ALTA
  assert resultado.fecha_baja is None
  assert resultado.motivo_baja is None
