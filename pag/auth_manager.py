#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
SISTEMA DE SEGURIDAD Y AUTENTICACIÓN — FASE 2
SEMILLERO DE INVESTIGACIÓN COTECTRONIX — COTECNOVA
Gestor de Usuarios, Roles UML, Hashing y Recuperación de Contraseñas
====================================================================
"""

import os
import sqlite3
import hashlib
import secrets
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "seguridad_usuarios.db"

# Roles oficiales modelados en los Diagramas UML
ROLES_UML = [
    "Administrador de BD",
    "Investigador / Docente",
    "Estudiante / Semillerista"
]

PREGUNTAS_SUGERIDAS = [
    "¿Cuál es el nombre del semillero de investigación?",
    "¿Cuál es la institución universitaria del proyecto?",
    "¿Cuál es el nombre de tu primera mascota?",
    "¿En qué ciudad naciste?",
    "¿Cuál es el nombre de tu profesor o mentor favorito?",
    "¿Cuál es tu color o planta favorita?"
]


def _normalize_text(text: str) -> str:
    """Normaliza texto eliminando acentos, espacios extra y convirtiendo a minúsculas."""
    if not text:
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize('NFKD', text)
    return "".join(c for c in text if not unicodedata.combining(c))


def _generate_salt() -> str:
    """Genera una sal aleatoria segura."""
    return secrets.token_hex(16)


def _hash_value(value: str, salt: str) -> str:
    """Calcula el hash SHA-256 de un valor con sal."""
    salted = f"{salt}${value}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()


def get_db_connection() -> sqlite3.Connection:
    """Obtiene una conexión a la base de datos SQLite de usuarios."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db() -> None:
    """Inicializa la tabla de usuarios y carga las cuentas iniciales basadas en el UML."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            rol TEXT NOT NULL,
            pregunta_seguridad TEXT NOT NULL,
            respuesta_hash TEXT NOT NULL,
            respuesta_salt TEXT NOT NULL,
            semillero TEXT DEFAULT 'COTECTRONIX',
            fecha_creacion TEXT NOT NULL,
            ultimo_acceso TEXT,
            activo INTEGER DEFAULT 1
        )
    """)
    conn.commit()

    # Verificar si ya existen usuarios; si no, crear las cuentas iniciales
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    if total_usuarios == 0:
        _crear_usuario_interno(
            conn,
            username="admin",
            nombre_completo="Administrador de BD — COTECTRONIX",
            password="admin123",
            rol="Administrador de BD",
            pregunta="¿Cuál es el nombre del semillero de investigación?",
            respuesta="cotectronix",
            semillero="COTECTRONIX"
        )
        _crear_usuario_interno(
            conn,
            username="investigador",
            nombre_completo="Docente Investigador COTECNOVA",
            password="investigador123",
            rol="Investigador / Docente",
            pregunta="¿Cuál es la institución universitaria del proyecto?",
            respuesta="cotecnova",
            semillero="COTECTRONIX"
        )
        _crear_usuario_interno(
            conn,
            username="estudiante",
            nombre_completo="Estudiante Semillerista",
            password="estudiante123",
            rol="Estudiante / Semillerista",
            pregunta="¿Cuál es el nombre del semillero de investigación?",
            respuesta="cotectronix",
            semillero="COTECTRONIX"
        )
        conn.commit()

    conn.close()


def _crear_usuario_interno(
    conn: sqlite3.Connection,
    username: str,
    nombre_completo: str,
    password: str,
    rol: str,
    pregunta: str,
    respuesta: str,
    semillero: str = "COTECTRONIX"
) -> None:
    """Función interna para insertar usuarios con hashing."""
    pwd_salt = _generate_salt()
    pwd_hash = _hash_value(password, pwd_salt)

    ans_salt = _generate_salt()
    norm_ans = _normalize_text(respuesta)
    ans_hash = _hash_value(norm_ans, ans_salt)

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.cursor().execute("""
        INSERT INTO usuarios (
            username, nombre_completo, password_hash, salt, rol,
            pregunta_seguridad, respuesta_hash, respuesta_salt,
            semillero, fecha_creacion, activo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        username.strip().lower(),
        nombre_completo.strip(),
        pwd_hash,
        pwd_salt,
        rol,
        pregunta.strip(),
        ans_hash,
        ans_salt,
        semillero.strip(),
        ahora
    ))


def autenticar_usuario(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Autentica un usuario contra la base de datos.
    Retorna: (exito, datos_usuario_dict, mensaje_error)
    """
    init_auth_db()
    if not username or not password:
        return False, None, "Por favor ingrese su usuario y contraseña."

    clean_user = username.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM usuarios WHERE username = ?
    """, (clean_user,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, None, "Usuario no encontrado en el sistema."

    if not row['activo']:
        conn.close()
        return False, None, "La cuenta se encuentra inactiva. Contacte al Administrador."

    # Validar contraseña
    calculated_hash = _hash_value(password, row['salt'])
    if calculated_hash != row['password_hash']:
        conn.close()
        return False, None, "Contraseña incorrecta."

    # Registrar último acceso
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE usuarios SET ultimo_acceso = ? WHERE id_usuario = ?
    """, (ahora, row['id_usuario']))
    conn.commit()

    user_data = {
        "id_usuario": row['id_usuario'],
        "username": row['username'],
        "nombre_completo": row['nombre_completo'],
        "rol": row['rol'],
        "semillero": row['semillero'],
        "fecha_creacion": row['fecha_creacion'],
        "ultimo_acceso": ahora
    }
    conn.close()
    return True, user_data, "Autenticación exitosa."


