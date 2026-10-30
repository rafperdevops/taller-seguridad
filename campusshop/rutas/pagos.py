"""Saldo, cupones y pagos."""

import time

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..auth import requiere_usuario
from ..db import conectar

router = APIRouter(prefix="/api")

SALDO_VIP = 250


class Canje(BaseModel):
    codigo: str


class Pago(BaseModel):
    monto: float
    concepto: str


@router.get("/saldo")
def saldo(usuario=Depends(requiere_usuario)):
    conn = conectar()
    actual = conn.execute("SELECT saldo FROM usuarios WHERE id = ?", (usuario["id"],)).fetchone()[0]
    conn.close()
    datos = {"usuario": usuario["username"], "saldo": actual}
    if actual >= SALDO_VIP:
        datos["premio"] = "¡Cliente VIP! FLAG{carrera_de_cupones}"
    return datos


@router.post("/cupones/canjear")
def canjear_cupon(canje: Canje, usuario=Depends(requiere_usuario)):
    conn = conectar()
    cupon = conn.execute("SELECT * FROM cupones WHERE codigo = ?", (canje.codigo,)).fetchone()
    if cupon is None:
        conn.close()
        return JSONResponse({"mensaje": "Cupón inválido"}, status_code=404)

    ya_usado = conn.execute(
        "SELECT COUNT(*) FROM canjes WHERE usuario_id = ? AND codigo = ?",
        (usuario["id"], canje.codigo),
    ).fetchone()[0]
    if ya_usado:
        conn.close()
        return JSONResponse({"mensaje": "Ya usaste este cupón"}, status_code=409)

    time.sleep(0.5)  # validación con el sistema de fidelización (simulada)

    conn.execute(
        "INSERT INTO canjes (usuario_id, codigo) VALUES (?, ?)", (usuario["id"], canje.codigo)
    )
    conn.execute(
        "UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (cupon["valor"], usuario["id"])
    )
    conn.commit()
    conn.close()
    return {"mensaje": f"Cupón aplicado: +{cupon['valor']:.0f} de saldo"}


@router.post("/pagos")
def pagar(pago: Pago, usuario=Depends(requiere_usuario)):
    if pago.monto <= 0:
        return JSONResponse({"mensaje": "Monto inválido"}, status_code=400)
    conn = conectar()
    cursor = conn.execute(
        "INSERT INTO pagos (usuario_id, monto, concepto) VALUES (?, ?, ?)",
        (usuario["id"], pago.monto, pago.concepto),
    )
    conn.execute(
        "UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (pago.monto, usuario["id"])
    )
    conn.commit()
    pago_id = cursor.lastrowid
    conn.close()
    return {"id": pago_id, "monto": pago.monto, "concepto": pago.concepto}
