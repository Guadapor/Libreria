import sqlite3

def iniciar_base_datos():
    conexion = sqlite3.connect("database/libreria.db")
    cursor = conexion.cursor() 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autores (
            id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor INTEGER NOT NULL,
            categoria INTEGER NOT NULL,
            precio REAL NOT NULL,
            stock_actual INTEGER NOT NULL,
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nombre_usuario TEXT NOT NULL UNIQUE, 
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL,
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL NOT NULL,
            id_usuario INTEGER, 
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)           
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER,
            id_libro INTEGER, 
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
            FOREIGN KEY (id_libro) REFERENCES libros(id_libro)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_stock (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            detalle TEXT,             
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos y tabla 'categorias' creadas correctamente.")

    if __name__ == "__main__": 
        iniciar_base_datos()

