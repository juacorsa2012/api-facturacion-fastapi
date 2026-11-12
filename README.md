# API de facturación

API asíncrona para gestionar clientes, dominios, servicios de hosting y VPS, construida con FastAPI, SQLAlchemy y PostgreSQL.

## Requisitos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL

## Instalación y configuración

Desde la raíz del proyecto, instala las dependencias:

```powershell
uv sync
```

Crea el archivo local de configuración y edítalo con los datos de tu entorno:

```powershell
Copy-Item .env.example .env
```

`DATABASE_URL` debe usar el driver asíncrono de PostgreSQL, por ejemplo:

```dotenv
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/facturacion
API_DESCRIPCION=API de facturación
API_VERSION=1.0.0
PORT=8000
JWT_SECRET_KEY=cambia-por-una-clave-segura-de-al-menos-32-caracteres
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Genera un valor aleatorio y privado para `JWT_SECRET_KEY` en cada entorno; no uses el texto de ejemplo como secreto real. `JWT_ALGORITHM` determina el algoritmo de firma y `ACCESS_TOKEN_EXPIRE_MINUTES` la duración del token.

No subas `.env` ni `.env.test` al repositorio. Los archivos de ejemplo no contienen credenciales reales.

## Migraciones

Aplica las migraciones a la base de datos configurada en `.env`:

```powershell
uv run alembic upgrade head
```

Para consultar la revisión actual:

```powershell
uv run alembic current
```

## Ejecutar la aplicación

Con `uv`, desde la raíz:

```powershell
uv run python main.py
```

También puedes usar `py main.py` si el intérprete seleccionado por el lanzador `py` tiene instaladas las dependencias del proyecto. La aplicación escucha en el puerto configurado en `PORT`.

Documentación interactiva de OpenAPI: `http://localhost:8000/docs` (ajusta el puerto si `PORT` tiene otro valor). Comprobación de estado: `http://localhost:8000/health`.

## Datos iniciales

Después de aplicar las migraciones, puedes generar datos ficticios con Faker. Por defecto se generan 10 clientes:

```powershell
uv run python -m app.seeds
```

Indica otra cantidad con `--cantidad`:

```powershell
uv run python -m app.seeds --cantidad 50
```

Para generar dominios asociados a clientes existentes:

```powershell
uv run python -m app.seeds --tipo dominios --cantidad 20
```

Para generar hostings asociados a clientes existentes:

```powershell
uv run python -m app.seeds --tipo hostings --cantidad 20
```

Para generar VPS asociados a clientes existentes:

```powershell
uv run python -m app.seeds --tipo vps --cantidad 20
```

Usa `--tipo todos` para generar clientes, dominios, hostings y VPS en una base vacía:

```powershell
uv run python -m app.seeds --tipo todos --cantidad 20
```

El comando crea nuevos registros al ejecutarse; evita usarlo repetidamente contra una base de datos de producción. Comprueba que `.env` apunta a la base de datos deseada antes de ejecutarlo.

## Rutas

Todas las rutas de recursos usan el prefijo `/api/v1` y devuelven la envoltura `ApiResponse`.

| Método | Ruta | Operación |
| --- | --- | --- |
| `POST` | `/api/v1/clientes/` | Crear cliente |
| `GET` | `/api/v1/clientes/` | Listar, filtrar por estado y paginar |
| `GET` | `/api/v1/clientes/{cliente_id}` | Obtener cliente |
| `GET` | `/api/v1/clientes/{cliente_id}/dominios` | Listar dominios del cliente, filtrar por estado y paginar |
| `GET` | `/api/v1/clientes/{cliente_id}/hostings` | Listar hostings del cliente, filtrar por estado y paginar |
| `GET` | `/api/v1/clientes/{cliente_id}/vps` | Listar VPS del cliente, filtrar por estado y paginar |
| `PATCH` | `/api/v1/clientes/{cliente_id}` | Actualizar parcialmente |
| `PATCH` | `/api/v1/clientes/{cliente_id}/baja` | Dar de baja (`motivo` opcional en query) |
| `PATCH` | `/api/v1/clientes/{cliente_id}/alta` | Dar de alta |
| `POST` | `/api/v1/dominios/` | Crear dominio |
| `GET` | `/api/v1/dominios/` | Listar, filtrar por estado y paginar |
| `GET` | `/api/v1/dominios/{dominio_id}` | Obtener dominio |
| `PATCH` | `/api/v1/dominios/{dominio_id}` | Actualizar parcialmente |
| `PATCH` | `/api/v1/dominios/{dominio_id}/baja` | Dar de baja (`motivo` opcional en query) |
| `PATCH` | `/api/v1/dominios/{dominio_id}/alta` | Dar de alta |
| `POST` | `/api/v1/hostings/` | Crear hosting |
| `GET` | `/api/v1/hostings/` | Listar, filtrar por estado y paginar |
| `GET` | `/api/v1/hostings/{hosting_id}` | Obtener hosting |
| `PATCH` | `/api/v1/hostings/{hosting_id}` | Actualizar parcialmente |
| `PATCH` | `/api/v1/hostings/{hosting_id}/baja` | Dar de baja (`motivo` opcional en query) |
| `PATCH` | `/api/v1/hostings/{hosting_id}/alta` | Dar de alta |
| `POST` | `/api/v1/vps/` | Crear VPS |
| `GET` | `/api/v1/vps/` | Listar, filtrar por estado y paginar |
| `GET` | `/api/v1/vps/{vps_id}` | Obtener VPS |
| `PATCH` | `/api/v1/vps/{vps_id}` | Actualizar parcialmente |
| `PATCH` | `/api/v1/vps/{vps_id}/baja` | Dar de baja (`motivo` opcional en query) |
| `PATCH` | `/api/v1/vps/{vps_id}/alta` | Dar de alta |
| `POST` | `/api/v1/auth/registrar` | Registrar usuario |
| `POST` | `/api/v1/auth/login` | Iniciar sesión y obtener un token JWT |

