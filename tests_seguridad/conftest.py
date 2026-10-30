"""Configuración común para las pruebas de seguridad."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path_factory):
    """Un CampusShop con base de datos nueva para cada prueba."""
    db = tmp_path_factory.mktemp("db") / "test.db"
    os.environ["CAMPUS_DB"] = str(db)

    # Importar DESPUÉS de fijar CAMPUS_DB para que use esta base.
    import importlib

    from campusshop import config

    importlib.reload(config)
    from campusshop.main import app

    with TestClient(app) as c:
        yield c


def iniciar_sesion(client, username, password):
    """Hace login y devuelve el client con la cookie puesta (o None si falla)."""
    r = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    if r.status_code == 303:
        return r.cookies.get("sesion")
    return None


# Credenciales de ejemplo (ver campusshop/db.py)
ADMIN = ("admin", "Admin#2026!segura")
ANA = ("ana", "sol123")
LUIS = ("luis", "dragon")
