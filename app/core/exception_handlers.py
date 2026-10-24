from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

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


def register_exception_handlers(app: FastAPI) -> None:
  app.add_exception_handler(AppError, app_error_handler)
  app.add_exception_handler(RequestValidationError, validation_error_handler)



# app.add_exception_handler(AppError, app_error_handler)
