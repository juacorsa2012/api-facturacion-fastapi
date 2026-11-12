# schemas/usuario.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Annotated
from pydantic import StringConstraints

Nombre = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]

class UsuarioCreate(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr
  nombre: Nombre
  password: str = Field(min_length=8, max_length=128)

  @field_validator("email")
  @classmethod
  def normalizar_email(cls, v: str) -> str:
    return v.strip().lower()

  @field_validator("nombre")
  @classmethod
  def limpiar_nombre(cls, v: str) -> str:
    return v.strip()

  @field_validator("password")
  @classmethod
  def validar_password(cls, v: str) -> str:
    if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
      raise ValueError("La contraseña debe contener letras y números")
    return v


class UsuarioRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  email: EmailStr
  nombre: str

class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"

class LoginRequest(BaseModel):
  model_config = ConfigDict(extra="forbid")

  email: EmailStr
  password: str = Field(min_length=8, max_length=128)

  @field_validator("email")
  @classmethod
  def normalizar_email(cls, v: str) -> str:
    return v.strip().lower()
