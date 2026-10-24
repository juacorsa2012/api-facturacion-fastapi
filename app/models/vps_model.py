from datetime import datetime

from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Enum, Numeric, CheckConstraint, ForeignKey

from .mixins import TimestampMixin
from .enums import Estado, FormaPago, Vencimiento, Ciclo
from app.core.database import Base

class Vps(TimestampMixin, Base):
  __tablename__ = "vps"

  __table_args__ = (
    CheckConstraint("dia_renovacion BETWEEN 1 AND 31", name="ck_vps_dia_renovacion_rango"),    
    CheckConstraint("precio > 0", name="ck_vps_precio_positivo"),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
  descripcion: Mapped[str] = mapped_column(String(100), nullable=False)
  dia_renovacion: Mapped[int] = mapped_column(Integer, nullable=False)
  precio: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
  domiciliacion: Mapped[str | None] = mapped_column(String(50))

  ciclo: Mapped[Ciclo] = mapped_column(
    Enum(Ciclo, native_enum=False, length=15),
    nullable=False,
    default=Ciclo.ANUAL,
    server_default=Ciclo.ANUAL.value,
    index=True
  )

  forma_pago: Mapped[FormaPago] = mapped_column(
    Enum(FormaPago, native_enum=False, length=15),
    nullable=False,
    default=FormaPago.RECIBO,
    server_default=FormaPago.RECIBO.value,
    index=True
  )

  vencimiento: Mapped[Vencimiento] = mapped_column(
    Enum(Vencimiento, native_enum=False, length=20),
    nullable=False,
    default=Vencimiento.UN_MES,
    server_default=Vencimiento.UN_MES.value,
    index=True
  )

  estado: Mapped[Estado] = mapped_column(
    Enum(Estado, native_enum=False, length=20),
    nullable=False,
    default=Estado.ALTA,
    server_default=Estado.ALTA.value,
    index=True,
  )
  fecha_baja: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  motivo_baja: Mapped[str | None] = mapped_column(String(255))
  info_adicional: Mapped[str | None] = mapped_column(String(1000))
  cliente: Mapped["Cliente"] = relationship(back_populates="vps")

