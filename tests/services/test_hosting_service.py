from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions.cliente_exceptions import ClienteNoEncontradoError
from app.exceptions.hosting_exceptions import (
  HostingFechaRenovacionInvalidaError,
  HostingNoEncontradoError,
  HostingYaExisteError,
)
from app.models.enums import Estado
from app.schemas.hosting_schema import HostingCreate, HostingUpdate
from app.services.hosting_service import HostingService


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
  return HostingService(db)


def datos_hosting(**cambios) -> HostingCreate:
  valores = {
    "cliente_id": 1,
    "nombre": "hosting-ejemplo",
    "dia_renovacion": 15,
    "mes_renovacion": 6,
  }
  return HostingCreate(**{**valores, **cambios})


def hosting_falso(**cambios):
  valores = {
    "id": 10,
    "cliente_id": 1,
    "nombre": "hosting-ejemplo",
    "dia_renovacion": 15,
    "mes_renovacion": 6,
    "precio": Decimal("19.90"),
    "estado": Estado.ALTA,
    "fecha_baja": None,
    "motivo_baja": None,
    "info_adicional": None,
  }
  return SimpleNamespace(**{**valores, **cambios})


async def test_obtener_por_id_inexistente_lanza_error(service, db):
  db.get.return_value = None

  with pytest.raises(HostingNoEncontradoError):
    await service.obtener_por_id(999)


async def test_crear_hosting_guarda_datos(service, db):
  db.scalar.side_effect = [1, None]
  datos = datos_hosting(info_adicional="Servidor Linux")

  resultado = await service.crear(datos)

  assert resultado.nombre == datos.nombre
  assert resultado.info_adicional == "Servidor Linux"
  db.add.assert_called_once_with(resultado)
  db.commit.assert_awaited_once()


async def test_crear_cliente_inexistente_lanza_error(service, db):
  db.scalar.return_value = None

  with pytest.raises(ClienteNoEncontradoError):
    await service.crear(datos_hosting())

  db.add.assert_not_called()
  db.commit.assert_not_awaited()


async def test_crear_nombre_duplicado_lanza_error(service, db):
  db.scalar.side_effect = [1, 10]

  with pytest.raises(HostingYaExisteError):
    await service.crear(datos_hosting())

  db.add.assert_not_called()
  db.commit.assert_not_awaited()


async def test_crear_conflicto_unico_revierte_y_lanza_error(service, db):
  db.scalar.side_effect = [1, None]
  error_db = SimpleNamespace(constraint_name="hostings_nombre_key")
  db.commit.side_effect = IntegrityError("INSERT", {}, error_db)

  with pytest.raises(HostingYaExisteError):
    await service.crear(datos_hosting())

  db.rollback.assert_awaited_once()


async def test_actualizar_cambia_solo_campos_enviados(service, db):
  hosting = hosting_falso()
  db.get.return_value = hosting
  db.scalar.return_value = 1

  resultado = await service.actualizar(
    hosting.id,
    HostingUpdate(info_adicional="Panel del proveedor"),
  )

  assert resultado.info_adicional == "Panel del proveedor"
  assert resultado.nombre == "hosting-ejemplo"
  db.commit.assert_awaited_once()


async def test_actualizar_fecha_invalida_lanza_error(service, db):
  db.get.return_value = hosting_falso(mes_renovacion=4)

  with pytest.raises(HostingFechaRenovacionInvalidaError):
    await service.actualizar(10, HostingUpdate(dia_renovacion=31))

  db.scalar.assert_not_awaited()
  db.commit.assert_not_awaited()


async def test_baja_y_alta_actualizan_estado(service, db):
  hosting = hosting_falso()
  db.get.return_value = hosting

  baja = await service.dar_de_baja(hosting.id, motivo="fin de contrato")
  assert baja.estado == Estado.BAJA
  assert baja.fecha_baja is not None
  assert baja.motivo_baja == "fin de contrato"

  alta = await service.dar_de_alta(hosting.id)
  assert alta.estado == Estado.ALTA
  assert alta.fecha_baja is None
  assert alta.motivo_baja is None
  assert db.commit.await_count == 2