def obtener_pregunta_seguridad(username: str) -> Tuple[bool, Optional[str], str]:
    """
    Obtiene la pregunta de seguridad asignada a un usuario.
    Retorna: (exito, pregunta_texto, mensaje)
    """
    init_auth_db()
    if not username:
        return False, None, "Ingrese el nombre de usuario."

    clean_user = username.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pregunta_seguridad, activo FROM usuarios WHERE username = ?
    """, (clean_user,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, None, f"El usuario '{clean_user}' no existe en el sistema."

    if not row['activo']:
        return False, None, "La cuenta está deshabilitada. Contacte al Administrador."

    return True, row['pregunta_seguridad'], "Pregunta encontrada."


def restablecer_password_con_pregunta(
    username: str,
    respuesta_seguridad: str,
    nueva_password: str
) -> Tuple[bool, str]:
    """
    Restablece la contraseña si la respuesta secreta coincide.
    Retorna: (exito, mensaje)
    """
    init_auth_db()
    if not username or not respuesta_seguridad or not nueva_password:
        return False, "Todos los campos son obligatorios."

    if len(nueva_password) < 6:
        return False, "La nueva contraseña debe tener al menos 6 caracteres."

    clean_user = username.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_usuario, respuesta_hash, respuesta_salt, activo FROM usuarios WHERE username = ?
    """, (clean_user,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "Usuario no encontrado."

    if not row['activo']:
        conn.close()
        return False, "La cuenta está desactivada."

    # Validar respuesta
    norm_ans = _normalize_text(respuesta_seguridad)
    calculated_ans_hash = _hash_value(norm_ans, row['respuesta_salt'])

    if calculated_ans_hash != row['respuesta_hash']:
        conn.close()
        return False, "La respuesta de seguridad es incorrecta."

    # Generar nueva contraseña y salt
    new_salt = _generate_salt()
    new_hash = _hash_value(nueva_password, new_salt)

    cursor.execute("""
        UPDATE usuarios
        SET password_hash = ?, salt = ?
        WHERE id_usuario = ?
    """, (new_hash, new_salt, row['id_usuario']))
    conn.commit()
    conn.close()

    return True, "¡Contraseña actualizada con éxito! Ya puedes iniciar sesión con tu nueva contraseña."


def crear_nuevo_usuario(
    username: str,
    nombre_completo: str,
    password: str,
    rol: str,
    pregunta: str,
    respuesta: str,
    semillero: str = "COTECTRONIX"
) -> Tuple[bool, str]:
    """
    Crea un nuevo usuario en el sistema (función para Administrador de BD).
    Retorna: (exito, mensaje)
    """
    init_auth_db()
    clean_user = username.strip().lower()

    if not clean_user or not nombre_completo.strip() or not password or not respuesta.strip():
        return False, "Todos los campos marcados son obligatorios."

    if len(clean_user) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres."

    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    if rol not in ROLES_UML:
        return False, f"El rol seleccionado no es válido. Debe ser uno de: {', '.join(ROLES_UML)}"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario FROM usuarios WHERE username = ?", (clean_user,))
    if cursor.fetchone():
        conn.close()
        return False, f"El nombre de usuario '{clean_user}' ya está registrado. Elige otro."

    try:
        _crear_usuario_interno(
            conn,
            username=clean_user,
            nombre_completo=nombre_completo,
            password=password,
            rol=rol,
            pregunta=pregunta,
            respuesta=respuesta,
            semillero=semillero
        )
        conn.commit()
        conn.close()
        return True, f"Usuario '{clean_user}' creado exitosamente con el rol '{rol}'."
    except Exception as e:
        conn.close()
        return False, f"Error al crear el usuario: {str(e)}"


def listar_usuarios() -> List[Dict[str, Any]]:
    """Retorna la lista de todos los usuarios registrados (sin hashes)."""
    init_auth_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_usuario, username, nombre_completo, rol, semillero,
               pregunta_seguridad, fecha_creacion, ultimo_acceso, activo
        FROM usuarios
        ORDER BY id_usuario ASC
    """)
    rows = cursor.fetchall()
    usuarios = [dict(row) for row in rows]
    conn.close()
    return usuarios


def cambiar_estado_usuario(username: str, activo: bool) -> Tuple[bool, str]:
    """Habilita o deshabilita un usuario."""
    init_auth_db()
    clean_user = username.strip().lower()
    
    # Prevenir que se desactive el admin principal si es el único activo
    if clean_user == "admin" and not activo:
        return False, "No es posible desactivar el usuario administrador principal."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios SET activo = ? WHERE username = ?
    """, (1 if activo else 0, clean_user))
    conn.commit()
    conn.close()
    return True, f"Estado del usuario '{clean_user}' actualizado."


def admin_restablecer_password(username: str, nueva_password: str) -> Tuple[bool, str]:
    """Permite al Administrador restablecer directamente la contraseña de un usuario."""
    init_auth_db()
    if len(nueva_password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    clean_user = username.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario FROM usuarios WHERE username = ?", (clean_user,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Usuario no encontrado."

    new_salt = _generate_salt()
    new_hash = _hash_value(nueva_password, new_salt)

    cursor.execute("""
        UPDATE usuarios SET password_hash = ?, salt = ? WHERE id_usuario = ?
    """, (new_hash, new_salt, row['id_usuario']))
    conn.commit()
    conn.close()
    return True, f"Contraseña del usuario '{clean_user}' restablecida exitosamente."
