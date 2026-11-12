from fastapi import status


class AppError(Exception):
  """Base para errores controlados de la aplicación."""

  def __init__(
    self,
    detail: str,
    error_code: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
  ) -> None:
    self.detail = detail
    self.error_code = error_code
    self.status_code = status_code
    super().__init__(detail)


class NotFoundError(AppError):
  """Indica que no se encontró un recurso solicitado."""

  def __init__(self, resource: str, identifier: str | int) -> None:
    super().__init__(
      detail=f"{resource} '{identifier}' no encontrado",
      error_code="RECURSO_NO_ENCONTRADO",
      status_code=status.HTTP_404_NOT_FOUND,
    )


class AlreadyExistsError(AppError):
  """Indica que ya existe un recurso con un valor único."""

  def __init__(self, resource: str, field: str, value: str) -> None:
    super().__init__(
      detail=f"Ya existe un {resource} con {field} '{value}'",
      error_code="RECURSO_DUPLICADO",
      status_code=status.HTTP_409_CONFLICT,
    )

class EmailYaRegistrado(Exception):
  pass

class CredencialesInvalidas(Exception):
  pass

class TokenInvalido(Exception):
  pass