from fastapi import APIRouter, status
from app.core.dependencies import AuthServiceDep
from app.schemas.api_response import ApiResponse
from app.schemas.usuario_schema import UsuarioCreate, Token, UsuarioRead, LoginRequest
from app.core.messages import MensajesAuth

router = APIRouter()

@router.post("/registrar", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[UsuarioRead])
async def registrar(datos: UsuarioCreate, service: AuthServiceDep) -> ApiResponse[UsuarioRead]:
  usuario = await service.registrar(datos)
  return ApiResponse[UsuarioRead](
    message=MensajesAuth.CREADO,
    data=UsuarioRead.model_validate(usuario),
  )  

@router.post("/login", status_code=status.HTTP_200_OK, response_model=ApiResponse[Token])
async def login(datos: LoginRequest, service: AuthServiceDep) -> ApiResponse[Token]:
  token = await service.login(datos.email, datos.password)
  return ApiResponse[Token](
    message=MensajesAuth.LOGIN_OK,
    data=token,
  )