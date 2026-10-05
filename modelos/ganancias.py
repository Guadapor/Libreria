from database.db import obtener_conexion

def _filtro(desde):
    if desde:
        return "WHERE v.fecha >= ?", (desde,)
    return "", ()


def obtener_resumen(desde=None):
    """Totales de ventas desde una fecha ('YYYY-MM-DD HH:MM:SS'). Con desde=None cuenta todo."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    filtro, parametros = _filtro(desde)

    cursor.execute(f"""
        SELECT
            COUNT(DISTINCT v.id_venta),
            COALESCE(SUM(d.cantidad * d.precio_unitario), 0),
            COALESCE(SUM(d.cantidad), 0),
            COALESCE(SUM(CASE WHEN d.costo_unitario IS NOT NULL
                              THEN d.cantidad * d.costo_unitario END), 0),
            COALESCE(SUM(CASE WHEN d.costo_unitario IS NOT NULL
                              THEN d.cantidad * d.precio_unitario END), 0),
            COALESCE(SUM(CASE WHEN d.costo_unitario IS NULL THEN d.cantidad END), 0)
        FROM detalle_ventas d
        JOIN ventas v ON d.id_venta = v.id_venta
        {filtro}
    """, parametros)
    cantidad_ventas, ingresos, unidades, costo, ingresos_con_costo, unidades_sin_costo = cursor.fetchone()
    conexion.close()
 
    if ingresos_con_costo > 0:
        ganancia = ingresos_con_costo - costo
        margen = ganancia / ingresos_con_costo * 100
    else:
        costo = ganancia = margen = None   # no hay ventas con costo para calcular
 
    return {
        "cantidad_ventas": cantidad_ventas,
        "ingresos": ingresos,
        "unidades": unidades,
        "ticket_promedio": ingresos / cantidad_ventas if cantidad_ventas else 0,
        "costo": costo,
        "ganancia": ganancia,
        "margen": margen,
        "unidades_sin_costo": unidades_sin_costo,
    }


def obtener_libros_mas_vendidos(desde=None, limite=15):
     filtro, parametros = _filtro(desde)
     conexion = obtener_conexion()
     cursor = conexion.cursor()
     cursor.execute(f"""
        SELECT l.titulo,
               SUM(d.cantidad) AS unidades,
               SUM(d.cantidad * d.precio_unitario) AS ingresos,
               SUM(CASE WHEN d.costo_unitario IS NOT NULL
                        THEN d.cantidad * (d.precio_unitario - d.costo_unitario) END) AS ganancia
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
     return [{"titulo": f[0], "unidades": f[1], "ingresos": f[2], "ganancia": f[3]} for f in filas]

def obtener_ventas_por_vendedor(desde=None):
    filtro, parametros = _filtro(desde)
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(f"""
        SELECT u.nombre,
               COUNT(DISTINCT v.id_venta) AS cantidad,
               SUM(d.cantidad * d.precio_unitario) AS ingresos,
               SUM(CASE WHEN d.costo_unitario IS NOT NULL
                        THEN d.cantidad * (d.precio_unitario - d.costo_unitario) END) AS ganancia
        FROM ventas v
        JOIN detalle_ventas d ON d.id_venta = v.id_venta
        JOIN usuarios u ON v.id_usuario = u.id_usuario
        {filtro}
        GROUP BY u.id_usuario, u.nombre
        ORDER BY ingresos DESC
    """, parametros)
    filas = cursor.fetchall()
    conexion.close()
    return [{"vendedor": f[0], "cantidad": f[1], "ingresos": f[2], "ganancia": f[3]} for f in filas]