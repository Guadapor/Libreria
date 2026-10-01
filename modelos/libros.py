import customtkinter as ctk
from tkinter import ttk, messagebox
from database.db import obtener_conexion
from datetime import datetime

def obtener_libros():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT l.id_libro, l.titulo, a.nombre, c.nombre, l.precio, l.stock_actual
        FROM libros l
        JOIN autores a ON l.id_autor = a.id_autor
        JOIN categorias c ON l.id_categoria = c.id_categoria
        ORDER BY l.titulo
    """)
    filas = cursor.fetchall()
    conexion.close()
    return [
        {
            "id_libro": fila[0],
            "titulo": fila[1],
            "autor": fila[2],
            "categoria": fila[3],
            "precio": fila[4],
            "stock_actual": fila[5],
        }
        for fila in filas
    ]
def obtener_autores():
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_autor, nombre FROM autores ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return [{"id_autor": fila[0], "nombre": fila[1]} for fila in filas]
def obtener_categorias():
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_categoria, nombre FROM categorias ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return [{"id_categoria": fila[0], "nombre": fila[1]} for fila in filas]
def agregar_autor(nombre):
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO autores (nombre) VALUES (?)", (nombre,))
    conexion.commit()
    id_autor = cursor.lastrowid
    conexion.close()
    return id_autor
def agregar_categoria(nombre, descripcion=None):
    
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
   
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """INSERT INTO libros (titulo, id_autor, id_categoria, precio, stock_actual)
               VALUES (?, ?, ?, ?, ?)""",
            (titulo, id_autor, id_categoria, precio, stock_inicial),
        )
        id_libro = cursor.lastrowid
        if stock_inicial > 0:
            cursor.execute(
                """INSERT INTO movimientos_stock (id_libro, tipo_movimiento, cantidad, fecha, detalle)
                   VALUES (?, 'entrada', ?, ?, ?)""",
                (id_libro, stock_inicial,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "Ingreso inicial"),
            )
        conexion.commit()
        return id_libro
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()

class LibroConVentas(Exception):
    pass


def eliminar_libro(id_libro):

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM detalle_ventas WHERE id_libro = ?", (id_libro,))
        if cursor.fetchone()[0] > 0:
            raise LibroConVentas(
                "Este libro ya tiene ventas registradas, por eso no se puede eliminar."
            )
        cursor.execute("DELETE FROM movimientos_stock WHERE id_libro = ?", (id_libro,))
        cursor.execute("DELETE FROM libros WHERE id_libro = ?", (id_libro,))
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()