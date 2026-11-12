from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.core.database import Base
from .mixins import TimestampMixin

class Usuario(TimestampMixin, Base):
  __tablename__ = "usuarios"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  nombre: Mapped[str] = mapped_column(String(100), nullable=False)
  email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
  password: Mapped[str] = mapped_column(String(255), nullable=False)
  