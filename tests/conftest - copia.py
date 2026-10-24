# tests/conftest.py

import os
from pathlib import Path
from sqlalchemy import text

from dotenv import load_dotenv

# Antes de importar app.*: override=True para que gane a cualquier variable ya definida
load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=True)

import pytest_asyncio
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.database import Base
import app.models 

TEST_DATABASE_URL = os.environ["DATABASE_URL"]

# drop_all sobre la BD equivocada sería un desastre
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

@pytest_asyncio.fixture
async def db(engine):
  async with AsyncSession(engine, expire_on_commit=False) as session:
    yield session

  async with engine.begin() as conn:
    tablas = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    await conn.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))