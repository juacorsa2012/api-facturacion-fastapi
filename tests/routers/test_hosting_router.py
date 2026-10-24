from httpx import AsyncClient
from fastapi import status

from app.core.messages import MensajesHosting
from app.models.enums import Estado


async def crear_cliente(client: AsyncClient, nombre_corto: str = "HOSTING TEST") -> int:
  respuesta = await client.post(
    "/clientes/",
    json={
      "nombre_corto": nombre_corto,
      "nombre_largo": "Cliente Hosting S.L.",
      "direccion": "Calle Mayor 1",
      "codigo_postal": "46001",
      "poblacion": "Valencia",
      "cif": "B12345678",
    },
  )
  assert respuesta.status_code == status.HTTP_201_CREATED
  return respuesta.json()["data"]["id"]


def datos_hosting(cliente_id: int, **cambios) -> dict:
  return {
    "cliente_id": cliente_id,
    "nombre": "hosting-ejemplo",
    "dia_renovacion": 15,
    "mes_renovacion": 6,
    **cambios,
  }


async def test_hosting_crud_y_ciclo_baja_alta(client: AsyncClient):
  cliente_id = await crear_cliente(client)
  creada = await client.post("/hostings/", json=datos_hosting(cliente_id))

  assert creada.status_code == status.HTTP_201_CREATED
  body_creada = creada.json()
  hosting = body_creada["data"]
  hosting_id = hosting["id"]
  assert hosting["nombre"] == "hosting-ejemplo"
  assert hosting["precio"] == "19.90"
  assert hosting["estado"] == Estado.ALTA.value
  assert body_creada["message"] == MensajesHosting.CREADO

  obtenido = await client.get(f"/hostings/{hosting_id}")
  assert obtenido.status_code == status.HTTP_200_OK
  assert obtenido.json()["data"]["id"] == hosting_id
  assert obtenido.json()["message"] == MensajesHosting.OBTENIDO

  listado = await client.get("/hostings/", params={"estado": Estado.ALTA.value})
  assert listado.status_code == status.HTTP_200_OK
  assert [item["id"] for item in listado.json()["data"]] == [hosting_id]
  assert listado.json()["message"] == MensajesHosting.LISTADOS

  actualizado = await client.patch(
    f"/hostings/{hosting_id}",
    json={"info_adicional": "Panel del proveedor", "precio": "35.50"},
  )
  assert actualizado.status_code == status.HTTP_200_OK
  assert actualizado.json()["data"]["info_adicional"] == "Panel del proveedor"
  assert actualizado.json()["data"]["precio"] == "35.50"
  assert actualizado.json()["message"] == MensajesHosting.ACTUALIZADO

  baja = await client.patch(
    f"/hostings/{hosting_id}/baja",
    params={"motivo": "fin de contrato"},
  )
  assert baja.status_code == status.HTTP_200_OK
  assert baja.json()["data"]["estado"] == Estado.BAJA.value
  assert baja.json()["data"]["motivo_baja"] == "fin de contrato"
  assert baja.json()["message"] == MensajesHosting.DADO_DE_BAJA

  alta = await client.patch(f"/hostings/{hosting_id}/alta")
  assert alta.status_code == status.HTTP_200_OK
  assert alta.json()["data"]["estado"] == Estado.ALTA.value
  assert alta.json()["data"]["motivo_baja"] is None
  assert alta.json()["message"] == MensajesHosting.DADO_DE_ALTA


async def test_hosting_duplicado_y_cliente_inexistente(client: AsyncClient):
  cliente_id = await crear_cliente(client)
  payload = datos_hosting(cliente_id)
  primera = await client.post("/hostings/", json=payload)
  assert primera.status_code == status.HTTP_201_CREATED

  duplicada = await client.post("/hostings/", json=payload)
  assert duplicada.status_code == status.HTTP_409_CONFLICT
  assert duplicada.json()["success"] is False
  assert duplicada.json()["code"] == "RECURSO_DUPLICADO"

  cliente_inexistente = await client.post(
    "/hostings/",
    json=datos_hosting(999999, nombre="otro-hosting"),
  )
  assert cliente_inexistente.status_code == status.HTTP_404_NOT_FOUND
  assert cliente_inexistente.json()["code"] == "RECURSO_NO_ENCONTRADO"


async def test_hosting_valida_renovacion_y_datos_adicionales(client: AsyncClient):
  cliente_id = await crear_cliente(client)
  payload = datos_hosting(cliente_id, dia_renovacion=30, mes_renovacion=2)

  respuesta = await client.post("/hostings/", json=payload)

  assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  body = respuesta.json()
  assert body["success"] is False
  assert body["code"] == "ERROR_VALIDACION"
  assert any("dia_renovacion" in error["msg"] for error in body["errors"])

  payload_valido = datos_hosting(
    cliente_id,
    nombre="otro-hosting",
    info_adicional="x" * 1001,
  )
  respuesta = await client.post("/hostings/", json=payload_valido)

  assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert any(
    error["loc"][-1] == "info_adicional"
    for error in respuesta.json()["errors"]
  )


async def test_hosting_inexistente_devuelve_404(client: AsyncClient):
  respuesta = await client.get("/hostings/999999")

  assert respuesta.status_code == status.HTTP_404_NOT_FOUND
  body = respuesta.json()
  assert body["success"] is False
  assert body["code"] == "RECURSO_NO_ENCONTRADO"
  assert body["message"] == "hosting '999999' no encontrado"
