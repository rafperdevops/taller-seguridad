"""Base de datos SQLite: esquema y datos de ejemplo."""

import sqlite3
import time

from .config import DB_PATH

ESQUEMA = """
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS sesiones;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS resenas;
DROP TABLE IF EXISTS facturas;
DROP TABLE IF EXISTS cupones;
DROP TABLE IF EXISTS canjes;
DROP TABLE IF EXISTS pagos;

CREATE TABLE usuarios (
    id       INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email    TEXT NOT NULL,
    rol      TEXT NOT NULL DEFAULT 'cliente',
    saldo    REAL NOT NULL DEFAULT 0,
    nota     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE sesiones (
    token      TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    creada     REAL NOT NULL
);

CREATE TABLE productos (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio      REAL NOT NULL
);

CREATE TABLE resenas (
    id          INTEGER PRIMARY KEY,
    producto_id INTEGER NOT NULL,
    usuario_id  INTEGER NOT NULL,
    texto       TEXT NOT NULL
);

CREATE TABLE facturas (
    id         INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    total      REAL NOT NULL,
    detalle    TEXT NOT NULL,
    nota       TEXT NOT NULL DEFAULT ''
);

CREATE TABLE cupones (
    codigo TEXT PRIMARY KEY,
    valor  REAL NOT NULL
);

CREATE TABLE canjes (
    id         INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    codigo     TEXT NOT NULL
);

CREATE TABLE pagos (
    id         INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    monto      REAL NOT NULL,
    concepto   TEXT NOT NULL
);
"""

USUARIOS = [
    # username, contraseña, email, rol, saldo, nota
    ("admin", "Admin#2026!segura", "admin@campusshop.test", "admin", 0, ""),
    ("ana", "sol123", "ana@campusshop.test", "cliente", 50, ""),
    ("luis", "dragon", "luis@campusshop.test", "cliente", 80, ""),
    ("maria", "princesa1", "maria@campusshop.test", "cliente", 120,
     "FLAG{md5_se_rompe_en_segundos}"),
]

PRODUCTOS = [
    ("Cuaderno argollado", "Cuaderno de 100 hojas cuadriculadas.", 12.5),
    ("Hoodie CampusShop", "Buzo con capucha, algodón perchado.", 85.0),
    ("Calculadora científica", "240 funciones, ideal para cálculo.", 64.9),
    ("Termo metálico", "Mantiene el café caliente 12 horas.", 39.0),
    ("Audífonos inalámbricos", "Bluetooth 5.3, 30 h de batería.", 99.0),
    ("Memoria USB 64 GB", "USB 3.2 para tus entregas.", 25.0),
]

FACTURAS = [
    # id, username, total, detalle, nota
    (1001, "ana", 97.5, "Cuaderno argollado + Hoodie CampusShop", ""),
    (1002, "ana", 25.0, "Memoria USB 64 GB", ""),
    (1003, "luis", 163.9, "Calculadora científica + Audífonos", "FLAG{idor_factura_ajena}"),
    (1004, "maria", 39.0, "Termo metálico", ""),
]


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Borra y vuelve a crear la base con los datos de ejemplo."""
    from .auth import hash_password

    conn = conectar()
    conn.executescript(ESQUEMA)
    for username, clave, email, rol, saldo, nota in USUARIOS:
        conn.execute(
            "INSERT INTO usuarios (username, password, email, rol, saldo, nota) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username, hash_password(clave), email, rol, saldo, nota),
        )
    conn.executemany(
        "INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?)", PRODUCTOS
    )
    for id_, username, total, detalle, nota in FACTURAS:
        conn.execute(
            "INSERT INTO facturas (id, usuario_id, total, detalle, nota) "
            "SELECT ?, id, ?, ?, ? FROM usuarios WHERE username = ?",
            (id_, total, detalle, nota, username),
        )
    conn.execute("INSERT INTO cupones VALUES ('BIENVENIDA', 100)")
    conn.execute(
        "INSERT INTO resenas (producto_id, usuario_id, texto) VALUES (2, 3, ?)",
        ("Muy abrigador, lo uso para las clases de las 6 a.m.",),
    )
    conn.commit()
    conn.close()


def ahora() -> float:
    return time.time()
