from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Enum, Numeric, CheckConstraint, ForeignKey
from .mixins import TimestampMixin
from .enums import Estado, FormaPago, Vencimiento, Ciclo
from app.core.database import Base

class Dominio(TimestampMixin, Base):
  __tablename__ = "dominios"

  __table_args__ = (
    CheckConstraint("dia_renovacion BETWEEN 1 AND 31", name="ck_dominios_dia_renovacion_rango"),
    CheckConstraint("mes_renovacion BETWEEN 1 AND 12", name="ck_dominios_mes_renovacion_rango"),
    CheckConstraint(
      "(mes_renovacion NOT IN (4, 6, 9, 11) OR dia_renovacion <= 30) "
      "AND (mes_renovacion != 2 OR dia_renovacion <= 29)",
      name="ck_dominios_fecha_renovacion_valida",
    ),
    CheckConstraint("precio > 0", name="ck_dominios_precio_positivo"),
  )

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False, index=True)
  nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
  dia_renovacion: Mapped[int] = mapped_column(Integer, nullable=False)
  mes_renovacion: Mapped[int] = mapped_column(Integer, nullable=False)
  precio: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("19.90"), server_default="19.90", nullable=False)

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

  cliente: Mapped["Cliente"] = relationship(back_populates="dominios")
