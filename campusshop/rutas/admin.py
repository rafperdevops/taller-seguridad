"""Panel de administración."""

import subprocess

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import usuario_actual
from ..config import RAIZ
from ..db import conectar
from ..plantillas import render

router = APIRouter(prefix="/admin")

FLAG_ADMIN = "FLAG{sqli_admin_sin_contrasena}"


def _es_admin(request: Request):
    usuario = usuario_actual(request)
    return usuario if usuario is not None and usuario["rol"] == "admin" else None


def _panel(request: Request, **extra):
    conn = conectar()
    usuarios = conn.execute("SELECT id, username, email, rol, saldo FROM usuarios").fetchall()
    conn.close()
    return render(request, "admin.html", usuarios=usuarios, flag=FLAG_ADMIN, **extra)


@router.get("")
def panel(request: Request):
    if _es_admin(request) is None:
        return RedirectResponse("/login", status_code=303)
    return _panel(request)


@router.post("/diagnostico")
def diagnostico(request: Request, host: str = Form(...)):
    if _es_admin(request) is None:
        return RedirectResponse("/login", status_code=303)
    resultado = subprocess.run(
        f"ping -c 1 -W 1 {host}",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=RAIZ,
    )
    return _panel(request, host=host, salida=resultado.stdout + resultado.stderr)
