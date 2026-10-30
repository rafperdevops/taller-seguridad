"""Vista previa de enlaces y descargas — versión corregida."""

import ipaddress
import socket
import urllib.parse
import urllib.request

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from ..auth import requiere_usuario
from ..config import PAQUETE
from ..plantillas import render

router = APIRouter()

CARPETA_DESCARGAS = (PAQUETE / "descargas").resolve()
DOMINIOS_PERMITIDOS = {"example.com", "www.example.com"}


@router.get("/herramientas")
def herramientas(request: Request):
    archivos = sorted(p.name for p in CARPETA_DESCARGAS.iterdir())
    return render(request, "herramientas.html", archivos=archivos)


def _destino_es_privado(host: str) -> bool:
    """¿El host resuelve a una IP privada, loopback o de metadatos?"""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return True
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return True
    return False


@router.get("/api/preview")
def vista_previa(url: str, usuario=Depends(requiere_usuario)):
    partes = urllib.parse.urlparse(url)
    if partes.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Solo se permite http/https")
    host = partes.hostname or ""
    # Lista blanca de dominios + bloqueo de IP internas/metadatos.
    if host not in DOMINIOS_PERMITIDOS or _destino_es_privado(host):
        raise HTTPException(status_code=400, detail="Dominio no permitido")
    with urllib.request.urlopen(url, timeout=3) as respuesta:
        contenido = respuesta.read(3000).decode("utf-8", errors="replace")
    return {"url": url, "contenido": contenido}


@router.get("/descargas")
def descargar(f: str):
    # Resolver la ruta y comprobar que sigue dentro de la carpeta permitida.
    ruta = (CARPETA_DESCARGAS / f).resolve()
    if not str(ruta).startswith(str(CARPETA_DESCARGAS) + "/") or not ruta.is_file():
        raise HTTPException(status_code=403, detail="Ruta no permitida")
    return FileResponse(ruta)
