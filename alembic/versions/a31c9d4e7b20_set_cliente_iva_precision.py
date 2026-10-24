"""set cliente iva precision

Revision ID: a31c9d4e7b20
Revises: b6ac83d7f214
Create Date: 2026-10-24

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a31c9d4e7b20"
down_revision: Union[str, Sequence[str], None] = "b6ac83d7f214"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.alter_column(
    "clientes",
    "iva",
    existing_type=sa.Numeric(precision=8, scale=2),
    type_=sa.Numeric(precision=5, scale=2),
    existing_nullable=False,
    existing_server_default="21.00",
  )


def downgrade() -> None:
  op.alter_column(
    "clientes",
    "iva",
    existing_type=sa.Numeric(precision=5, scale=2),
    type_=sa.Numeric(precision=8, scale=2),
    existing_nullable=False,
    existing_server_default="21.00",
  )
