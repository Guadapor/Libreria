import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent / "libreria.db"

def obtener_conexion():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

def iniciar_base_datos():
    conexion = obtener_conexion()
    cursor = conexion.cursor() 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autores (
            id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            id_autor INTEGER NOT NULL,
            id_categoria INTEGER NOT NULL,
            precio REAL NOT NULL CHECK (precio >= 0),
            stock_actual INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
            FOREIGN KEY (id_autor) REFERENCES autores(id_autor),
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nombre_usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (rol IN ('administrador', 'vendedor')),
            domicilio TEXT,
            telefono TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL NOT NULL CHECK (total >= 0),
            id_usuario INTEGER NOT NULL,  
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)           
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_libro INTEGER NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
            FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
            FOREIGN KEY (id_libro) REFERENCES libros(id_libro)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_stock (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_libro INTEGER NOT NULL, 
            tipo_movimiento TEXT NOT NULL CHECK (tipo_movimiento IN ('entrada', 'salida')),
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            fecha TEXT NOT NULL,
            detalle TEXT,  
            FOREIGN KEY (id_libro) REFERENCES libros(id_libro)           
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos creada correctamente.")

    if __name__ == "__main__": 
        iniciar_base_datos()

