"""Contraseñas y sesiones — versión corregida."""

import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request

from .config import SECRET_KEY
from .db import ahora, conectar

COOKIE_SESION = "sesion"


def hash_password(password: str) -> str:
    """Hash lento con sal usando scrypt (incluido en la librería estándar).

    Formato guardado:  scrypt$<sal_hex>$<hash_hex>
    En producción se suele usar bcrypt o Argon2; scrypt nos sirve sin dependencias.
    """
    sal = secrets.token_bytes(16)
    dk = hashlib.scrypt(password.encode(), salt=sal, n=2**14, r=8, p=1)
    return f"scrypt${sal.hex()}${dk.hex()}"


def verificar_password(password: str, guardado: str) -> bool:
    try:
        _, sal_hex, hash_hex = guardado.split("$")
        dk = hashlib.scrypt(password.encode(), salt=bytes.fromhex(sal_hex), n=2**14, r=8, p=1)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except ValueError:
        return False


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
    token = request.cookies.get(COOKIE_SESION)
    if not token:
        return None
    conn = conectar()
    fila = conn.execute(
        "SELECT u.* FROM sesiones s JOIN usuarios u ON u.id = s.usuario_id WHERE s.token = ?",
        (token,),
    ).fetchone()
    conn.close()
    return fila


def requiere_usuario(request: Request):
    usuario = usuario_actual(request)
    if usuario is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión")
    return usuario


def token_csrf(request: Request) -> str:
    """Token anti-CSRF ligado a la sesión (patrón de doble envío con HMAC)."""
    sesion = request.cookies.get(COOKIE_SESION, "")
    return hmac.new(SECRET_KEY.encode(), sesion.encode(), hashlib.sha256).hexdigest()


def csrf_valido(request: Request, enviado: str) -> bool:
    return hmac.compare_digest(token_csrf(request), enviado or "")
