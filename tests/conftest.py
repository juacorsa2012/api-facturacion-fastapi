# tests/conftest.py
import os
from pathlib import Path

from dotenv import load_dotenv

# Antes de importar app.*: override=True para que gane a cualquier variable ya definida
load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=True)

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models
from app.core.database import Base, get_db_session
from app.main import app  

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

# Red de seguridad: drop_all/TRUNCATE sobre la BD equivocada sería un desastre
assert make_url(TEST_DATABASE_URL).database.endswith("_test"), (
  "DATABASE_URL debe apuntar a una BD cuyo nombre termine en _test"
)


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def limpiar_bd(engine):
    """Vacía todas las tablas al terminar cada test."""
    yield
    async with engine.begin() as conn:
        tablas = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
        await conn.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def db(engine):
    """Sesión para tests de service y para preparar o comprobar datos."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    """Cliente HTTP contra la app, con la dependencia de sesión apuntando a la BD de test."""
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async def _get_db_test():
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db_session] = _get_db_test
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000/api/v1"
    ) as c:
        yield c
    app.dependency_overrides.clear()