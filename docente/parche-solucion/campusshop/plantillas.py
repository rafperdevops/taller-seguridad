"""Renderizado de plantillas Jinja2."""

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .auth import usuario_actual
from .config import PAQUETE

templates = Jinja2Templates(directory=str(PAQUETE / "templates"))


def render(request: Request, nombre: str, status_code: int = 200, **contexto):
    contexto.setdefault("usuario", usuario_actual(request))
    return templates.TemplateResponse(request, nombre, contexto, status_code=status_code)
