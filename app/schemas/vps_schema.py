from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.models.enums import Ciclo, Estado, FormaPago, Vencimiento


DescripcionVps = Annotated[
  str,
  StringConstraints(
    strip_whitespace=True,
    min_length=1,
    max_length=100,
  ),
]
PrecioVps = Annotated[Decimal, Field(gt=0, max_digits=8, decimal_places=2)]
DomiciliacionVps = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
InfoAdicionalVps = Annotated[str, StringConstraints(max_length=1000)]

class VpsBase(BaseModel):
  model_config = ConfigDict(extra="forbid")

  cliente_id: Annotated[int, Field(gt=0)]
  descripcion: DescripcionVps
  dia_renovacion: Annotated[int, Field(ge=1, le=31)]


class VpsCreate(VpsBase):
  precio: PrecioVps
  domiciliacion: DomiciliacionVps | None = None
  ciclo: Ciclo = Ciclo.ANUAL
  forma_pago: FormaPago = FormaPago.RECIBO
  vencimiento: Vencimiento = Vencimiento.UN_MES
  info_adicional: InfoAdicionalVps | None = None


class VpsUpdate(BaseModel):
  cliente_id: Annotated[int, Field(gt=0)] | None = None
  descripcion: DescripcionVps | None = None
  dia_renovacion: Annotated[int, Field(ge=1, le=31)] | None = None
  precio: PrecioVps | None = None
  domiciliacion: DomiciliacionVps | None = None
  ciclo: Ciclo | None = None
  forma_pago: FormaPago | None = None
  vencimiento: Vencimiento | None = None
  info_adicional: InfoAdicionalVps | None = None

  model_config = ConfigDict(extra="forbid")

  @model_validator(mode="after")
  def validar_campos_obligatorios_no_nulos(self) -> "VpsUpdate":
    campos_no_nulos = {
      "cliente_id",
      "descripcion",
      "dia_renovacion",
      "precio",
      "ciclo",
      "forma_pago",
      "vencimiento",
    }

    for campo in campos_no_nulos & self.model_fields_set:
      if getattr(self, campo) is None:
        raise ValueError(f"{campo} no puede ser null")

    return self


class VpsResponse(VpsBase):
  id: int
  precio: Decimal
  domiciliacion: str | None
  ciclo: Ciclo
  forma_pago: FormaPago
  vencimiento: Vencimiento
  estado: Estado
  fecha_baja: datetime | None
  motivo_baja: str | None
  info_adicional: str | None
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)
