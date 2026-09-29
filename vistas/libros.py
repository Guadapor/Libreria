import tkinter as tk
from tkinter import ttk, messagebox

from modelos.libros import (
    obtener_libros,
    obtener_autores,
    obtener_categorias,
    agregar_autor,
    agregar_categoria,
    agregar_libro,
    eliminar_libro,
    LibroConVentas,
)


def abrir_libros(usuario):
    ventana = tk.Toplevel()
    ventana.title("Librería - Libros")
    ventana.geometry("640x460")

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
            tabla.insert(
                "", "end",
                iid=str(libro["id_libro"]),   # guardamos el id para poder eliminar
                values=(
                    libro["titulo"],
                    libro["autor"],
                    libro["categoria"],
                    f"{libro['precio']:.2f}",
                    libro["stock_actual"],
                ),
            )

    def abrir_formulario_nuevo_libro():
        _abrir_formulario_agregar_libro(ventana, al_guardar=cargar_tabla)

    def eliminar_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccioná un libro de la tabla.")
            return
        id_libro = int(seleccion[0])
        titulo = tabla.item(seleccion[0])["values"][0]

        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{titulo}'?\nEsta acción no se puede deshacer."):
            return
        try:
            eliminar_libro(id_libro)
        except LibroConVentas as error:
            messagebox.showwarning("No se puede eliminar", str(error))
            return
        cargar_tabla()

    marco_botones = tk.Frame(ventana)
    marco_botones.pack(pady=(0, 10))
    tk.Button(marco_botones, text="Agregar libro", width=16, command=abrir_formulario_nuevo_libro).pack(side="left", padx=5)
    if usuario["rol"] == "administrador":
        tk.Button(marco_botones, text="Eliminar libro", width=16, command=eliminar_seleccionado).pack(side="left", padx=5)
    tk.Button(marco_botones, text="Actualizar", width=16, command=cargar_tabla).pack(side="left", padx=5)
    tk.Button(marco_botones, text="Volver al menú", width=16, command=ventana.destroy).pack(side="left", padx=5)

    cargar_tabla()


def _buscar_o_crear(nombre, existentes, clave_id, crear):
    
    for e in existentes:
        if e["nombre"].lower() == nombre.lower():
            return e[clave_id]
    return crear(nombre)


def _abrir_formulario_agregar_libro(padre, al_guardar):
    ventana = tk.Toplevel(padre)
    ventana.title("Agregar libro")
    ventana.geometry("380x500")
    ventana.resizable(False, False)
    ventana.grab_set()  

    autores = obtener_autores()
    categorias = obtener_categorias()

    tk.Label(ventana, text="Nuevo libro", font=("Arial", 14, "bold")).pack(pady=15)

    tk.Label(ventana, text="Título").pack(anchor="w", padx=30)
    entrada_titulo = tk.Entry(ventana, width=38)
    entrada_titulo.pack(pady=(0, 10), padx=30)

    tk.Label(ventana, text="Autor").pack(anchor="w", padx=30)
    combo_autor = ttk.Combobox(ventana, width=35, values=[a["nombre"] for a in autores])
    combo_autor.pack(padx=30)
    tk.Label(ventana, text="Elegí uno de la lista o escribí uno nuevo",
             fg="gray", font=("Arial", 8)).pack(anchor="w", padx=30, pady=(0, 10))

    tk.Label(ventana, text="Categoría").pack(anchor="w", padx=30)
    combo_categoria = ttk.Combobox(ventana, width=35, values=[c["nombre"] for c in categorias])
    combo_categoria.pack(padx=30)
    tk.Label(ventana, text="Elegí una de la lista o escribí una nueva",
             fg="gray", font=("Arial", 8)).pack(anchor="w", padx=30, pady=(0, 10))

    tk.Label(ventana, text="Precio").pack(anchor="w", padx=30)
    entrada_precio = tk.Entry(ventana, width=38)
    entrada_precio.pack(pady=(0, 10), padx=30)

    tk.Label(ventana, text="Stock inicial").pack(anchor="w", padx=30)
    entrada_stock = tk.Entry(ventana, width=38)
    entrada_stock.insert(0, "0")
    entrada_stock.pack(pady=(0, 15), padx=30)

    def guardar():
        titulo = entrada_titulo.get().strip()
        nombre_autor = combo_autor.get().strip()
        nombre_categoria = combo_categoria.get().strip()

        if not titulo or not nombre_autor or not nombre_categoria:
            messagebox.showwarning("Datos incompletos", "Completá título, autor y categoría.")
            return

        try:
            precio = float(entrada_precio.get().strip().replace(",", "."))
            if precio < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "El precio debe ser un número mayor o igual a 0.")
            return

        try:
            stock_inicial = int(entrada_stock.get().strip() or "0")
            if stock_inicial < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "El stock debe ser un entero mayor o igual a 0.")
            return

     
        id_autor = _buscar_o_crear(nombre_autor, autores, "id_autor", agregar_autor)
        id_categoria = _buscar_o_crear(nombre_categoria, categorias, "id_categoria", agregar_categoria)

        agregar_libro(titulo, id_autor, id_categoria, precio, stock_inicial)
        messagebox.showinfo("Listo", f"'{titulo}' se agregó correctamente.")
        al_guardar()
        ventana.destroy()

    tk.Button(ventana, text="Guardar", width=20, command=guardar).pack(pady=5)