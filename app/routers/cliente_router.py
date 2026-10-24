from fastapi import APIRouter, Query, status
from app.schemas.cliente_schema import ClienteCreate, ClienteResponse, ClienteUpdate
from app.schemas.api_response import ApiResponse
from app.core.dependencies import ClienteServiceDep
from app.core.messages import MensajesCliente
from app.models.enums import Estado

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[ClienteResponse])
async def crear(datos: ClienteCreate, service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.crear(datos)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.CREADO,
    data=ClienteResponse.model_validate(cliente),
  )

@router.get("/", response_model=ApiResponse[list[ClienteResponse]])
async def obtener_todos(service: ClienteServiceDep, offset: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=500), estado: Estado | None = None) -> ApiResponse[list[ClienteResponse]]:
  clientes = await service.obtener_todos(offset=offset, limit=limit, estado=estado)
  return ApiResponse[list[ClienteResponse]](
    message=MensajesCliente.LISTADOS,
    data=[ClienteResponse.model_validate(cliente) for cliente in clientes],
  )

@router.get("/{cliente_id}", response_model=ApiResponse[ClienteResponse])
async def obtener_por_id(cliente_id: int, service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.obtener_por_id(cliente_id)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.OBTENIDO,
    data=ClienteResponse.model_validate(cliente),
  )

@router.patch("/{cliente_id}", response_model=ApiResponse[ClienteResponse])
async def actualizar(cliente_id: int, datos: ClienteUpdate, service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.actualizar(cliente_id, datos)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.ACTUALIZADO,
    data=ClienteResponse.model_validate(cliente),
  )

@router.patch("/{cliente_id}/baja", response_model=ApiResponse[ClienteResponse])
async def dar_de_baja(cliente_id: int, service: ClienteServiceDep, motivo: str | None = None) -> ApiResponse[ClienteResponse]:
  cliente = await service.dar_de_baja(cliente_id, motivo)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.DADO_DE_BAJA,
    data=ClienteResponse.model_validate(cliente),
  )

@router.patch("/{cliente_id}/alta", response_model=ApiResponse[ClienteResponse])
async def dar_de_alta(cliente_id: int, service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.dar_de_alta(cliente_id)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.DADO_DE_ALTA,
    data=ClienteResponse.model_validate(cliente),
  )
