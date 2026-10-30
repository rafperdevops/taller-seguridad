"""Catálogo, buscador y reseñas."""

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from ..auth import usuario_actual
from ..db import conectar
from ..plantillas import render

router = APIRouter()


@router.get("/")
def inicio(request: Request):
    conn = conectar()
    productos = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()
    return render(request, "index.html", productos=productos)


@router.get("/buscar")
def buscar(request: Request, q: str = ""):
    conn = conectar()
    sql = (
        "SELECT id, nombre, descripcion, precio FROM productos "
        f"WHERE nombre LIKE '%{q}%' OR descripcion LIKE '%{q}%'"
    )
    productos = conn.execute(sql).fetchall()
    conn.close()
    return render(request, "buscar.html", q=q, productos=productos)


@router.get("/productos/{producto_id}")
def ver_producto(request: Request, producto_id: int):
    conn = conectar()
    producto = conn.execute("SELECT * FROM productos WHERE id = ?", (producto_id,)).fetchone()
    resenas = conn.execute(
        "SELECT r.texto, u.username FROM resenas r JOIN usuarios u ON u.id = r.usuario_id "
        "WHERE r.producto_id = ? ORDER BY r.id",
        (producto_id,),
    ).fetchall()
    conn.close()
    if producto is None:
        return render(request, "error.html", status_code=404, mensaje="Producto no encontrado")
    return render(request, "producto.html", producto=producto, resenas=resenas)


@router.post("/productos/{producto_id}/resenas")
def crear_resena(request: Request, producto_id: int, texto: str = Form(...)):
    usuario = usuario_actual(request)
    if usuario is None:
        return RedirectResponse("/login", status_code=303)
    conn = conectar()
    conn.execute(
        "INSERT INTO resenas (producto_id, usuario_id, texto) VALUES (?, ?, ?)",
        (producto_id, usuario["id"], texto),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(f"/productos/{producto_id}", status_code=303)


@router.get("/api/productos/{producto_id}")
def api_producto(producto_id: int):
    conn = conectar()
    producto = conn.execute("SELECT * FROM productos WHERE id = ?", (producto_id,)).fetchone()
    conn.close()
    return {
        "id": producto["id"],
        "nombre": producto["nombre"],
        "descripcion": producto["descripcion"],
        "precio": producto["precio"],
    }
