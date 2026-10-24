import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.messages import MensajesComunes as m
from app.core.config import settings
from app.core.database import dispose_engine, get_engine
from app.core.exception_handlers import register_exception_handlers
from app.schemas.api_response import ApiResponse
from app.routers.cliente_router import router as cliente_router

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

app.include_router(cliente_router, prefix="/api/v1/clientes", tags=["Clientes"])


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
  uvicorn.run("app:main:app", host="0.0.0.0", port=settings.PORT, reload=True, log_level="info")
  
# py -m uvicorn app.main:app --reload