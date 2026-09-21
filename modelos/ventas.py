from database.db import obtener_conexion
from datetime import datetime

def registrar_venta(id_usuario, productos):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        total = sum(
            producto['precio_unitario'] * producto['cantidad']
            for producto in productos
        )
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO ventas (fecha, total, id_usuario) VALUES (?, ?, ?)",
            (fecha, total, id_usuario)
        )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()