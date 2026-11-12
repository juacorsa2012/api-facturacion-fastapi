from functools import lru_cache
from typing import Annotated

from pydantic import Field, StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict

DatabaseURL = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class Settings(BaseSettings):
  DATABASE_URL: DatabaseURL
  API_DESCRIPCION: str
  API_VERSION: str
  PORT: int = Field(gt=0, le=65535)
  JWT_SECRET_KEY: str
  JWT_ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
  return Settings()

settings = get_settings()