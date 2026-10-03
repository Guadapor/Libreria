from database.db import obtener_conexion


def obtener_resumen(desde=None):
    """Totales de ventas desde una fecha ('YYYY-MM-DD HH:MM:SS'). Con desde=None cuenta todo."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    filtro = "WHERE v.fecha >= ?" if desde else ""
    parametros = (desde,) if desde else ()

    cursor.execute(f"SELECT COUNT(*), COALESCE(SUM(v.total), 0) FROM ventas v {filtro}", parametros)
    cantidad_ventas, ingresos = cursor.fetchone()

    cursor.execute(f"""
        SELECT COALESCE(SUM(d.cantidad), 0)
        FROM detalle_ventas d
        JOIN ventas v ON d.id_venta = v.id_venta
        {filtro}
    """, parametros)
    unidades = cursor.fetchone()[0]
    conexion.close()

    return {
        "cantidad_ventas": cantidad_ventas,
        "ingresos": ingresos,
        "unidades": unidades,
        "ticket_promedio": ingresos / cantidad_ventas if cantidad_ventas else 0,
    }


def obtener_libros_mas_vendidos(desde=None, limite=15):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    filtro = "WHERE v.fecha >= ?" if desde else ""
    parametros = (desde,) if desde else ()
    cursor.execute(f"""
        SELECT l.titulo, SUM(d.cantidad) AS unidades, SUM(d.cantidad * d.precio_unitario) AS ingresos
        FROM detalle_ventas d
        JOIN ventas v ON d.id_venta = v.id_venta
        JOIN libros l ON d.id_libro = l.id_libro
        {filtro}
        GROUP BY l.id_libro, l.titulo
        ORDER BY unidades DESC, ingresos DESC
        LIMIT ?
    """, parametros + (limite,))
    filas = cursor.fetchall()
    conexion.close()
    return [{"titulo": f[0], "unidades": f[1], "ingresos": f[2]} for f in filas]


def obtener_ventas_por_vendedor(desde=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    filtro = "WHERE v.fecha >= ?" if desde else ""
    parametros = (desde,) if desde else ()
    cursor.execute(f"""
        SELECT u.nombre, COUNT(*) AS cantidad, SUM(v.total) AS ingresos
        FROM ventas v
        JOIN usuarios u ON v.id_usuario = u.id_usuario
        {filtro}
        GROUP BY u.id_usuario, u.nombre
        ORDER BY ingresos DESC
    """, parametros)
    filas = cursor.fetchall()
    conexion.close()
    return [{"vendedor": f[0], "cantidad": f[1], "ingresos": f[2]} for f in filas]