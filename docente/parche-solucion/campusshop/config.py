"""Configuración general de CampusShop."""

import os
import secrets
from pathlib import Path

PAQUETE = Path(__file__).resolve().parent      # carpeta campusshop/
RAIZ = PAQUETE.parent                          # carpeta del proyecto

SECRET_KEY = os.getenv("CAMPUS_SECRET", secrets.token_hex(32))
DEBUG = os.getenv("CAMPUS_DEBUG", "0") == "1"

DB_PATH = os.getenv("CAMPUS_DB", str(RAIZ / "campusshop.db"))
PUERTO_INTERNO = int(os.getenv("CAMPUS_PUERTO_INTERNO", "9001"))
