from fastapi import APIRouter, Query, status

from app.core.dependencies import VpsServiceDep
from app.core.messages import MensajesVps
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, MAX_LIMIT
from app.models.enums import Estado
from app.schemas.api_response import ApiResponse
from app.schemas.vps_schema import VpsCreate, VpsResponse, VpsUpdate


router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[VpsResponse])
async def crear(datos: VpsCreate, service: VpsServiceDep) -> ApiResponse[VpsResponse]:
  vps = await service.crear(datos)
  return ApiResponse[VpsResponse](message=MensajesVps.CREADO, data=VpsResponse.model_validate(vps))


@router.get("/", response_model=ApiResponse[list[VpsResponse]])
async def obtener_todos(
  service: VpsServiceDep,
  offset: int = Query(default=DEFAULT_OFFSET, ge=0),
  limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
  estado: Estado | None = None,
) -> ApiResponse[list[VpsResponse]]:
  vps_list = await service.obtener_todos(offset=offset, limit=limit, estado=estado)
  return ApiResponse[list[VpsResponse]](message=MensajesVps.LISTADOS, data=[VpsResponse.model_validate(vps) for vps in vps_list])


@router.get("/{vps_id}", response_model=ApiResponse[VpsResponse])
async def obtener_por_id(vps_id: int, service: VpsServiceDep) -> ApiResponse[VpsResponse]:
  vps = await service.obtener_por_id(vps_id)
  return ApiResponse[VpsResponse](message=MensajesVps.OBTENIDO, data=VpsResponse.model_validate(vps))


@router.patch("/{vps_id}", response_model=ApiResponse[VpsResponse])
async def actualizar(vps_id: int, datos: VpsUpdate, service: VpsServiceDep) -> ApiResponse[VpsResponse]:
  vps = await service.actualizar(vps_id, datos)
  return ApiResponse[VpsResponse](message=MensajesVps.ACTUALIZADO, data=VpsResponse.model_validate(vps))


@router.patch("/{vps_id}/baja", response_model=ApiResponse[VpsResponse])
async def dar_de_baja(vps_id: int, service: VpsServiceDep, motivo: str | None = Query(default=None, max_length=255)) -> ApiResponse[VpsResponse]:
  vps = await service.dar_de_baja(vps_id, motivo)
  return ApiResponse[VpsResponse](message=MensajesVps.DADO_DE_BAJA, data=VpsResponse.model_validate(vps))


@router.patch("/{vps_id}/alta", response_model=ApiResponse[VpsResponse])
async def dar_de_alta(vps_id: int, service: VpsServiceDep) -> ApiResponse[VpsResponse]:
  vps = await service.dar_de_alta(vps_id)
  return ApiResponse[VpsResponse](message=MensajesVps.DADO_DE_ALTA, data=VpsResponse.model_validate(vps))
