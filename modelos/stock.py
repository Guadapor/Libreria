from datetime import datetime
from database.db import obtener_conexion


def agregar_stock(id_libro, cantidad, detalle="Reposición"):
    """Suma unidades al stock de un libro y deja registrado el movimiento de entrada."""
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor a 0.")
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT 1 FROM libros WHERE id_libro = ?", (id_libro,))
        if cursor.fetchone() is None:
            raise ValueError(f"El libro con id {id_libro} no existe.")

        cursor.execute(
            "UPDATE libros SET stock_actual = stock_actual + ? WHERE id_libro = ?",
            (cantidad, id_libro),
        )
        cursor.execute(
            """INSERT INTO movimientos_stock (id_libro, tipo_movimiento, cantidad, fecha, detalle)
               VALUES (?, 'entrada', ?, ?, ?)""",
            (id_libro, cantidad,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             detalle or "Reposición"),
        )
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()