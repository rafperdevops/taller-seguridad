"""Servicio interno de metadatos (simula el 169.254.169.254 de una nube).

Escucha en 127.0.0.1:9001. En un despliegue real este servicio no sería
accesible desde Internet: solo el servidor puede llegar a él.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from .config import PUERTO_INTERNO

RESPUESTAS = {
    "/": "latest/\n",
    "/latest/meta-data/": "hostname\niam/\n",
    "/latest/meta-data/hostname": "campusshop-prod-01\n",
    "/latest/meta-data/iam/": "credenciales\n",
    "/latest/meta-data/iam/credenciales": json.dumps(
        {
            "AccessKeyId": "AKIAFALSA0123456789",
            "SecretAccessKey": "esto-es-un-secreto-de-mentiras",
            "Nota": "FLAG{ssrf_metadatos_internos}",
        },
        indent=2,
    ),
}

_iniciado = False


class _Manejador(BaseHTTPRequestHandler):
    def do_GET(self):
        cuerpo = RESPUESTAS.get(self.path)
        self.send_response(200 if cuerpo else 404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write((cuerpo or "no encontrado\n").encode())

    def log_message(self, *args):
        pass


def iniciar_servicio_interno() -> None:
    global _iniciado
    if _iniciado:
        return
    try:
        servidor = HTTPServer(("127.0.0.1", PUERTO_INTERNO), _Manejador)
    except OSError:
        return  # ya hay otro proceso usando el puerto
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    _iniciado = True
