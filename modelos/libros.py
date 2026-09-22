from database.db import obtener_conexion

def obtener_libros():
    """Devuelve la lista de libros con el nombre del autor y categoría ya resueltos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT 1.id_libro, 1.titulo, a.nombre, c.nombre, 1.precio, 1.stock_actual
        FROM libros 1
        JOIN autores a ON 1.id_autor = a.id_autor
        JOIN categorias c ON 1.id_categoria = c.id_categoria
        ORDER BY 1.titulo
    """)
    filas = cursor.fetchall()
    conexion.close()
    return [
        {
            "id_libros": fila [0],
            "titulo": fila [1],
            "nombre_autor": fila [2],
            "nombre_categoria": fila [3],
            "precio": fila [4],
            "stock_actual": fila [5]
        }
        for fila in filas
    ]
def obtener_autores():
    """Devuelve la lista de autores (id, nombre) para usar en combos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_autor, nombre FROM autores ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return [{"id_autor": fila[0], "nombre": fila[1]} for fila in filas]
def obtener_categorias():
    """Devuelve la lista de categorías (id; nombre) para usar en combos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return [{"id_categoria": fila[0], "nombre": fila[1]} for fila in filas]
def agregar_autor(nombre):
    """Crea un autor nuevo y devuelve su id."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO autores (nombre) VALUES (?)", (nombre,))
    conexion.commit()
    id_autor = cursor.lastrowid
    conexion.close()
    return id_autor
def agregar_categoria(nombre, descripcion=None):
    """Crea una categoría nueva y devuelve su id."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)",
        (nombre, descripcion)
    )
    conexion.commit()
    id_categoria = cursor.lastrowid
    conexion.close()
    return id_categoria
def agregar_libro(titulo, id_autor, id_categoria, precio, stock_inicial=0):
    """
    Inserta un libro nuevo. Si stock_inicial > 0, además registra el movimiento de stock de tipo 'entrada' para dejar trazabilidad del ingreso inicial."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO libros (titulo, id_autor, id_categoria, precio, stock_actual)
           VALUES (?, ?, ?, ?, ?)""",
        (titulo, id_autor, id_categoria, precio, stock_inicial),
    )
    id_libro = cursor.lastrowid
    if stock_inicial > 0:
        from datetime import datetime
        cursor.execute(
            """INSERT INTO movimientos_stock (id_libro, tipo_movimiento, cantidad, fecha, detalle)
               VALUES (?, 'entrada', ?, ?, 'Ingreso inicial')""",
            (id_libro, stock_inicial, datetime.now().isoformat("%Y-%m-%d %H:%M:%S"), "Carga inicial de stock"),
        )
    conexion.commit()
    conexion.close()
    return id_libro