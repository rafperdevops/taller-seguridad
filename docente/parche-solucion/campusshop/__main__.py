"""Arranca CampusShop con:  python -m campusshop"""

import uvicorn

from .config import PAQUETE

if __name__ == "__main__":
    print("\n  CampusShop corriendo en  http://localhost:8000\n")
    uvicorn.run(
        "campusshop.main:app",
        host="127.0.0.1",          # solo accesible desde este equipo
        port=8000,
        reload=True,
        reload_dirs=[str(PAQUETE)],
    )
