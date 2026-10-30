"""Batería de pruebas de seguridad de CampusShop.

Con la aplicación vulnerable, estas pruebas FALLAN (en rojo).
A medida que el estudiante aplica cada mitigación, deben pasar a verde.

Ejecutar:   pytest -v
"""

import threading

from conftest import ADMIN, ANA, LUIS, iniciar_sesion


# ── 01 · Inyección SQL ────────────────────────────────────────────────────────
def test_sqli_login_no_permite_saltarse_la_contrasena(client):
    """Un payload clásico de SQLi no debe iniciar sesión."""
    token = iniciar_sesion(client, "admin' --", "lo-que-sea")
    assert token is None, "El login es vulnerable a inyección SQL"


def test_sqli_buscador_no_filtra_otras_tablas(client):
    """El buscador no debe permitir un UNION que lea la tabla usuarios."""
    r = client.get("/buscar", params={"q": "' UNION SELECT id, username, password, '1' FROM usuarios --"})
    assert "admin" not in r.text.lower() or "md5" not in r.text.lower()
    # Ningún hash MD5 (32 hex) debe aparecer en la página de resultados.
    import re

    assert not re.search(r"\b[0-9a-f]{32}\b", r.text), "El buscador filtra datos de otras tablas"


# ── 02 · XSS ───────────────────────────────────────────────────────────────────
def test_xss_buscador_escapa_la_salida(client):
    r = client.get("/buscar", params={"q": "<script>alert(1)</script>"})
    assert "<script>alert(1)</script>" not in r.text, "El buscador refleja XSS sin escapar"


def test_xss_resenas_escapa_la_salida(client):
    iniciar_sesion(client, *ANA)
    payload = "<img src=x onerror=alert(document.cookie)>"
    client.post("/productos/1/resenas", data={"texto": payload}, follow_redirects=True)
    r = client.get("/productos/1")
    assert payload not in r.text, "Las reseñas almacenan y muestran XSS sin escapar"


# ── 03 · Inyección de comandos ──────────────────────────────────────────────────
def test_inyeccion_comandos_en_diagnostico(client):
    import re

    iniciar_sesion(client, *ADMIN)
    r = client.post("/admin/diagnostico", data={"host": "127.0.0.1; echo HACKEADO"})
    # El marcador no debe aparecer en la SALIDA del comando (bloque <pre>);
    # que se refleje en el campo del formulario es inofensivo.
    salida = " ".join(re.findall(r"<pre>(.*?)</pre>", r.text, re.S))
    assert "HACKEADO" not in salida, "El diagnóstico ejecuta comandos arbitrarios"


# ── 04 · IDOR ────────────────────────────────────────────────────────────────────
def test_idor_factura_ajena(client):
    """Ana no debe poder ver la factura 1003, que es de Luis."""
    iniciar_sesion(client, *ANA)
    r = client.get("/api/facturas/1003")
    assert r.status_code in (403, 404), "IDOR: se puede leer la factura de otro usuario"


def test_factura_propia_sigue_accesible(client):
    iniciar_sesion(client, *ANA)
    r = client.get("/api/facturas/1001")
    assert r.status_code == 200, "El dueño sí debe poder ver su propia factura"


# ── 05 · Falta de idempotencia ───────────────────────────────────────────────────
def test_cupon_no_se_puede_canjear_dos_veces_en_paralelo(client):
    iniciar_sesion(client, *ANA)
    resultados = []

    def canjear():
        r = client.post("/api/cupones/canjear", json={"codigo": "BIENVENIDA"})
        resultados.append(r.status_code)

    hilos = [threading.Thread(target=canjear) for _ in range(8)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    exitos = sum(1 for c in resultados if c == 200)
    assert exitos <= 1, f"El cupón se acreditó {exitos} veces (condición de carrera)"


# ── 06 · CSRF ────────────────────────────────────────────────────────────────────
def test_csrf_cambio_de_email_requiere_token(client):
    iniciar_sesion(client, *ANA)
    # Petición sin token anti-CSRF: debe rechazarse.
    r = client.post("/perfil/email", data={"email": "atacante@evil.example"},
                    follow_redirects=False)
    assert r.status_code in (400, 403), "El cambio de correo no exige token anti-CSRF"


def test_cookie_de_sesion_es_segura(client):
    r = client.post("/login", data={"username": ANA[0], "password": ANA[1]},
                    follow_redirects=False)
    cookie = r.headers.get("set-cookie", "").lower()
    assert "httponly" in cookie, "La cookie de sesión no es HttpOnly"
    assert "samesite" in cookie, "La cookie de sesión no tiene SameSite"


# ── 07 · Autenticación débil ──────────────────────────────────────────────────────
def test_contrasenas_no_se_guardan_en_md5(client):
    """El hash guardado no debe ser MD5 sin sal (32 hex)."""
    import importlib
    import re

    from campusshop import config

    importlib.reload(config)
    from campusshop.db import conectar

    fila = conectar().execute(
        "SELECT password FROM usuarios WHERE username = 'ana'"
    ).fetchone()
    assert not re.fullmatch(r"[0-9a-f]{32}", fila[0]), "Las contraseñas se guardan en MD5"


# ── 08 · SSRF ─────────────────────────────────────────────────────────────────────
def test_ssrf_bloquea_servicio_interno(client):
    iniciar_sesion(client, *ANA)
    r = client.get("/api/preview", params={"url": "http://127.0.0.1:9001/latest/meta-data/"})
    assert r.status_code >= 400 or "meta-data" not in r.text.lower(), \
        "SSRF: la vista previa alcanza servicios internos"


# ── 09 · Path traversal ───────────────────────────────────────────────────────────
def test_path_traversal_no_sale_de_la_carpeta(client):
    r = client.get("/descargas", params={"f": "../../.env"})
    assert r.status_code >= 400 or "FLAG" not in r.text, \
        "Path traversal: se puede leer fuera de la carpeta de descargas"


def test_descarga_legitima_sigue_funcionando(client):
    r = client.get("/descargas", params={"f": "manual-usuario.txt"})
    assert r.status_code == 200 and "MANUAL" in r.text


# ── 10 · Configuración y exposición de datos ──────────────────────────────────────
def test_error_no_expone_traza_ni_secreto(client):
    r = client.get("/api/productos/99999")  # id inexistente
    assert "Traceback" not in r.text, "El error expone la traza de pila"
    assert "campus-super-secreto" not in r.text, "El error expone el SECRET_KEY"


def test_cors_no_permite_cualquier_origen(client):
    r = client.get("/api/productos/1", headers={"Origin": "http://evil.example"})
    permitido = r.headers.get("access-control-allow-origin", "")
    assert permitido != "*", "CORS permite cualquier origen con credenciales"
