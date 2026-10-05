import hashlib
import sqlite3
from database.db import obtener_conexion

ROLES = ["administrador", "vendedor"]


class UsuarioDuplicado(Exception):
    pass


class UsuarioConVentas(Exception):
    pass


class UltimoAdministrador(Exception):
    pass


def encriptar(contrasena):
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()


def crear_admin_inicial():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    cantidad = cursor.fetchone()[0]
    if cantidad == 0:
        cursor.execute(
            "INSERT INTO usuarios (nombre, nombre_usuario, contrasena, rol) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin", encriptar("admin123"), "administrador"),
        )
        conexion.commit()
    conexion.close()


def validar_login(nombre_usuario, contrasena):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id_usuario, nombre, nombre_usuario, rol "
        "FROM usuarios WHERE nombre_usuario = ? AND contrasena = ?",
        (nombre_usuario, encriptar(contrasena)),
    )
    fila = cursor.fetchone()
    conexion.close()

    if fila is None:
        return None
    return {
        "id_usuario": fila[0],
        "nombre": fila[1],
        "nombre_usuario": fila[2],
        "rol": fila[3],
    }


def obtener_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT id_usuario, nombre, nombre_usuario, rol, domicilio, telefono
        FROM usuarios
        ORDER BY nombre
    """)
    filas = cursor.fetchall()
    conexion.close()
    return [
        {
            "id_usuario": f[0],
            "nombre": f[1],
            "nombre_usuario": f[2],
            "rol": f[3],
            "domicilio": f[4] or "",
            "telefono": f[5] or "",
        }
        for f in filas
    ]


def _existe_nombre_usuario(cursor, nombre_usuario, excepto_id=None):
    cursor.execute(
        "SELECT id_usuario FROM usuarios WHERE lower(nombre_usuario) = lower(?)",
        (nombre_usuario,),
    )
    fila = cursor.fetchone()
    return fila is not None and fila[0] != excepto_id


def agregar_usuario(nombre, nombre_usuario, contrasena, rol, domicilio=None, telefono=None):
    if rol not in ROLES:
        raise ValueError("Rol inválido.")
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        if _existe_nombre_usuario(cursor, nombre_usuario):
            raise UsuarioDuplicado(f"Ya existe un usuario llamado '{nombre_usuario}'.")
        cursor.execute(
            """INSERT INTO usuarios (nombre, nombre_usuario, contrasena, rol, domicilio, telefono)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nombre, nombre_usuario, encriptar(contrasena), rol,
             domicilio or None, telefono or None),
        )
        conexion.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as error:
        conexion.rollback()
        raise UsuarioDuplicado(f"Ya existe un usuario llamado '{nombre_usuario}'.") from error
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def _cantidad_administradores(cursor, excepto_id=None):
    cursor.execute(
        "SELECT COUNT(*) FROM usuarios WHERE rol = 'administrador' AND id_usuario != ?",
        (excepto_id if excepto_id is not None else -1,),
    )
    return cursor.fetchone()[0]


def actualizar_usuario(id_usuario, nombre, nombre_usuario, rol, domicilio=None, telefono=None):
    if rol not in ROLES:
        raise ValueError("Rol inválido.")
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT rol FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        fila = cursor.fetchone()
        if fila is None:
            raise ValueError("El usuario no existe.")
        if fila[0] == "administrador" and rol != "administrador" \
                and _cantidad_administradores(cursor, id_usuario) == 0:
            raise UltimoAdministrador("No se puede quitar el rol al único administrador.")
        if _existe_nombre_usuario(cursor, nombre_usuario, excepto_id=id_usuario):
            raise UsuarioDuplicado(f"Ya existe un usuario llamado '{nombre_usuario}'.")
        cursor.execute(
            """UPDATE usuarios
               SET nombre = ?, nombre_usuario = ?, rol = ?, domicilio = ?, telefono = ?
               WHERE id_usuario = ?""",
            (nombre, nombre_usuario, rol, domicilio or None, telefono or None, id_usuario),
        )
        conexion.commit()
    except sqlite3.IntegrityError as error:
        conexion.rollback()
        raise UsuarioDuplicado(f"Ya existe un usuario llamado '{nombre_usuario}'.") from error
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def cambiar_contrasena(id_usuario, nueva_contrasena):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE usuarios SET contrasena = ? WHERE id_usuario = ?",
            (encriptar(nueva_contrasena), id_usuario),
        )
        if cursor.rowcount == 0:
            raise ValueError("El usuario no existe.")
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def eliminar_usuario(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT rol FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        fila = cursor.fetchone()
        if fila is None:
            raise ValueError("El usuario no existe.")
        if fila[0] == "administrador" and _cantidad_administradores(cursor, id_usuario) == 0:
            raise UltimoAdministrador("No se puede eliminar al único administrador.")
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_usuario = ?", (id_usuario,))
        if cursor.fetchone()[0] > 0:
            raise UsuarioConVentas(
                "Este usuario tiene ventas registradas, por eso no se puede eliminar."
            )
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()