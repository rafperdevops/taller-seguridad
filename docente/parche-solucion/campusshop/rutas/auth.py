"""Inicio y cierre de sesión — versión corregida."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import COOKIE_SESION, cerrar_sesion, crear_sesion, verificar_password
from ..db import conectar
from ..plantillas import render

router = APIRouter()


@router.get("/login")
def formulario_login(request: Request):
    return render(request, "login.html")


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = conectar()
    # Consulta parametrizada: el valor nunca se concatena en el SQL.
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    # Verificación del hash en Python, con comparación en tiempo constante.
    if usuario is None or not verificar_password(password, usuario["password"]):
        return render(request, "login.html", status_code=401,
                      error="Usuario o contraseña incorrectos")

    token = crear_sesion(usuario["id"])  # nuevo ID de sesión al autenticarse
    respuesta = RedirectResponse("/perfil", status_code=303)
    respuesta.set_cookie(COOKIE_SESION, token, samesite="lax", httponly=True)
    return respuesta


@router.get("/logout")
def logout(request: Request):
    token = request.cookies.get(COOKIE_SESION)
    if token:
        cerrar_sesion(token)
    respuesta = RedirectResponse("/", status_code=303)
    respuesta.delete_cookie(COOKIE_SESION)
    return respuesta
