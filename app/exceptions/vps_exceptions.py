from app.core.exceptions import NotFoundError

class VpsNoEncontradoError(NotFoundError):
  def __init__(self, vps_id: int) -> None:
    super().__init__("vps", vps_id)
