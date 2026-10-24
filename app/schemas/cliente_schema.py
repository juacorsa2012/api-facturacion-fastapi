from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from app.models.enums import Empresa, Estado, FormaPago, Vencimiento

NombreCorto = Annotated[
  str,
  StringConstraints(
    strip_whitespace=True,
    to_upper=True,
    min_length=1,
    max_length=100,
  ),
]

NombreLargo = Annotated[
  str,
  StringConstraints(
    strip_whitespace=True,
    to_upper=True,
    min_length=1,
    max_length=255,
  ),
]
Texto255 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
CodigoPostal = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10)]
Poblacion = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Cif = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=25)]
Domiciliacion = Annotated[str, StringConstraints(strip_whitespace=True, max_length=25)]
Email = Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]


class ClienteBase(BaseModel):
  nombre_corto: NombreCorto
  nombre_largo: NombreLargo
  direccion: Texto255
  codigo_postal: CodigoPostal
  poblacion: Poblacion
  cif: Cif
  domiciliacion: Domiciliacion | None = None
  email: Email | None = None


class ClienteCreate(ClienteBase):
  iva: Decimal = Decimal("21.00")
  precio_desplazamiento: Decimal = Decimal("25.00")
  precio_mano_obra: Decimal = Decimal("55.00")
  empresa: Empresa = Empresa.LEMS
  forma_pago: FormaPago = FormaPago.RECIBO
  vencimiento: Vencimiento = Vencimiento.UN_MES


class ClienteUpdate(BaseModel):
  nombre_corto: NombreCorto | None = None
  nombre_largo: NombreLargo | None = None
  direccion: Texto255 | None = None
  codigo_postal: CodigoPostal | None = None
  poblacion: Poblacion | None = None
  cif: Cif | None = None
  domiciliacion: Domiciliacion | None = None
  email: Email | None = None
  iva: Decimal | None = None
  precio_desplazamiento: Decimal | None = None
  precio_mano_obra: Decimal | None = None
  empresa: Empresa | None = None
  forma_pago: FormaPago | None = None
  vencimiento: Vencimiento | None = None

  model_config = ConfigDict(extra="forbid")

  @model_validator(mode="after")
  def validar_campos_obligatorios_no_nulos(self) -> "ClienteUpdate":
    campos_no_nulos = {
      "nombre_corto",
      "nombre_largo",
      "direccion",
      "codigo_postal",
      "poblacion",
      "cif",
      "iva",
      "precio_desplazamiento",
      "precio_mano_obra",
      "empresa",
      "forma_pago",
      "vencimiento",
    }

    for campo in campos_no_nulos & self.model_fields_set:
      if getattr(self, campo) is None:
        raise ValueError(f"{campo} no puede ser null")

    return self


class ClienteResponse(ClienteBase):
  id: int
  iva: Decimal
  precio_desplazamiento: Decimal
  precio_mano_obra: Decimal
  empresa: Empresa
  forma_pago: FormaPago
  vencimiento: Vencimiento
  estado: Estado
  fecha_baja: datetime | None
  motivo_baja: str | None
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)
