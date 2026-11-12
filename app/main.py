import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Response, status, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
from app.core.messages import MensajesComunes as m
from app.core.messages import MensajesAuth
from app.core.config import settings
from app.core.database import dispose_engine, get_engine
from app.core.exceptions import EmailYaRegistrado, CredencialesInvalidas, TokenInvalido
from app.core.exception_handlers import register_exception_handlers
from app.schemas.api_response import ApiResponse
from app.routers.cliente_router import router as cliente_router
from app.routers.dominio_router import router as dominio_router
from app.routers.hosting_router import router as hosting_router
from app.routers.vps_router import router as vps_router
from app.routers.auth_router import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  try:
    yield
  finally:
    await dispose_engine()


app = FastAPI(
  lifespan=lifespan,
  title="API de Facturación",
  description=settings.API_DESCRIPCION,
  version=settings.API_VERSION
)

register_exception_handlers(app)

@app.exception_handler(EmailYaRegistrado)
async def email_registrado_handler(request: Request, exc: EmailYaRegistrado):
  return JSONResponse(
    status_code=status.HTTP_409_CONFLICT,
    content={
      "success": False,
      "code": "EMAIL_YA_REGISTRADO",
      "message": MensajesAuth.EMAIL_YA_REGISTRADO,
    },
  )

@app.exception_handler(CredencialesInvalidas)
async def credenciales_handler(request: Request, exc: CredencialesInvalidas):
  return JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    content={
      "success": False,
      "code": "CREDENCIALES_INVALIDAS",
      "message": MensajesAuth.CREDENCIALES_INVALIDAS,
    },
    headers={"WWW-Authenticate": "Bearer"},
  )

@app.exception_handler(TokenInvalido)
async def token_invalido_handler(request: Request, exc: TokenInvalido):
  return JSONResponse(
    status_code=status.HTTP_401_UNAUTHORIZED,
    content={
      "success": False,
      "code": "TOKEN_INVALIDO",
      "message": MensajesAuth.TOKEN_INVALIDO,
    },
    headers={"WWW-Authenticate": "Bearer"},
  )

app.include_router(cliente_router, prefix="/api/v1/clientes", tags=["Clientes"])
app.include_router(dominio_router, prefix="/api/v1/dominios", tags=["Dominios"])
app.include_router(hosting_router, prefix="/api/v1/hostings", tags=["Hostings"])
app.include_router(vps_router, prefix="/api/v1/vps", tags=["VPS"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])


@app.get("/health", response_model=ApiResponse)
async def health(response: Response) -> ApiResponse:
  try:
    async with get_engine().connect() as connection:
      await connection.execute(text("SELECT 1"))
  except SQLAlchemyError:
    logger.error(m.BASE_DE_DATOS_NO_DISPONIBLE)
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ApiResponse(
      message=m.BASE_DE_DATOS_NO_DISPONIBLE,
      data={"status": "ERROR", "database": m.BASE_DE_DATOS_NO_DISPONIBLE},
      success=False,
    )

  return ApiResponse(
    message=m.OPERACION_EXITOSA,
    data={
      "status": m.OK,
      "database": m.BASE_DE_DATOS_CONECTADA,
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "version": settings.API_VERSION,
      "service": settings.API_DESCRIPCION,
    },
  )

if __name__ == "__main__":
  import uvicorn
  uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True, log_level="info") 

