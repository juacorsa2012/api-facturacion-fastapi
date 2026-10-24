from decimal import Decimal

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.messages import MensajesCliente
from app.models.enums import Empresa, Estado, FormaPago, Vencimiento

PAYLOAD = {
  "nombre_corto": "a",
  "nombre_largo": "A S.L.",
  "direccion": "Calle Mayor 1",
  "codigo_postal": "46001",
  "poblacion": "Valencia",
  "cif": "B12345678",
}

CLIENTE_ID_INEXISTENTE = 999999


async def test_crear_cliente(client: AsyncClient):
  r = await client.post("/clientes/", json=PAYLOAD)
  assert r.status_code == status.HTTP_201_CREATED
  body = r.json()
  cliente = body["data"]

  assert cliente["id"] is not None
  assert cliente["estado"] == Estado.ALTA.value
  assert body["success"] is True
  assert body["message"] == MensajesCliente.CREADO

async def test_crear_duplicado_devuelve_409(client: AsyncClient):
  r_primero = await client.post("/clientes/", json=PAYLOAD)
  assert r_primero.status_code == status.HTTP_201_CREATED

  r = await client.post("/clientes/", json=PAYLOAD)
  assert r.status_code == status.HTTP_409_CONFLICT
  body = r.json()

  assert body["success"] is False
  assert body["code"] == "RECURSO_DUPLICADO"
  assert body["message"] == f"Ya existe un cliente con nombre_corto '{PAYLOAD['nombre_corto'].upper()}'"


@pytest.mark.parametrize("accion", ["baja", "alta"])
async def test_baja_o_alta_cliente_inexistente_devuelve_404(client: AsyncClient, accion: str):
  cliente_id = CLIENTE_ID_INEXISTENTE
  r = await client.patch(f"/clientes/{cliente_id}/{accion}")

  assert r.status_code == status.HTTP_404_NOT_FOUND
  body = r.json()
  assert body["success"] is False
  assert body["message"] == f"cliente '{cliente_id}' no encontrado"
  assert body["code"] == "RECURSO_NO_ENCONTRADO"

async def test_payload_invalido_devuelve_422_no_cumple_con_el_schema(client: AsyncClient):
  r = await client.post("/clientes/", json={"nombre_corto": "a"})
  assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  body = r.json()

  campos_ausentes = {
    error["loc"][-1]
    for error in body["detail"]
    if error["type"] == "missing"
  }
  assert campos_ausentes == {
    "nombre_largo",
    "direccion",
    "codigo_postal",
    "poblacion",
    "cif",
  }

async def test_paginacion_fuera_de_rango_devuelve_422(client: AsyncClient):
  assert (await client.get("/clientes/?limit=0")).status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert (await client.get("/clientes/?offset=-1")).status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_baja_y_alta(client: AsyncClient):
  r_creacion = await client.post("/clientes/", json=PAYLOAD)
  assert r_creacion.status_code == status.HTTP_201_CREATED
  cliente_id = r_creacion.json()["data"]["id"]

  r = await client.patch(f"/clientes/{cliente_id}/baja", params={"motivo": "impago"})
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.BAJA.value
  assert cliente["motivo_baja"] == "impago"
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_BAJA
 
  r = await client.patch(f"/clientes/{cliente_id}/alta")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.ALTA.value
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_ALTA
  

