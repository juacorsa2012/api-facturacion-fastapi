from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.core.dependencies import DominioServiceDep
from app.core.messages import MensajesDominio
from app.core.pagination import DEFAULT_LIMIT, DEFAULT_OFFSET, MAX_LIMIT
from app.models.enums import Estado
from app.schemas.api_response import ApiResponse
from app.schemas.dominio_schema import DominioCreate, DominioResponse, DominioUpdate

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[DominioResponse])
async def crear(datos: DominioCreate, service: DominioServiceDep) -> ApiResponse[DominioResponse]:
  dominio = await service.crear(datos)
  return ApiResponse[DominioResponse](message=MensajesDominio.CREADO, data=DominioResponse.model_validate(dominio))


@router.get("/", response_model=ApiResponse[list[DominioResponse]])
async def obtener_todos(
  service: DominioServiceDep,
  offset: int = Query(default=DEFAULT_OFFSET, ge=0),
  limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
  estado: Estado | None = None,
) -> ApiResponse[list[DominioResponse]]:
  dominios = await service.obtener_todos(offset=offset, limit=limit, estado=estado)
  return ApiResponse[list[DominioResponse]](message=MensajesDominio.LISTADOS, data=[DominioResponse.model_validate(dominio) for dominio in dominios])


@router.get("/{dominio_id}", response_model=ApiResponse[DominioResponse])
async def obtener_por_id(dominio_id: Annotated[int, Path(gt=0)], service: DominioServiceDep) -> ApiResponse[DominioResponse]:
  dominio = await service.obtener_por_id(dominio_id)
  return ApiResponse[DominioResponse](message=MensajesDominio.OBTENIDO, data=DominioResponse.model_validate(dominio))


@router.patch("/{dominio_id}", response_model=ApiResponse[DominioResponse])
async def actualizar(
  dominio_id: Annotated[int, Path(gt=0)],
  datos: DominioUpdate,
  service: DominioServiceDep,
) -> ApiResponse[DominioResponse]:
  dominio = await service.actualizar(dominio_id, datos)
  return ApiResponse[DominioResponse](message=MensajesDominio.ACTUALIZADO, data=DominioResponse.model_validate(dominio))


@router.patch("/{dominio_id}/baja", response_model=ApiResponse[DominioResponse])
async def dar_de_baja(
  dominio_id: Annotated[int, Path(gt=0)],
  service: DominioServiceDep,
  motivo: str | None = Query(default=None, max_length=255),
) -> ApiResponse[DominioResponse]:
  dominio = await service.dar_de_baja(dominio_id, motivo)
  return ApiResponse[DominioResponse](message=MensajesDominio.DADO_DE_BAJA, data=DominioResponse.model_validate(dominio))


@router.patch("/{dominio_id}/alta", response_model=ApiResponse[DominioResponse])
async def dar_de_alta(dominio_id: Annotated[int, Path(gt=0)], service: DominioServiceDep) -> ApiResponse[DominioResponse]:
  dominio = await service.dar_de_alta(dominio_id)
  return ApiResponse[DominioResponse](message=MensajesDominio.DADO_DE_ALTA, data=DominioResponse.model_validate(dominio))
