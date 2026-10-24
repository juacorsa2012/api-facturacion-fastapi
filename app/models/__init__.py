# app/models/__init__.py
from .cliente_model import Cliente
from .dominio_model import Dominio  
from .hosting_model import Hosting

__all__ = ["Cliente", "Dominio", "Hosting"]