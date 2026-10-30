"""Contraseñas y sesiones."""

import hashlib
import secrets

from fastapi import HTTPException, Request

from .db import ahora, conectar

COOKIE_SESION = "sesion"


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def verificar_password(password: str, guardado: str) -> bool:
    return hash_password(password) == guardado


def crear_sesion(usuario_id: int) -> str:
    token = secrets.token_hex(16)
    conn = conectar()
    conn.execute(
        "INSERT INTO sesiones (token, usuario_id, creada) VALUES (?, ?, ?)",
        (token, usuario_id, ahora()),
    )
    conn.commit()
    conn.close()
    return token


def cerrar_sesion(token: str) -> None:
    conn = conectar()
    conn.execute("DELETE FROM sesiones WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def usuario_actual(request: Request):
    """Devuelve la fila del usuario autenticado o None."""
    token = request.cookies.get(COOKIE_SESION)
    if not token:
        return None
    conn = conectar()
    fila = conn.execute(
        "SELECT u.* FROM sesiones s JOIN usuarios u ON u.id = s.usuario_id "
        "WHERE s.token = ?",
        (token,),
    ).fetchone()
    conn.close()
    return fila


def requiere_usuario(request: Request):
    """Dependencia para endpoints de API que exigen sesión."""
    usuario = usuario_actual(request)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión")
    return usuario
