import argparse
import asyncio

from app.core.database import get_session_factory
from app.seeds.cliente_seed import seed_clientes
from app.seeds.dominio_seed import seed_dominios


async def main(tipo: str, cantidad: int) -> None:
  async with get_session_factory()() as db:
    if tipo in {"clientes", "ambos"}:
      clientes_creados = await seed_clientes(db, cantidad)
      print(f"Seed de clientes completado: {clientes_creados} cliente(s) añadido(s).")

    if tipo in {"dominios", "ambos"}:
      dominios_creados = await seed_dominios(db, cantidad)
      print(f"Seed de dominios completado: {dominios_creados} dominio(s) añadido(s).")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Genera clientes y dominios ficticios para desarrollo.")
  parser.add_argument(
    "--tipo",
    choices=("clientes", "dominios", "ambos"),
    default="clientes",
    help="Qué datos generar (predeterminado: clientes).",
  )
  parser.add_argument("--cantidad", type=int, default=10, help="Número de registros por tipo (predeterminado: 10).")
  args = parser.parse_args()
  asyncio.run(main(args.tipo, args.cantidad))


# uv run python -m app.seeds --tipo dominios --cantidad 20
# uv run python -m app.seeds --tipo ambos --cantidad 20