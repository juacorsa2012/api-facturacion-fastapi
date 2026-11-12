from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.core.dependencies import HostingServiceDep
from app.core.messages import MensajesHosting
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, MAX_LIMIT
from app.models.enums import Estado
from app.schemas.api_response import ApiResponse
from app.schemas.hosting_schema import HostingCreate, HostingResponse, HostingUpdate


router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[HostingResponse])
async def crear(datos: HostingCreate, service: HostingServiceDep) -> ApiResponse[HostingResponse]:
  hosting = await service.crear(datos)
  return ApiResponse[HostingResponse](message=MensajesHosting.CREADO, data=HostingResponse.model_validate(hosting))


@router.get("/", response_model=ApiResponse[list[HostingResponse]])
async def obtener_todos(
  service: HostingServiceDep,
  offset: int = Query(default=DEFAULT_OFFSET, ge=0),
  limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
  estado: Estado | None = None,
) -> ApiResponse[list[HostingResponse]]:
  hostings = await service.obtener_todos(offset=offset, limit=limit, estado=estado)
  return ApiResponse[list[HostingResponse]](message=MensajesHosting.LISTADOS, data=[HostingResponse.model_validate(hosting) for hosting in hostings])


@router.get("/{hosting_id}", response_model=ApiResponse[HostingResponse])
async def obtener_por_id(hosting_id: Annotated[int, Path(gt=0)], service: HostingServiceDep) -> ApiResponse[HostingResponse]:
  hosting = await service.obtener_por_id(hosting_id)
  return ApiResponse[HostingResponse](message=MensajesHosting.OBTENIDO, data=HostingResponse.model_validate(hosting))


@router.patch("/{hosting_id}", response_model=ApiResponse[HostingResponse])
async def actualizar(
  hosting_id: Annotated[int, Path(gt=0)],
  datos: HostingUpdate,
  service: HostingServiceDep,
) -> ApiResponse[HostingResponse]:
  hosting = await service.actualizar(hosting_id, datos)
  return ApiResponse[HostingResponse](message=MensajesHosting.ACTUALIZADO, data=HostingResponse.model_validate(hosting))


@router.patch("/{hosting_id}/baja", response_model=ApiResponse[HostingResponse])
async def dar_de_baja(
  hosting_id: Annotated[int, Path(gt=0)],
  service: HostingServiceDep,
  motivo: str | None = Query(default=None, max_length=255),
) -> ApiResponse[HostingResponse]:
  hosting = await service.dar_de_baja(hosting_id, motivo)
  return ApiResponse[HostingResponse](message=MensajesHosting.DADO_DE_BAJA, data=HostingResponse.model_validate(hosting))


@router.patch("/{hosting_id}/alta", response_model=ApiResponse[HostingResponse])
async def dar_de_alta(hosting_id: Annotated[int, Path(gt=0)], service: HostingServiceDep) -> ApiResponse[HostingResponse]:
  hosting = await service.dar_de_alta(hosting_id)
  return ApiResponse[HostingResponse](message=MensajesHosting.DADO_DE_ALTA, data=HostingResponse.model_validate(hosting))
