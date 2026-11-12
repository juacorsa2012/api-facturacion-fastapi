from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Enum, Numeric
from app.core.database import Base
from .mixins import TimestampMixin
from .enums import Estado, Empresa, FormaPago, Vencimiento

class Cliente(TimestampMixin, Base):
  __tablename__ = "clientes"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  nombre_corto: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
  nombre_largo: Mapped[str] = mapped_column(String(255), nullable=False)
  direccion: Mapped[str] = mapped_column(String(255), nullable=False)
  codigo_postal: Mapped[str] = mapped_column(String(10), nullable=False)
  poblacion: Mapped[str] = mapped_column(String(50), nullable=False)
  cif: Mapped[str] = mapped_column(String(25), nullable=False)
  domiciliacion: Mapped[str | None] = mapped_column(String(50))
  email: Mapped[str | None] = mapped_column(String(255))
  iva: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("21.00"), server_default="21.00")
  precio_desplazamiento: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("25.00"), server_default="25.00")
  precio_mano_obra: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal("55.00"), server_default="55.00")

  empresa: Mapped[Empresa] = mapped_column(
    Enum(Empresa, native_enum=False, length=5),
    nullable=False,
    default=Empresa.LEMS,
    server_default=Empresa.LEMS.value,
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

  dominios: Mapped[list["Dominio"]] = relationship(back_populates="cliente")
  hostings: Mapped[list["Hosting"]] = relationship(back_populates="cliente")
  vps: Mapped[list["Vps"]] = relationship(back_populates="cliente")
