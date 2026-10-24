from typing import Annotated, Self

from pydantic import Field, StringConstraints, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DatabaseURL = Annotated[
  str,
  StringConstraints(strip_whitespace=True, min_length=1),
]

class Settings(BaseSettings):
  DATABASE_URL: DatabaseURL
  API_DESCRIPCION: str
  API_VERSION: str
  PORT: int = Field(gt=0, le=65535)
  PAGINACION_LIMITE_POR_DEFECTO: int = Field(default=100, ge=1)
  PAGINACION_LIMITE_MAXIMO: int = Field(default=500, ge=1)

  @model_validator(mode="after")
  def validar_limites_paginacion(self) -> Self:
    if self.PAGINACION_LIMITE_POR_DEFECTO > self.PAGINACION_LIMITE_MAXIMO:
      raise ValueError(
        "PAGINACION_LIMITE_POR_DEFECTO no puede superar PAGINACION_LIMITE_MAXIMO"
      )
    return self
  
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8"
  )

settings = Settings()