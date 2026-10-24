from fastapi import status

from app.core.exceptions import AlreadyExistsError, AppError, NotFoundError


class HostingNoEncontradoError(NotFoundError):
  def __init__(self, hosting_id: int) -> None:
    super().__init__("hosting", hosting_id)


class HostingYaExisteError(AlreadyExistsError):
  def __init__(self, nombre: str) -> None:
    super().__init__("hosting", "nombre", nombre)


class HostingFechaRenovacionInvalidaError(AppError):
  def __init__(self, dia: int, mes: int) -> None:
    super().__init__(
      detail=f"El día {dia} no es válido para el mes {mes}",
      error_code="FECHA_RENOVACION_INVALIDA",
      status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
