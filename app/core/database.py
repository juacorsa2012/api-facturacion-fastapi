from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
  AsyncEngine,
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

class Base(DeclarativeBase):
  pass

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
  global _engine
  if _engine is None:
    _engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=1800)
  return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
  global _session_factory
  if _session_factory is None:
    _session_factory = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
  return _session_factory


async def get_db_session() -> AsyncIterator[AsyncSession]:
  async with get_session_factory()() as session:
    try:
      yield session
    except Exception:
      await session.rollback()
      raise


async def dispose_engine() -> None:
  """Cierra el pool de conexiones"""
  global _engine, _session_factory
  if _engine is not None:
    await _engine.dispose()
  _engine = None
  _session_factory = None