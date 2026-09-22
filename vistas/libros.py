import tkinter as tk
from tkinter import ttk, messagebox

from modelos.libros import (
    obtener_libros,
    obtener_autores,
    obtener_categorias,
    agregar_autor,
    agregar_categoria,
    agregar_libro,
)


def abrir_libros(usuario):
    ventana = tk.Toplevel()
    ventana.title("Librería - Libros")
    ventana.geometry("640x420")

    tk.Label(ventana, text="Catálogo de libros", font=("Arial", 16, "bold")).pack(pady=10)

    columnas = ("titulo", "autor", "categoria", "precio", "stock")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=14)
    tabla.heading("titulo", text="Título")
    tabla.heading("autor", text="Autor")
    tabla.heading("categoria", text="Categoría")
    tabla.heading("precio", text="Precio")
    tabla.heading("stock", text="Stock")
    tabla.column("titulo", width=200)
    tabla.column("autor", width=140)
    tabla.column("categoria", width=120)
    tabla.column("precio", width=70, anchor="e")
    tabla.column("stock", width=60, anchor="center")
    tabla.pack(padx=10, pady=10, fill="both", expand=True)

    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)
        for libro in obtener_libros():
            tabla.insert("", "end", values=(
                libro["titulo"],
                libro["autor"],
                libro["categoria"],
                f"{libro['precio']:.2f}",
                libro["stock_actual"],
            ))

    def abrir_formulario_nuevo_libro():
        _abrir_formulario_agregar_libro(ventana, al_guardar=cargar_tabla)

    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=(0, 10))
    tk.Button(marco_botones, text="Agregar libro", width=16, command=abrir_formulario_nuevo_libro).pack(side="left", padx=5)
    tk.Button(marco_botones, text="Actualizar", width=16, command=cargar_tabla).pack(side="left", padx=5)

    cargar_tabla()


def _abrir_formulario_agregar_libro(padre, al_guardar):
    ventana = tk.Toplevel(padre)
    ventana.title("Agregar libro")
    ventana.geometry("360x420")
    ventana.resizable(False, False)
    ventana.grab_set()  # modal: bloquea la ventana de atrás hasta que se cierre

    tk.Label(ventana, text="Nuevo libro", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(ventana, text="Título").pack(anchor="w", padx=30)
    entrada_titulo = tk.Entry(ventana, width=35)
    entrada_titulo.pack(pady=(0, 10), padx=30)

    # --- Autor: combo con los existentes + opción de crear uno nuevo ---
    tk.Label(ventana, text="Autor").pack(anchor="w", padx=30)
    autores = obtener_autores()
    combo_autor = ttk.Combobox(ventana, width=32, state="readonly",
                                values=[a["nombre"] for a in autores])
    combo_autor.pack(padx=30)
    tk.Label(ventana, text="o autor nuevo (dejar el combo vacío)", fg="gray", font=("Arial", 8)).pack(anchor="w", padx=30)
    entrada_autor_nuevo = tk.Entry(ventana, width=35)
    entrada_autor_nuevo.pack(pady=(0, 10), padx=30)

    # --- Categoría: mismo esquema ---
    tk.Label(ventana, text="Categoría").pack(anchor="w", padx=30)
    categorias = obtener_categorias()
    combo_categoria = ttk.Combobox(ventana, width=32, state="readonly",
                                    values=[c["nombre"] for c in categorias])
    combo_categoria.pack(padx=30)
    tk.Label(ventana, text="o categoría nueva (dejar el combo vacío)", fg="gray", font=("Arial", 8)).pack(anchor="w", padx=30)
    entrada_categoria_nueva = tk.Entry(ventana, width=35)
    entrada_categoria_nueva.pack(pady=(0, 10), padx=30)

    tk.Label(ventana, text="Precio").pack(anchor="w", padx=30)
    entrada_precio = tk.Entry(ventana, width=35)
    entrada_precio.pack(pady=(0, 10), padx=30)

    tk.Label(ventana, text="Stock inicial").pack(anchor="w", padx=30)
    entrada_stock = tk.Entry(ventana, width=35)
    entrada_stock.insert(0, "0")
    entrada_stock.pack(pady=(0, 15), padx=30)

    def guardar():
        titulo = entrada_titulo.get().strip()
        precio_texto = entrada_precio.get().strip()
        stock_texto = entrada_stock.get().strip() or "0"

        if not titulo:
            messagebox.showwarning("Datos incompletos", "Ingresá el título del libro.")
            return

        try:
            precio = float(precio_texto)
            if precio < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "El precio debe ser un número mayor o igual a 0.")
            return

        try:
            stock_inicial = int(stock_texto)
            if stock_inicial < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "El stock inicial debe ser un número entero mayor o igual a 0.")
            return

        # Resolver autor (existente o nuevo)
        nombre_autor_nuevo = entrada_autor_nuevo.get().strip()
        if nombre_autor_nuevo:
            id_autor = agregar_autor(nombre_autor_nuevo)
        elif combo_autor.get():
            id_autor = next(a["id_autor"] for a in autores if a["nombre"] == combo_autor.get())
        else:
            messagebox.showwarning("Datos incompletos", "Elegí un autor existente o escribí uno nuevo.")
            return

        # Resolver categoría (existente o nueva)
        nombre_categoria_nueva = entrada_categoria_nueva.get().strip()
        if nombre_categoria_nueva:
            id_categoria = agregar_categoria(nombre_categoria_nueva)
        elif combo_categoria.get():
            id_categoria = next(c["id_categoria"] for c in categorias if c["nombre"] == combo_categoria.get())
        else:
            messagebox.showwarning("Datos incompletos", "Elegí una categoría existente o escribí una nueva.")
            return

        agregar_libro(titulo, id_autor, id_categoria, precio, stock_inicial)
        messagebox.showinfo("Listo", f"'{titulo}' se agregó correctamente.")
        al_guardar()
        ventana.destroy()

    tk.Button(ventana, text="Guardar", width=20, command=guardar).pack(pady=5)