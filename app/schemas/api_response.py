from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
  """Respuesta estándar de la API con datos tipados."""
  message: str
  data: T | None = None
  success: bool = True