La paginación usa `offset` y `limit`: el desplazamiento predeterminado es `0`, el límite predeterminado es `100` y el máximo admitido es `500`. Los estados admitidos son `ALTA` y `BAJA`. Los IDs de ruta deben ser mayores que cero. El parámetro opcional `motivo` de las rutas de baja admite hasta 255 caracteres. El nombre de dominio se normaliza a minúsculas. Su precio debe ser positivo y su fecha de renovación debe existir en el calendario (se admite el 29 de febrero).

El registro requiere nombre, email válido y una contraseña de 8 a 128 caracteres que contenga letras y números. El login devuelve `access_token` y `token_type`. Aunque se emiten tokens y existe una dependencia para validar usuarios, actualmente las rutas de clientes, dominios, hostings y VPS no requieren autenticación.

## Respuestas de error

Los errores controlados de la aplicación y los errores HTTP de FastAPI devuelven `success`, `code` y `message`. Por ejemplo, un recurso inexistente responde con HTTP `404`:

```json
{
  "success": false,
  "code": "RECURSO_NO_ENCONTRADO",
  "message": "cliente '123' no encontrado"
}
```

Las solicitudes que no cumplen la validación de FastAPI responden con HTTP `422` e incluyen `errors` con las ubicaciones y tipos de error detectados:

```json
{
  "success": false,
  "code": "ERROR_VALIDACION",
  "message": "Los datos enviados no son válidos",
  "errors": [
    {
      "type": "missing",
      "loc": ["body", "nombre_corto"],
      "msg": "Field required"
    }
  ]
}
```

Los errores HTTP generados por FastAPI (por ejemplo, una ruta inexistente) usan un código `HTTP_<estado>`, como `HTTP_404`. Los errores de autenticación usan también la envoltura estándar; los 401 incluyen la cabecera `WWW-Authenticate: Bearer`.

## Tests

Prepara una base de datos PostgreSQL exclusiva para tests y crea el archivo de configuración:

```powershell
Copy-Item .env.test.example .env.test
```

Edita `DATABASE_URL` en `.env.test` para que apunte a esa base de datos. Su nombre debe terminar en `_test`, por ejemplo `facturacion_test`. La fixture comprueba ese sufijo y, al iniciar la sesión de tests, elimina y recrea las tablas; además, vacía las tablas tras cada test. **No apuntes `DATABASE_URL` a una base de datos con datos que quieras conservar.**

Ejecuta la suite:

```powershell
uv run pytest
```

La fixture de `tests/conftest.py` crea el esquema desde los modelos con `Base.metadata.create_all` y limpia las tablas después de cada test; no aplica las migraciones de Alembic. Por eso, la suite no comprueba que las migraciones construyan el mismo esquema que los modelos.

Los tests de `tests/routers/` para clientes, hostings y VPS llaman a la API por HTTP. `tests/routers/test_dominio_router.py` conserva ese nombre y ubicación, pero sus pruebas llaman directamente a `DominioService` contra la base de datos; no prueban el router HTTP. Los archivos de `tests/services/` comprueban los servicios, incluyendo casos con mocks. Los tests con mocks también activan la fixture automática de base de datos.

## Estructura

- `app/models`: modelos SQLAlchemy y enums
- `app/schemas`: schemas Pydantic de entrada y salida
- `app/services`: lógica de negocio
- `app/routers`: endpoints HTTP
- `app/core`: configuración, base de datos, dependencias, errores y paginación
- `alembic/versions`: historial de migraciones
- `tests`: tests unitarios y de integración
