"""Facturas del usuario."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from ..auth import requiere_usuario, usuario_actual
from ..db import conectar
from ..plantillas import render

router = APIRouter()


@router.get("/facturas")
def mis_facturas(request: Request):
    usuario = usuario_actual(request)
    if usuario is None:
        return RedirectResponse("/login", status_code=303)
    conn = conectar()
    facturas = conn.execute(
        "SELECT id, total, detalle FROM facturas WHERE usuario_id = ?", (usuario["id"],)
    ).fetchall()
    conn.close()
    return render(request, "facturas.html", facturas=facturas)


@router.get("/api/facturas/{factura_id}")
def ver_factura(factura_id: int, usuario=Depends(requiere_usuario)):
    conn = conectar()
    factura = conn.execute("SELECT * FROM facturas WHERE id = ?", (factura_id,)).fetchone()
    conn.close()
    if factura is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    # Autorización por objeto: la factura debe pertenecer a quien la pide.
    if factura["usuario_id"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="No es tu factura")
    return dict(factura)