async def test_obtener_por_id(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.get(f"/clientes/{cliente_id}")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["id"] == cliente_id
  assert cliente["nombre_corto"] == PAYLOAD["nombre_corto"].upper()
  assert body["success"] is True
  assert body["message"] == MensajesCliente.OBTENIDO

async def test_obtener_por_id_inexistente(client: AsyncClient):
  cliente_id = CLIENTE_ID_INEXISTENTE
  r = await client.get(f"/clientes/{cliente_id}")
  assert r.status_code == status.HTTP_404_NOT_FOUND
  body = r.json()

  assert body["success"] is False
  assert body["message"] == f"cliente '{cliente_id}' no encontrado"
  assert body["code"] == "RECURSO_NO_ENCONTRADO"

async def test_baja_sin_motivo(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.patch(f"/clientes/{cliente_id}/baja")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.BAJA.value
  assert cliente["motivo_baja"] is None
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_BAJA

async def test_repetir_baja_y_alta_es_idempotente(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  await client.patch(
    f"/clientes/{cliente_id}/baja",
    params={"motivo": "impago"},
  )
  r = await client.patch(
    f"/clientes/{cliente_id}/baja",
    params={"motivo": "otro motivo"},
  )
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.BAJA.value
  assert cliente["motivo_baja"] == "impago"
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_BAJA

  await client.patch(f"/clientes/{cliente_id}/alta")
  r = await client.patch(f"/clientes/{cliente_id}/alta")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.ALTA.value
  assert cliente["motivo_baja"] is None
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_ALTA

async def test_listar_clientes_sin_resultados(client: AsyncClient):
  r = await client.get("/clientes/")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()

  assert body["data"] == []
  assert body["success"] is True
  assert body["message"] == MensajesCliente.LISTADOS

async def test_listar_clientes_filtrados_por_estado(client: AsyncClient):
  creado_alta = await client.post("/clientes/", json=PAYLOAD)
  assert creado_alta.status_code == status.HTTP_201_CREATED
  creado_baja = await client.post(
    "/clientes/",
    json={**PAYLOAD, "nombre_corto": "cliente baja"},
  )
  assert creado_baja.status_code == status.HTTP_201_CREATED
  cliente_baja_id = creado_baja.json()["data"]["id"]
  await client.patch(f"/clientes/{cliente_baja_id}/baja")

  r_alta = await client.get("/clientes/", params={"estado": Estado.ALTA.value})
  assert r_alta.status_code == status.HTTP_200_OK
  body_alta = r_alta.json()
  r_baja = await client.get("/clientes/", params={"estado": Estado.BAJA.value})
  assert r_baja.status_code == status.HTTP_200_OK
  body_baja = r_baja.json()

  assert [cliente["estado"] for cliente in body_alta["data"]] == [Estado.ALTA.value]
  assert [cliente["estado"] for cliente in body_baja["data"]] == [Estado.BAJA.value]
  assert body_alta["success"] is True
  assert body_baja["success"] is True
  assert body_alta["message"] == MensajesCliente.LISTADOS
  assert body_baja["message"] == MensajesCliente.LISTADOS

async def test_listar_clientes_con_paginacion_valida(client: AsyncClient):
  for nombre in ("ALFA", "BETA", "GAMMA"):
    r_creacion = await client.post("/clientes/", json={**PAYLOAD, "nombre_corto": nombre})
    assert r_creacion.status_code == status.HTTP_201_CREATED

  r = await client.get("/clientes/", params={"offset": 1, "limit": 1})
  assert r.status_code == status.HTTP_200_OK
  body = r.json()

  assert [cliente["nombre_corto"] for cliente in body["data"]] == ["BETA"]
  assert body["success"] is True
  assert body["message"] == MensajesCliente.LISTADOS

async def test_actualizar_cliente_parcialmente_conserva_campos_no_enviados(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.patch(f"/clientes/{cliente_id}", json={"poblacion": "Alicante"})
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["poblacion"] == "Alicante"
  assert cliente["nombre_corto"] == PAYLOAD["nombre_corto"].upper()
  assert cliente["nombre_largo"] == PAYLOAD["nombre_largo"].upper()
  assert cliente["direccion"] == PAYLOAD["direccion"]
  assert cliente["codigo_postal"] == PAYLOAD["codigo_postal"]
  assert cliente["cif"] == PAYLOAD["cif"]
  assert body["success"] is True
  assert body["message"] == MensajesCliente.ACTUALIZADO

async def test_actualizar_cliente_sin_cambios(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_original = creado.json()["data"]
  cliente_id = cliente_original["id"]

  r = await client.patch(f"/clientes/{cliente_id}", json={})
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["id"] == cliente_id
  assert cliente["nombre_corto"] == cliente_original["nombre_corto"]
  assert cliente["poblacion"] == cliente_original["poblacion"]
  assert cliente["updated_at"] == cliente_original["updated_at"]
  assert body["success"] is True
  assert body["message"] == MensajesCliente.ACTUALIZADO

async def test_actualizar_cliente_inexistente_devuelve_404(client: AsyncClient):
  cliente_id = CLIENTE_ID_INEXISTENTE
  r = await client.patch(f"/clientes/{cliente_id}", json={"poblacion": "Alicante"})
  assert r.status_code == status.HTTP_404_NOT_FOUND
  body = r.json()

  assert body["success"] is False
  assert body["message"] == f"cliente '{cliente_id}' no encontrado"
  assert body["code"] == "RECURSO_NO_ENCONTRADO"

async def test_actualizar_cliente_rechaza_campos_desconocidos(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.patch(f"/clientes/{cliente_id}", json={"campo_desconocido": "valor"})

  assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert any(
    error["type"] == "extra_forbidden"
    and error["loc"][-1] == "campo_desconocido"
    for error in r.json()["detail"]
  )

async def test_actualizar_cliente_rechaza_null_en_campo_obligatorio(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.patch(f"/clientes/{cliente_id}", json={"nombre_corto": None})

  assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
  assert any(
    error["loc"][-1] == "body"
    and "nombre_corto no puede ser null" in error["msg"]
    for error in r.json()["detail"]
  )

async def test_crear_cliente_aplica_valores_por_defecto(client: AsyncClient):
  r = await client.post("/clientes/", json=PAYLOAD)
  assert r.status_code == status.HTTP_201_CREATED
  body = r.json()
  cliente = body["data"]

  assert cliente["email"] is None
  assert cliente["domiciliacion"] is None
  assert Decimal(cliente["iva"]) == Decimal("21.00")
  assert Decimal(cliente["precio_desplazamiento"]) == Decimal("25.00")
  assert Decimal(cliente["precio_mano_obra"]) == Decimal("55.00")
  assert cliente["empresa"] == Empresa.LEMS.value
  assert cliente["forma_pago"] == FormaPago.RECIBO.value
  assert cliente["vencimiento"] == Vencimiento.UN_MES.value

async def test_listar_clientes_rechaza_estado_invalido(client: AsyncClient):
  r = await client.get("/clientes/", params={"estado": "OTRO"})

  assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_actualizar_cliente_a_nombre_corto_existente_devuelve_409(client: AsyncClient):
  r_primero = await client.post("/clientes/", json=PAYLOAD)
  assert r_primero.status_code == status.HTTP_201_CREATED
  creado = await client.post(
    "/clientes/",
    json={**PAYLOAD, "nombre_corto": "otro cliente"},
  )
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.patch(
    f"/clientes/{cliente_id}",
    json={"nombre_corto": PAYLOAD["nombre_corto"]},
  )
  assert r.status_code == status.HTTP_409_CONFLICT
  body = r.json()

  assert body["success"] is False
  assert body["code"] == "RECURSO_DUPLICADO"
  assert body["message"] == (
    f"Ya existe un cliente con nombre_corto '{PAYLOAD['nombre_corto'].upper()}'"
  )

async def test_repetir_baja_sin_motivo_es_idempotente(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r_primera_baja = await client.patch(f"/clientes/{cliente_id}/baja")
  assert r_primera_baja.status_code == status.HTTP_200_OK
  r = await client.patch(f"/clientes/{cliente_id}/baja")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.BAJA.value
  assert cliente["motivo_baja"] is None
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_BAJA

async def test_dar_de_alta_cliente_ya_activo_es_idempotente(client: AsyncClient):
  creado = await client.post("/clientes/", json=PAYLOAD)
  assert creado.status_code == status.HTTP_201_CREATED
  cliente_id = creado.json()["data"]["id"]

  r = await client.patch(f"/clientes/{cliente_id}/alta")
  assert r.status_code == status.HTTP_200_OK
  body = r.json()
  cliente = body["data"]

  assert cliente["estado"] == Estado.ALTA.value
  assert body["success"] is True
  assert body["message"] == MensajesCliente.DADO_DE_ALTA
