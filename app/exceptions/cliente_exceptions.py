from app.core.exceptions import AlreadyExistsError, NotFoundError

class ClienteYaExisteError(AlreadyExistsError):
  def __init__(self, nombre_corto: str) -> None:
    super().__init__("cliente", "nombre_corto", nombre_corto)

class ClienteNoEncontradoError(NotFoundError):
  def __init__(self, cliente_id: int) -> None:
    super().__init__("cliente", cliente_id)