from typing import Annotated

from fastapi import APIRouter, Path, Query, status
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, MAX_LIMIT
from app.schemas.cliente_schema import ClienteCreate, ClienteResponse, ClienteUpdate
from app.schemas.api_response import ApiResponse
from app.schemas.dominio_schema import DominioResponse
from app.schemas.hosting_schema import HostingResponse
from app.schemas.vps_schema import VpsResponse
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
async def obtener_todos(service: ClienteServiceDep, offset: int = Query(default=DEFAULT_OFFSET, ge=0), limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT), estado: Estado | None = None) -> ApiResponse[list[ClienteResponse]]:
  clientes = await service.obtener_todos(offset=offset, limit=limit, estado=estado)
  return ApiResponse[list[ClienteResponse]](
    message=MensajesCliente.LISTADOS,
    data=[ClienteResponse.model_validate(cliente) for cliente in clientes],
  )

@router.get("/{cliente_id}", response_model=ApiResponse[ClienteResponse])
async def obtener_por_id(cliente_id: Annotated[int, Path(gt=0)], service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.obtener_por_id(cliente_id)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.OBTENIDO,
    data=ClienteResponse.model_validate(cliente),
  )


@router.get("/{cliente_id}/dominios", response_model=ApiResponse[list[DominioResponse]])
async def dominios_de_cliente(cliente_id: Annotated[int, Path(gt=0)], service: ClienteServiceDep,
  offset: int = Query(default=DEFAULT_OFFSET, ge=0),
  limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
  estado: Estado | None = None
) -> ApiResponse[list[DominioResponse]]:
    dominios = await service.obtener_dominios(cliente_id=cliente_id, offset=offset, limit=limit, estado=estado)
    return ApiResponse[list[DominioResponse]](
      message=MensajesCliente.DOMINIOS_OBTENIDOS,
      data=[DominioResponse.model_validate(d) for d in dominios],
    )

@router.get("/{cliente_id}/hostings", response_model=ApiResponse[list[HostingResponse]])
async def hostings_de_cliente(cliente_id: Annotated[int, Path(gt=0)], service: ClienteServiceDep,
  offset: int = Query(default=DEFAULT_OFFSET, ge=0),
  limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
  estado: Estado | None = None
) -> ApiResponse[list[HostingResponse]]:
    hostings = await service.obtener_hostings(cliente_id=cliente_id, offset=offset, limit=limit, estado=estado)
    return ApiResponse[list[HostingResponse]](
      message=MensajesCliente.HOSTINGS_OBTENIDOS,
      data=[HostingResponse.model_validate(h) for h in hostings],
    )

@router.get("/{cliente_id}/vps", response_model=ApiResponse[list[VpsResponse]])
async def vps_de_cliente(
  cliente_id: Annotated[int, Path(gt=0)],
  service: ClienteServiceDep,
  offset: int = Query(default=DEFAULT_OFFSET, ge=0),
  limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
  estado: Estado | None = None,
) -> ApiResponse[list[VpsResponse]]:
    vps_list = await service.obtener_vps(cliente_id=cliente_id, offset=offset, limit=limit, estado=estado)
    return ApiResponse[list[VpsResponse]](
      message=MensajesCliente.VPS_OBTENIDOS,
      data=[VpsResponse.model_validate(vps) for vps in vps_list],
    )



@router.patch("/{cliente_id}", response_model=ApiResponse[ClienteResponse])
async def actualizar(cliente_id: Annotated[int, Path(gt=0)], datos: ClienteUpdate, service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.actualizar(cliente_id, datos)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.ACTUALIZADO,
    data=ClienteResponse.model_validate(cliente),
  )

@router.patch("/{cliente_id}/baja", response_model=ApiResponse[ClienteResponse])
async def dar_de_baja(cliente_id: Annotated[int, Path(gt=0)], service: ClienteServiceDep, motivo: str | None = Query(default=None, max_length=255)) -> ApiResponse[ClienteResponse]:
  cliente = await service.dar_de_baja(cliente_id, motivo)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.DADO_DE_BAJA,
    data=ClienteResponse.model_validate(cliente),
  )

@router.patch("/{cliente_id}/alta", response_model=ApiResponse[ClienteResponse])
async def dar_de_alta(cliente_id: Annotated[int, Path(gt=0)], service: ClienteServiceDep) -> ApiResponse[ClienteResponse]:
  cliente = await service.dar_de_alta(cliente_id)
  return ApiResponse[ClienteResponse](
    message=MensajesCliente.DADO_DE_ALTA,
    data=ClienteResponse.model_validate(cliente),
  )
