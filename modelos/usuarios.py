import hashlib
from database.db import obtener_conexion

def encriptar (contrasena):
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
    cursor.execute("SELECT id_usuario, nombre, nombre_usuario, rol "
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

    
    