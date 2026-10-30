"""Aplicación principal de CampusShop."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import DEBUG, PAQUETE
from .db import init_db
from .rutas import admin, auth, facturas, herramientas, pagos, perfil, tienda
from .servicio_interno import iniciar_servicio_interno


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()                     # cada arranque deja la base como nueva
    iniciar_servicio_interno()
    yield


app = FastAPI(title="CampusShop", debug=DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(PAQUETE / "static")), name="static")

for modulo in (tienda, auth, perfil, pagos, facturas, admin, herramientas):
    app.include_router(modulo.router)
