from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.core.messages import MensajesComunes

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
  return JSONResponse(
    status_code=exc.status_code,
    content={
      "success": False,
      "code": exc.error_code,
      "message": exc.detail,
    }    
  )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
  return JSONResponse(
    status_code=422,
    content={
      "success": False,
      "code": "ERROR_VALIDACION",
      "message": MensajesComunes.DATOS_NO_VALIDOS,
      "errors": jsonable_encoder(exc.errors()),
    },
  )


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
  return JSONResponse(
    status_code=exc.status_code,
    content={
      "success": False,
      "code": f"HTTP_{exc.status_code}",
      "message": str(exc.detail),
    },
    headers=exc.headers,
  )


def register_exception_handlers(app: FastAPI) -> None:
  app.add_exception_handler(AppError, app_error_handler)
  app.add_exception_handler(RequestValidationError, validation_error_handler)
  app.add_exception_handler(StarletteHTTPException, http_error_handler)



# app.add_exception_handler(AppError, app_error_handler)
