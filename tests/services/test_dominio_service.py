from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.dominio_exceptions import (
  DominioFechaRenovacionInvalidaError,
  DominioNoEncontradoError,
  DominioYaExisteError,
)
from app.models.enums import Estado
from app.schemas.dominio_schema import DominioCreate, DominioUpdate
from app.services.dominio_service import DominioService


@pytest.fixture
def db():
  return SimpleNamespace(
    get=AsyncMock(),
    scalar=AsyncMock(),
    scalars=AsyncMock(),
    add=MagicMock(),
    commit=AsyncMock(),
    rollback=AsyncMock(),
  )


@pytest.fixture
def service(db):
  return DominioService(db)


def datos_dominio(**cambios) -> DominioCreate:
  valores = {
    "cliente_id": 1,
    "nombre": "ejemplo.com",
    "dia_renovacion": 15,
    "mes_renovacion": 6,
  }
  return DominioCreate(**{**valores, **cambios})


def dominio_falso(**cambios):
  valores = {
    "id": 10,
    "cliente_id": 1,
    "nombre": "ejemplo.com",
    "dia_renovacion": 15,
    "mes_renovacion": 6,
    "estado": Estado.ALTA,
    "fecha_baja": None,
    "motivo_baja": None,
    "precio": 19.90,
  }
  return SimpleNamespace(**{**valores, **cambios})


async def test_obtener_por_id_devuelve_dominio(service, db):
  dominio = dominio_falso()
  db.get.return_value = dominio

  resultado = await service.obtener_por_id(dominio.id)

  assert resultado is dominio
  db.get.assert_awaited_once()


async def test_obtener_por_id_inexistente_lanza_error(service, db):
  db.get.return_value = None

  with pytest.raises(DominioNoEncontradoError):
    await service.obtener_por_id(999)


async def test_obtener_todos_devuelve_resultados(service, db):
  dominios = [dominio_falso(id=1), dominio_falso(id=2, nombre="otro.com")]
  resultado_db = MagicMock()
  resultado_db.all.return_value = dominios
  db.scalars.return_value = resultado_db

  resultado = await service.obtener_todos(offset=1, limit=2, estado=Estado.ALTA)

  assert resultado == dominios
  db.scalars.assert_awaited_once()


async def test_crear_cliente_inexistente_lanza_error(service, db):
  db.scalar.return_value = None

  with pytest.raises(ClienteNoEncontradoError):
    await service.crear(datos_dominio())

  db.add.assert_not_called()
  db.commit.assert_not_awaited()


async def test_crear_nombre_existente_lanza_error(service, db):
  db.scalar.side_effect = [1, 20]

  with pytest.raises(DominioYaExisteError):
    await service.crear(datos_dominio())

  db.add.assert_not_called()
  db.commit.assert_not_awaited()


async def test_crear_guarda_dominio(service, db):
  db.scalar.side_effect = [1, None]
  datos = datos_dominio()

  resultado = await service.crear(datos)

  assert resultado.nombre == datos.nombre
  assert resultado.cliente_id == datos.cliente_id
  db.add.assert_called_once_with(resultado)
  db.commit.assert_awaited_once()


async def test_crear_conflicto_de_unicidad_revierte_y_lanza_error(service, db):
  db.scalar.side_effect = [1, None]
  error_db = SimpleNamespace(
    diag=SimpleNamespace(constraint_name="dominios_nombre_key")
  )
  db.commit.side_effect = IntegrityError("INSERT", {}, error_db)

  with pytest.raises(DominioYaExisteError):
    await service.crear(datos_dominio())

  db.rollback.assert_awaited_once()


async def test_actualizar_cambia_solo_campos_enviados(service, db):
  dominio = dominio_falso()
  db.get.return_value = dominio
  db.scalar.return_value = 1

  resultado = await service.actualizar(dominio.id, DominioUpdate(precio="25.00"))

  assert resultado.precio == 25
  assert resultado.nombre == "ejemplo.com"
  db.commit.assert_awaited_once()


async def test_actualizar_vacio_no_hace_commit(service, db):
  dominio = dominio_falso()
  db.get.return_value = dominio

  resultado = await service.actualizar(dominio.id, DominioUpdate())

  assert resultado is dominio
  db.scalar.assert_not_awaited()
  db.commit.assert_not_awaited()


async def test_actualizar_cliente_inexistente_lanza_error(service, db):
  db.get.return_value = dominio_falso()
  db.scalar.return_value = None

  with pytest.raises(ClienteNoEncontradoError):
    await service.actualizar(10, DominioUpdate(cliente_id=99))

  db.commit.assert_not_awaited()


async def test_actualizar_nombre_existente_lanza_error(service, db):
  db.get.return_value = dominio_falso()
  db.scalar.side_effect = [1, 20]

  with pytest.raises(DominioYaExisteError):
    await service.actualizar(10, DominioUpdate(nombre="otro.com"))

  db.commit.assert_not_awaited()


async def test_actualizar_fecha_invalida_lanza_error_de_dominio(service, db):
  db.get.return_value = dominio_falso(mes_renovacion=4)

  with pytest.raises(DominioFechaRenovacionInvalidaError):
    await service.actualizar(10, DominioUpdate(dia_renovacion=31))

  db.scalar.assert_not_awaited()
  db.commit.assert_not_awaited()


async def test_dar_de_baja_actualiza_estado_y_motivo(service, db):
  dominio = dominio_falso()
  db.get.return_value = dominio

  resultado = await service.dar_de_baja(dominio.id, motivo="impago")

  assert resultado.estado == Estado.BAJA
  assert resultado.fecha_baja is not None
  assert resultado.fecha_baja.tzinfo is not None
  assert resultado.motivo_baja == "impago"
  db.commit.assert_awaited_once()


async def test_dar_de_baja_es_idempotente(service, db):
  dominio = dominio_falso(estado=Estado.BAJA, motivo_baja="impago")
  db.get.return_value = dominio

  resultado = await service.dar_de_baja(dominio.id, motivo="otro")

  assert resultado.motivo_baja == "impago"
  db.commit.assert_not_awaited()


async def test_dar_de_alta_limpia_datos_de_baja(service, db):
  dominio = dominio_falso(estado=Estado.BAJA, motivo_baja="impago")
  db.get.return_value = dominio

  resultado = await service.dar_de_alta(dominio.id)

  assert resultado.estado == Estado.ALTA
  assert resultado.fecha_baja is None
  assert resultado.motivo_baja is None
  db.commit.assert_awaited_once()


async def test_dar_de_alta_es_idempotente(service, db):
  dominio = dominio_falso(estado=Estado.ALTA)
  db.get.return_value = dominio

  resultado = await service.dar_de_alta(dominio.id)

  assert resultado is dominio
  db.commit.assert_not_awaited()
