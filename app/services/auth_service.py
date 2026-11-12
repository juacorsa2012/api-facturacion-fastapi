from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioCreate, Token
from app.core.exceptions import CredencialesInvalidas, EmailYaRegistrado

DUMMY_HASH = hash_password("password-falsa-para-timing")

class AuthService:
  def __init__(self, db: AsyncSession) -> None:
    self.db = db
   
  async def _obtener_por_email(self, email: str) -> Usuario | None:
    result = await self.db.execute(select(Usuario).where(Usuario.email == email))
    return result.scalar_one_or_none()

  async def obtener_por_id(self, usuario_id: int) -> Usuario | None:
    result = await self.db.execute(select(Usuario).where(Usuario.id == usuario_id))
    return result.scalar_one_or_none()

  async def registrar(self, data: UsuarioCreate) -> Usuario:
    if await self._obtener_por_email(data.email):
      raise EmailYaRegistrado()
    
    usuario = Usuario(
      email=data.email,
      nombre=data.nombre,
      password=hash_password(data.password),
    )
    self.db.add(usuario)
    await self.db.commit()
    await self.db.refresh(usuario)
    return usuario

  async def _autenticar_usuario(self, email: str, password: str) -> Usuario | None:
    usuario = await self._obtener_por_email(email.strip().lower())
    if not usuario:
      verify_password(password, DUMMY_HASH)
      return None
    if not verify_password(password, usuario.password):
      return None
    return usuario

  async def login(self, email: str, password: str) -> Token:
    usuario = await self._autenticar_usuario(email, password)
    if not usuario:
      raise CredencialesInvalidas()
    return Token(access_token=create_access_token({"sub": str(usuario.id)}))
