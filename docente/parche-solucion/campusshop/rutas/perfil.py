"""Perfil del usuario — versión corregida."""

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from ..auth import csrf_valido, token_csrf, usuario_actual
from ..db import conectar
from ..plantillas import render

router = APIRouter()


@router.get("/perfil")
def perfil(request: Request):
    usuario = usuario_actual(request)
    if usuario is None:
        return RedirectResponse("/login", status_code=303)
    return render(request, "perfil.html", usuario=usuario, csrf=token_csrf(request))


@router.post("/perfil/email")
def cambiar_email(request: Request, email: str = Form(...), csrf: str = Form("")):
    usuario = usuario_actual(request)
    if usuario is None:
        return RedirectResponse("/login", status_code=303)
    if not csrf_valido(request, csrf):
        raise HTTPException(status_code=403, detail="Token anti-CSRF inválido")
    conn = conectar()
    conn.execute("UPDATE usuarios SET email = ? WHERE id = ?", (email, usuario["id"]))
    conn.commit()
    conn.close()
    return RedirectResponse("/perfil?msg=Correo actualizado", status_code=303)
