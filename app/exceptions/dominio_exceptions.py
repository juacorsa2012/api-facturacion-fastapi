from fastapi import status

from app.core.exceptions import AppError, NotFoundError, AlreadyExistsError

class DominioNoEncontradoError(NotFoundError):
  def __init__(self, dominio_id: int) -> None:
    super().__init__("dominio", dominio_id)

class DominioYaExisteError(AlreadyExistsError):
  def __init__(self, nombre: str) -> None:
    super().__init__("dominio", "nombre", nombre)


class DominioFechaRenovacionInvalidaError(AppError):
  def __init__(self, dia: int, mes: int) -> None:
    super().__init__(
      detail=f"El día {dia} no es válido para el mes {mes}",
      error_code="FECHA_RENOVACION_INVALIDA",
      status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
