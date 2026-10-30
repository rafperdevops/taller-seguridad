"""Aplicación principal de CampusShop — versión corregida."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import DEBUG, PAQUETE
from .db import init_db
from .rutas import admin, auth, facturas, herramientas, pagos, perfil, tienda
from .servicio_interno import iniciar_servicio_interno

ORIGENES = ["http://localhost:8000", "http://127.0.0.1:8000"]

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data:; object-src 'none'; base-uri 'none'"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    iniciar_servicio_interno()
    yield


app = FastAPI(title="CampusShop", debug=DEBUG, lifespan=lifespan)

# CORS acotado a los orígenes propios (no "*" con credenciales).
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def cabeceras_seguridad(request: Request, call_next):
    respuesta = await call_next(request)
    respuesta.headers["Content-Security-Policy"] = CSP
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "no-referrer"
    return respuesta


@app.exception_handler(Exception)
async def error_generico(request: Request, exc: Exception):
    # Nunca exponer la traza ni secretos al usuario.
    return JSONResponse({"detail": "Error interno"}, status_code=500)


app.mount("/static", StaticFiles(directory=str(PAQUETE / "static")), name="static")

for modulo in (tienda, auth, perfil, pagos, facturas, admin, herramientas):
    app.include_router(modulo.router)
