from datetime import datetime
from database.db import obtener_conexion
class StockInsuficiente(Exception):
    """Se lanza cuando se intenta vender más libros de los que hay en stock."""
    pass
def registrar_venta(id_usuario, items):
    """
    Registra una venta completa.
    items: lista de dicts con la forma:
         {"id_libro": int, "cantidad": int, "precio_unitario": float}
    Inserta en 'ventas' y en 'detalles_venta', descuenta stock en 'libros'. y deja constancia en 'movimientos_stock'.
    Todo dentro de una misma transacción. si algo falla, no se guarda nada."""
    if not items:
        raise ValueError("La venta necesita al menos un libro.")
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        "Verificar stock disponible antes de tocar nada"
        for item in items:
            cursor.execute( "SELECT titulo, stock_actual FROM libros WHERE id_libro = ?", (item["id_libro"],),)
            fila = cursor. fetchone()
            if fila is None:
                raise ValueError(f"Este libro con id {item['id_libro']} no existe.")
            titulo, stock_actual = fila
            if item["cantidad"] > stock_actual:
                raise StockInsuficiente(
                    f"Hay insuficiente para '{titulo}': estaría quedando {stock_actual},"
                    f"se pidieron {item['cantidad']}.")
        total = sum(item["cantidad"] * item["precio_unitario"] for item in items)
        fecha = datetime.now().isoformat("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO ventas (fecha, total, id_usuario) VALUES(?, ?, ?)",
            (fecha, total, id_usuario),
        )
        id_venta = cursor.lastrowid
        for item in items:
            cursor.execute(
                """INSERT INTO detalle_ventas (id_ventas, id_libro, cantidad, precio_unitario)
                   VALUES (?, ?, ?, ?)""",
                (id_venta, item["id_libro"], item["cantidad"], item["precio_unitario"]),
            )

            cursor.execute(
                "UPDATE libros SET stock_actual = stock_actual - ? WHERE id_libro = ?",
                (item["cantidad"], item["id_libro"]),
            )
            cursor.execute(
                """INSERT INTO movimientos_stock (id_libro, tipo_movimiento, cantidad, fecha, detalle) VALUES (?, 'salida', ?, ?, ?)""",
                (item["id_libro"], item["cantidad"], fecha, f"Venta #{id_venta}"),
            )
        conexion.commit()
        return id_venta
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

def obtener_ventas():
    """Devuelve la lista de ventas con el nombre del vendedor que las hizo."""      
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT v.id_venta, v.fecha, v.total, u.nombre
           FROM ventas v
           JOIN usuarios u ON v.id_usuario = u.id_usuario
           ORDER BY v.fecha DESC
    """)
    filas = cursor.fetchall()
    conexion.close()

    return [
        {"id_venta": fila[0], "fecha": fila[1], "total": fila[2], "vendedor": fila[3]}
        for fila in filas
    ]
def obtener_detalle_venta(id_venta):
    """Devuelve el detalle (libros, cantidades, precios) de una venta en específica."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT l.titulo, d.cantidad, d.precio_unitario
        FROM detalle_ventas d
        JOIN libros l ON d.id_libro = l.id_libro
        WHERE d.id_venta = ?)
    """, (id_venta,))
    filas = cursor.fetchall()
    conexion.close()

    return [ 
        {"titulo": fila[0], "cantidad": fila[1], "precio_unitario": fila[2]}
        for fila in filas
    ]