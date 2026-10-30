"""Inicio y cierre de sesión."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import COOKIE_SESION, cerrar_sesion, crear_sesion, hash_password
from ..db import conectar
from ..plantillas import render

router = APIRouter()


@router.get("/login")
def formulario_login(request: Request):
    return render(request, "login.html")


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = conectar()
    sql = (
        f"SELECT * FROM usuarios WHERE username = '{username}' "
        f"AND password = '{hash_password(password)}'"
    )
    usuario = conn.execute(sql).fetchone()
    conn.close()

    if usuario is None:
        return render(request, "login.html", status_code=401,
                      error="Usuario o contraseña incorrectos")

    token = crear_sesion(usuario["id"])
    respuesta = RedirectResponse("/perfil", status_code=303)
    respuesta.set_cookie(COOKIE_SESION, token, samesite=None, httponly=False)
    return respuesta


@router.get("/logout")
def logout(request: Request):
    token = request.cookies.get(COOKIE_SESION)
    if token:
        cerrar_sesion(token)
    respuesta = RedirectResponse("/", status_code=303)
    respuesta.delete_cookie(COOKIE_SESION)
    return respuesta
