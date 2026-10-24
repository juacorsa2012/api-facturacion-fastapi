from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.vps_exceptions import VpsNoEncontradoError
from app.models.enums import Estado
from app.schemas.vps_schema import VpsCreate, VpsUpdate
from app.services.vps_service import VpsService


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
  return VpsService(db)


def datos_vps(**cambios) -> VpsCreate:
  valores = {
    "cliente_id": 1,
    "descripcion": "Servidor de aplicaciones",
    "dia_renovacion": 15,
    "precio": Decimal("49.90"),
  }
  return VpsCreate(**{**valores, **cambios})


def vps_falso(**cambios):
  valores = {
    "id": 10,
    "cliente_id": 1,
    "descripcion": "Servidor de aplicaciones",
    "dia_renovacion": 15,
    "precio": Decimal("49.90"),
    "estado": Estado.ALTA,
    "fecha_baja": None,
    "motivo_baja": None,
    "domiciliacion": None,
    "info_adicional": None,
  }
  return SimpleNamespace(**{**valores, **cambios})


async def test_obtener_por_id_inexistente_lanza_error(service, db):
  db.get.return_value = None

  with pytest.raises(VpsNoEncontradoError):
    await service.obtener_por_id(999)


async def test_obtener_todos_filtra_y_pagina(service, db):
  registros = [vps_falso()]
  resultado_db = MagicMock()
  resultado_db.all.return_value = registros
  db.scalars.return_value = resultado_db

  resultado = await service.obtener_todos(offset=2, limit=3, estado=Estado.ALTA)

  assert resultado == registros
  db.scalars.assert_awaited_once()


async def test_crear_vps_guarda_datos(service, db):
  db.scalar.return_value = 1
  datos = datos_vps(domiciliacion="ES1234567890")

  resultado = await service.crear(datos)

  assert resultado.descripcion == datos.descripcion
  assert resultado.precio == Decimal("49.90")
  assert resultado.domiciliacion == "ES1234567890"
  db.add.assert_called_once_with(resultado)
  db.commit.assert_awaited_once()


async def test_crear_cliente_inexistente_lanza_error(service, db):
  db.scalar.return_value = None

  with pytest.raises(ClienteNoEncontradoError):
    await service.crear(datos_vps())

  db.add.assert_not_called()
  db.commit.assert_not_awaited()


async def test_actualizar_cambia_solo_campos_enviados(service, db):
  vps = vps_falso()
  db.get.return_value = vps
  db.scalar.return_value = 1

  resultado = await service.actualizar(
    vps.id,
    VpsUpdate(info_adicional="Proveedor de infraestructura"),
  )

  assert resultado.info_adicional == "Proveedor de infraestructura"
  assert resultado.descripcion == "Servidor de aplicaciones"
  db.commit.assert_awaited_once()


async def test_actualizar_cliente_inexistente_lanza_error(service, db):
  db.get.return_value = vps_falso()
  db.scalar.return_value = None

  with pytest.raises(ClienteNoEncontradoError):
    await service.actualizar(10, VpsUpdate(cliente_id=999))

  db.commit.assert_not_awaited()


async def test_actualizar_sin_cambios_no_hace_commit(service, db):
  vps = vps_falso()
  db.get.return_value = vps

  resultado = await service.actualizar(vps.id, VpsUpdate())

  assert resultado is vps
  db.scalar.assert_not_awaited()
  db.commit.assert_not_awaited()


async def test_baja_y_alta_actualizan_estado(service, db):
  vps = vps_falso()
  db.get.return_value = vps

  baja = await service.dar_de_baja(vps.id, motivo="fin de contrato")
  assert baja.estado == Estado.BAJA
  assert baja.fecha_baja is not None
  assert baja.motivo_baja == "fin de contrato"

  alta = await service.dar_de_alta(vps.id)
  assert alta.estado == Estado.ALTA
  assert alta.fecha_baja is None
  assert alta.motivo_baja is None
  assert db.commit.await_count == 2
