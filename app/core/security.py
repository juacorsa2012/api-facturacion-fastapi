import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
  return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
  now = datetime.now(timezone.utc)
  expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
  to_encode = {**data, "iat": now, "exp": expire}
  return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict | None:
  try:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
  except jwt.InvalidTokenError:
    return None