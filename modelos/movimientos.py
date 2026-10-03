from database.db import obtener_conexion


def obtener_movimientos():
    """Devuelve todos los movimientos de stock, del más reciente al más antiguo."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT m.id_movimiento, m.fecha, l.titulo, m.tipo_movimiento, m.cantidad, m.detalle
        FROM movimientos_stock m
        JOIN libros l ON m.id_libro = l.id_libro
        ORDER BY m.fecha DESC, m.id_movimiento DESC
    """)
    filas = cursor.fetchall()
    conexion.close()
    return [
        {
            "id_movimiento": fila[0],
            "fecha": fila[1],
            "titulo": fila[2],
            "tipo": fila[3],
            "cantidad": fila[4],
            "detalle": fila[5] or "",
        }
        for fila in filas
    ]