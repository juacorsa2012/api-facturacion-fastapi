import argparse
import asyncio

from app.core.database import get_session_factory
from app.seeds.cliente_seed import seed_clientes
from app.seeds.dominio_seed import seed_dominios
from app.seeds.hosting_seed import seed_hostings
from app.seeds.vps_seed import seed_vps


async def main(tipo: str, cantidad: int) -> None:
  async with get_session_factory()() as db:
    if tipo in {"clientes", "todos"}:
      clientes_creados = await seed_clientes(db, cantidad)
      print(f"Seed de clientes completado: {clientes_creados} cliente(s) añadido(s).")

    if tipo in {"dominios", "todos"}:
      dominios_creados = await seed_dominios(db, cantidad)
      print(f"Seed de dominios completado: {dominios_creados} dominio(s) añadido(s).")

    if tipo in {"hostings", "todos"}:
      hostings_creados = await seed_hostings(db, cantidad)
      print(f"Seed de hostings completado: {hostings_creados} hosting(s) añadido(s).")

    if tipo in {"vps", "todos"}:
      vps_creados = await seed_vps(db, cantidad)
      print(f"Seed de VPS completado: {vps_creados} VPS añadido(s).")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Genera datos ficticios para desarrollo.")
  parser.add_argument(
    "--tipo",
    choices=("clientes", "dominios", "hostings", "vps", "todos"),
    default="clientes",
    help="Qué datos generar (predeterminado: clientes). 'todos' genera clientes, dominios, hostings y VPS.",
  )
  parser.add_argument("--cantidad", type=int, default=10, help="Número de registros por tipo (predeterminado: 10).")
  args = parser.parse_args()
  asyncio.run(main(args.tipo, args.cantidad))


# uv run python -m app.seeds --tipo dominios --cantidad 20
