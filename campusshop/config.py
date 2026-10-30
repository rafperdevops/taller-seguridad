"""Configuración general de CampusShop."""

import os
from pathlib import Path

PAQUETE = Path(__file__).resolve().parent      # carpeta campusshop/
RAIZ = PAQUETE.parent                          # carpeta del proyecto

SECRET_KEY = "campus-super-secreto-2026"
DEBUG = True

DB_PATH = os.getenv("CAMPUS_DB", str(RAIZ / "campusshop.db"))
PUERTO_INTERNO = int(os.getenv("CAMPUS_PUERTO_INTERNO", "9001"))
