"""Perfil del usuario."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import usuario_actual
from ..db import conectar
from ..plantillas import render

router = APIRouter()


@router.get("/perfil")
def perfil(request: Request):
    usuario = usuario_actual(request)
    if usuario is None:
        return RedirectResponse("/login", status_code=303)
    return render(request, "perfil.html", usuario=usuario)


@router.post("/perfil/email")
def cambiar_email(request: Request, email: str = Form(...)):
    usuario = usuario_actual(request)
    if usuario is None:
        return RedirectResponse("/login", status_code=303)
    conn = conectar()
    conn.execute("UPDATE usuarios SET email = ? WHERE id = ?", (email, usuario["id"]))
    conn.commit()
    conn.close()
    return RedirectResponse("/perfil?msg=Correo actualizado", status_code=303)
