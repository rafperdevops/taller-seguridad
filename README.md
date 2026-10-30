# 🛡️ Taller — Hackea y protege CampusShop

**Tecnologías Web · Unidad 3 · Seguridad en el desarrollo web**
Universidad Simón Bolívar — Rafael Pérez Meriño

CampusShop es una tienda universitaria **vulnerable a propósito**, hecha con
Python + FastAPI + SQLite. Contiene las 10 amenazas de la presentación de clase.
Tu trabajo: **explotar** cada falla, **entender** por qué ocurre y **corregirla**.

> ⚠️ **Aviso ético.** Todo en este laboratorio (contraseñas, claves, "banderas")
> es **falso** y vive solo en tu equipo (`localhost`). Estas técnicas se practican
> únicamente aquí o sobre sistemas para los que tengas **autorización por escrito**.
> Usarlas contra sistemas ajenos es un delito.

---

## ✅ Requisitos

- **Python 3.10 o superior** (verifica con `python3 --version`).
- Nada más: SQLite viene con Python y el laboratorio corre en WSL/Linux, macOS o Windows.
- No se usa Docker ni se instalan servicios externos.

## 🚀 Puesta en marcha (WSL / Linux / macOS)

```bash
cd taller-seguridad-web

# 1) Entorno virtual
python3 -m venv venv
source venv/bin/activate          # en Windows PowerShell: venv\Scripts\Activate.ps1

# 2) Dependencias
pip install -r requirements.txt

# 3) Levantar CampusShop
python -m campusshop
```

Abre **http://localhost:8000**. La base de datos (`campusshop.db`) se **recrea
sola** en cada arranque, así que puedes experimentar sin miedo.

### Usuarios de ejemplo

| Usuario | Contraseña          | Rol     |
|---------|---------------------|---------|
| `ana`   | `sol123`            | cliente |
| `luis`  | `dragon`            | cliente |
| `maria` | `princesa1`         | cliente |
| `admin` | (nadie te la dirá…) | admin   |

El reto 01 (SQL Injection) consiste, justamente, en entrar como `admin` sin su contraseña.

## 🧪 Las pruebas de seguridad

```bash
pytest -v
```

Al empezar verás **13 pruebas en rojo**: cada una corresponde a una vulnerabilidad.
Las **3 en verde** comprueban que la funcionalidad legítima no se rompa.
Tu objetivo en la fase de defensa es dejar **las 16 en verde** sin romper la tienda.

## 🗂️ Estructura

```
taller-seguridad-web/
├── campusshop/            # la aplicación vulnerable (FastAPI)
│   ├── rutas/             # endpoints por tema
│   ├── templates/         # vistas Jinja2
│   ├── static/            # CSS y JS
│   └── descargas/         # archivos para la sección de descargas
├── tests_seguridad/       # batería de pruebas (pytest)
├── exploits/              # scripts de apoyo para los ataques
├── atacante/              # página maliciosa para el reto de CSRF
├── GUIA_ESTUDIANTE.md     # enunciado, retos y pistas  ← EMPIEZA AQUÍ
├── requirements.txt
└── docente/               # material del profesor (no mirar hasta terminar 😉)
```

## 🎯 Las 10 amenazas en CampusShop

| # | Amenaza                         | Dónde vive en la app                         |
|---|---------------------------------|----------------------------------------------|
| 01 | Inyección SQL                  | Login y buscador de productos                |
| 02 | Cross-Site Scripting (XSS)     | Buscador, reseñas y mensajes de la URL       |
| 03 | Inyección de comandos          | Admin → "Diagnóstico de red"                 |
| 04 | IDOR                           | `GET /api/facturas/{id}`                     |
| 05 | Falta de idempotencia          | Canje de cupones (`/api/cupones/canjear`)    |
| 06 | CSRF                           | Cambio de correo (`POST /perfil/email`)      |
| 07 | Autenticación/sesiones débiles | Hash MD5, cookie insegura, sin regenerar id  |
| 08 | SSRF                           | Herramientas → "Vista previa de enlace"      |
| 09 | Path traversal                 | `GET /descargas?f=`                          |
| 10 | Configuración y datos expuestos| CORS `*`, debug, secreto en el código        |

Lee **`GUIA_ESTUDIANTE.md`** para el enunciado completo, las pistas y los entregables.
