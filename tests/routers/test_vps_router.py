from fastapi import status
from httpx import AsyncClient

from app.core.messages import MensajesVps
from app.models.enums import Estado


async def crear_cliente(client: AsyncClient, nombre_corto: str = "VPS TEST") -> int:
  respuesta = await client.post(
    "/clientes/",
    json={
      "nombre_corto": nombre_corto,
      "nombre_largo": "Cliente VPS S.L.",
      "direccion": "Calle Mayor 1",
      "codigo_postal": "46001",
      "poblacion": "Valencia",
      "cif": "B12345678",
    },
  )
  assert respuesta.status_code == status.HTTP_201_CREATED
  return respuesta.json()["data"]["id"]


def datos_vps(cliente_id: int, **cambios) -> dict:
  return {
    "cliente_id": cliente_id,
    "descripcion": "Servidor de aplicaciones",
    "dia_renovacion": 15,
    "precio": "49.90",
    **cambios,
  }


async def test_vps_crud_y_ciclo_baja_alta(client: AsyncClient):
  cliente_id = await crear_cliente(client)
  creada = await client.post(
    "/vps/",
    json=datos_vps(cliente_id, domiciliacion="ES1234567890"),
  )

  assert creada.status_code == status.HTTP_201_CREATED
  body_creada = creada.json()
  vps = body_creada["data"]
  vps_id = vps["id"]
  assert vps["descripcion"] == "Servidor de aplicaciones"
  assert vps["precio"] == "49.90"
  assert vps["estado"] == Estado.ALTA.value
  assert body_creada["message"] == MensajesVps.CREADO

  obtenido = await client.get(f"/vps/{vps_id}")
  assert obtenido.status_code == status.HTTP_200_OK
  assert obtenido.json()["data"]["id"] == vps_id
  assert obtenido.json()["message"] == MensajesVps.OBTENIDO

  listado = await client.get("/vps/", params={"estado": Estado.ALTA.value})
  assert listado.status_code == status.HTTP_200_OK
  assert [item["id"] for item in listado.json()["data"]] == [vps_id]
  assert listado.json()["message"] == MensajesVps.LISTADOS

  actualizado = await client.patch(
    f"/vps/{vps_id}",
    json={"descripcion": "Servidor web", "info_adicional": "Ubuntu LTS"},
  )
  assert actualizado.status_code == status.HTTP_200_OK
  assert actualizado.json()["data"]["descripcion"] == "Servidor web"
  assert actualizado.json()["data"]["info_adicional"] == "Ubuntu LTS"
  assert actualizado.json()["message"] == MensajesVps.ACTUALIZADO

  baja = await client.patch(
    f"/vps/{vps_id}/baja",
    params={"motivo": "fin de contrato"},
  )
  assert baja.status_code == status.HTTP_200_OK
  assert baja.json()["data"]["estado"] == Estado.BAJA.value
  assert baja.json()["data"]["motivo_baja"] == "fin de contrato"
  assert baja.json()["message"] == MensajesVps.DADO_DE_BAJA

  alta = await client.patch(f"/vps/{vps_id}/alta")
  assert alta.status_code == status.HTTP_200_OK
  assert alta.json()["data"]["estado"] == Estado.ALTA.value
  assert alta.json()["data"]["motivo_baja"] is None
  assert alta.json()["message"] == MensajesVps.DADO_DE_ALTA


async def test_vps_cliente_inexistente_devuelve_404(client: AsyncClient):
  respuesta = await client.post(
    "/vps/",
    json=datos_vps(999999),
  )

  assert respuesta.status_code == status.HTTP_404_NOT_FOUND
  assert respuesta.json()["success"] is False
  assert respuesta.json()["code"] == "RECURSO_NO_ENCONTRADO"


async def test_vps_inexistente_devuelve_404(client: AsyncClient):
  respuesta = await client.get("/vps/999999")

  assert respuesta.status_code == status.HTTP_404_NOT_FOUND
  body = respuesta.json()
  assert body["success"] is False
  assert body["code"] == "RECURSO_NO_ENCONTRADO"
  assert body["message"] == "vps '999999' no encontrado"


async def test_vps_rechaza_precio_y_dia_de_renovacion_invalidos(client: AsyncClient):
  cliente_id = await crear_cliente(client)

  precio_invalido = await client.post(
    "/vps/",
    json=datos_vps(cliente_id, precio="0.00"),
  )
  assert precio_invalido.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert precio_invalido.json()["code"] == "ERROR_VALIDACION"
  assert any(
    "precio" in error["loc"]
    for error in precio_invalido.json()["errors"]
  )

  dia_invalido = await client.post(
    "/vps/",
    json=datos_vps(cliente_id, dia_renovacion=32),
  )
  assert dia_invalido.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert any(
    "dia_renovacion" in error["loc"]
    for error in dia_invalido.json()["errors"]
  )
