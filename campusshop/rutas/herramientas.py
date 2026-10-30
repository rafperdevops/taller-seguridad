"""Vista previa de enlaces y descargas."""

import urllib.request

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse

from ..auth import requiere_usuario
from ..config import PAQUETE
from ..plantillas import render

router = APIRouter()

CARPETA_DESCARGAS = PAQUETE / "descargas"


@router.get("/herramientas")
def herramientas(request: Request):
    archivos = sorted(p.name for p in CARPETA_DESCARGAS.iterdir())
    return render(request, "herramientas.html", archivos=archivos)


@router.get("/api/preview")
def vista_previa(url: str, usuario=Depends(requiere_usuario)):
    with urllib.request.urlopen(url, timeout=3) as respuesta:
        contenido = respuesta.read(3000).decode("utf-8", errors="replace")
    return {"url": url, "contenido": contenido}


@router.get("/descargas")
def descargar(f: str):
    return FileResponse(CARPETA_DESCARGAS / f)
