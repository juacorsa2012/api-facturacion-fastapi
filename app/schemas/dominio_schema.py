import calendar
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.models.enums import Ciclo, Estado, FormaPago, Vencimiento

NombreDominio = Annotated[
  str,
  StringConstraints(
    strip_whitespace=True,
    to_lower=True,
    min_length=1,
    max_length=100,
  ),
]
PrecioDominio = Annotated[Decimal, Field(gt=0, max_digits=8, decimal_places=2)]


def validar_dia_mes_renovacion(dia: int, mes: int) -> None:
  max_dia = calendar.monthrange(2000, mes)[1]
  if dia > max_dia:
    raise ValueError("dia_renovacion no es válido para el mes_renovacion")


class DominioBase(BaseModel):
  model_config = ConfigDict(extra="forbid")

  cliente_id: Annotated[int, Field(gt=0)]
  nombre: NombreDominio
  dia_renovacion: Annotated[int, Field(ge=1, le=31)]
  mes_renovacion: Annotated[int, Field(ge=1, le=12)]

  @model_validator(mode="after")
  def validar_fecha_renovacion(self) -> "DominioBase":
    validar_dia_mes_renovacion(self.dia_renovacion, self.mes_renovacion)
    return self


class DominioCreate(DominioBase):
  precio: PrecioDominio = Decimal("19.90")
  ciclo: Ciclo = Ciclo.ANUAL
  forma_pago: FormaPago = FormaPago.RECIBO
  vencimiento: Vencimiento = Vencimiento.UN_MES


class DominioUpdate(BaseModel):
  cliente_id: Annotated[int, Field(gt=0)] | None = None
  nombre: NombreDominio | None = None
  dia_renovacion: Annotated[int, Field(ge=1, le=31)] | None = None
  mes_renovacion: Annotated[int, Field(ge=1, le=12)] | None = None
  precio: PrecioDominio | None = None
  ciclo: Ciclo | None = None
  forma_pago: FormaPago | None = None
  vencimiento: Vencimiento | None = None

  model_config = ConfigDict(extra="forbid")

  @model_validator(mode="after")
  def validar_campos_obligatorios_no_nulos(self) -> "DominioUpdate":
    campos_no_nulos = {
      "cliente_id",
      "nombre",
      "dia_renovacion",
      "mes_renovacion",
      "precio",
      "ciclo",
      "forma_pago",
      "vencimiento",
    }

    for campo in campos_no_nulos & self.model_fields_set:
      if getattr(self, campo) is None:
        raise ValueError(f"{campo} no puede ser null")

    if {"dia_renovacion", "mes_renovacion"}.issubset(self.model_fields_set):
      validar_dia_mes_renovacion(self.dia_renovacion, self.mes_renovacion)

    return self


class DominioResponse(DominioBase):
  id: int
  precio: Decimal
  ciclo: Ciclo
  forma_pago: FormaPago
  vencimiento: Vencimiento
  estado: Estado
  fecha_baja: datetime | None
  motivo_baja: str | None
  created_at: datetime
  updated_at: datetime

  model_config = ConfigDict(from_attributes=True)
