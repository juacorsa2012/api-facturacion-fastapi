"""add domain price and renewal checks

Revision ID: b6ac83d7f214
Revises: 6e4def432730
Create Date: 2026-10-24

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b6ac83d7f214"
down_revision: Union[str, Sequence[str], None] = "6e4def432730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_check_constraint(
    "ck_dominios_fecha_renovacion_valida",
    "dominios",
    "(mes_renovacion NOT IN (4, 6, 9, 11) OR dia_renovacion <= 30) "
    "AND (mes_renovacion != 2 OR dia_renovacion <= 29)",
  )
  op.create_check_constraint(
    "ck_dominios_precio_positivo",
    "dominios",
    "precio > 0",
  )


def downgrade() -> None:
  op.drop_constraint("ck_dominios_precio_positivo", "dominios", type_="check")
  op.drop_constraint("ck_dominios_fecha_renovacion_valida", "dominios", type_="check")
