import math
import customtkinter as ctk
from tkinter import ttk, messagebox

from vistas.estilos import aplicar_estilo_tabla
from modelos.libros import (
    obtener_libros,
    obtener_autores,
    obtener_categorias,
    agregar_autor,
    agregar_categoria,
    agregar_libro,
    eliminar_libro,
    actualizar_costo,
    LibroConVentas,
)


def _texto_costo(costo):
    return "—" if costo is None else f"{costo:.2f}"


def _leer_costo(texto):
    """Devuelve un float, None si el campo está vacío, o lanza ValueError si no es válido."""
    texto = texto.strip().replace(",", ".")
    if texto == "":
        return None
    valor = float(texto)
    if not math.isfinite(valor) or valor < 0:
        raise ValueError
    return valor


def abrir_libros(usuario):
    es_admin = usuario["rol"] == "administrador"

    aplicar_estilo_tabla()
    ventana = ctk.CTkToplevel()
    ventana.title("Librería - Libros")
    ventana.geometry("800x500")
    ventana.after(100, ventana.lift)

    ctk.CTkLabel(ventana, text="Catálogo de libros", font=("Arial", 18, "bold")).pack(pady=10)

    # Los botones van abajo y se empaquetan primero para que la tabla no los empuje fuera
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(side="bottom", pady=(0, 12))

    # El costo solo lo ve el administrador
    columnas = ["titulo", "autor", "categoria"] + (["costo"] if es_admin else []) + ["precio", "stock"]
    textos = {"titulo": "Título", "autor": "Autor", "categoria": "Categoría",
              "costo": "Costo", "precio": "Precio", "stock": "Stock"}
    anchos = {"titulo": 240, "autor": 160, "categoria": 120, "costo": 80, "precio": 80, "stock": 60}
    anclas = {"costo": "e", "precio": "e", "stock": "center"}

    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=14)
    for col in columnas:
        tabla.heading(col, text=textos[col])
        tabla.column(col, width=anchos[col], anchor=anclas.get(col, "w"))
    tabla.pack(padx=10, pady=10, fill="both", expand=True)

    datos = {}  # id_libro -> datos del libro, para no volver a consultar al editar

    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)
        datos.clear()
        for libro in obtener_libros():
            datos[libro["id_libro"]] = libro
            fila = {
                "titulo": libro["titulo"],
                "autor": libro["autor"],
                "categoria": libro["categoria"],
                "costo": _texto_costo(libro["costo"]),
                "precio": f"{libro['precio']:.2f}",
                "stock": libro["stock_actual"],
            }
            tabla.insert("", "end", iid=str(libro["id_libro"]),
                         values=[fila[c] for c in columnas])

    def abrir_formulario_nuevo_libro():
        _abrir_formulario_agregar_libro(ventana, al_guardar=cargar_tabla, es_admin=es_admin)

    def editar_costo_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccioná un libro de la tabla.")
            return
        _abrir_formulario_costo(ventana, datos[int(seleccion[0])], al_guardar=cargar_tabla)

    def eliminar_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccioná un libro de la tabla.")
            return
        id_libro = int(seleccion[0])
        titulo = datos[id_libro]["titulo"]

        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{titulo}'?\nEsta acción no se puede deshacer."):
            return
        try:
            eliminar_libro(id_libro)
        except LibroConVentas as error:
            messagebox.showwarning("No se puede eliminar", str(error))
            return
        cargar_tabla()

    ctk.CTkButton(marco_botones, text="Agregar libro", width=125, command=abrir_formulario_nuevo_libro).pack(side="left", padx=4)
    if es_admin:
        ctk.CTkButton(marco_botones, text="Editar costo", width=125,
                      command=editar_costo_seleccionado).pack(side="left", padx=4)
        ctk.CTkButton(marco_botones, text="Eliminar libro", width=125,
                      fg_color="#8B2E2E", hover_color="#6E2323",
                      command=eliminar_seleccionado).pack(side="left", padx=4)
    ctk.CTkButton(marco_botones, text="Actualizar", width=125, command=cargar_tabla).pack(side="left", padx=4)
    ctk.CTkButton(marco_botones, text="Volver al menú", width=125, command=ventana.destroy).pack(side="left", padx=4)

    cargar_tabla()


def _buscar_o_crear(nombre, existentes, clave_id, crear):
    for e in existentes:
        if e["nombre"].lower() == nombre.lower():
            return e[clave_id]
    return crear(nombre)


def _abrir_formulario_costo(padre, libro, al_guardar):
    ventana = ctk.CTkToplevel(padre)
    ventana.title("Editar costo")
    ventana.geometry("440x370")
    ventana.resizable(False, False)
    ventana.after(100, ventana.lift)
    ventana.after(150, ventana.grab_set)

    ctk.CTkLabel(ventana, text="Costo del libro", font=("Arial", 18, "bold")).pack(pady=(15, 5))
    ctk.CTkLabel(ventana, text=libro["titulo"], wraplength=380).pack(padx=30)
    ctk.CTkLabel(ventana, text=f"Precio de venta: ${libro['precio']:.2f}",
                 text_color="gray").pack(pady=(0, 12))

    ctk.CTkLabel(ventana, text="Costo (lo que te cuesta cada unidad)").pack(anchor="w", padx=30)
    entrada_costo = ctk.CTkEntry(ventana, width=380)
    if libro["costo"] is not None:
        entrada_costo.insert(0, f"{libro['costo']:.2f}")
    entrada_costo.pack(padx=30, pady=(0, 12))

    aplicar_previas = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        ventana, variable=aplicar_previas,
        text="Aplicar también a ventas anteriores\nde este libro que no tengan costo",
    ).pack(anchor="w", padx=30, pady=(0, 15))

    def guardar():
        try:
            costo = _leer_costo(entrada_costo.get())
        except ValueError:
            messagebox.showwarning("Dato inválido", "El costo debe ser un número mayor o igual a 0.")
            return
        if costo is None:
            messagebox.showwarning("Datos incompletos", "Ingresá el costo.")
            return
        try:
            completadas = actualizar_costo(libro["id_libro"], costo, aplicar_previas.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        mensaje = "Costo actualizado."
        if completadas:
            mensaje += f"\nSe completó el costo en {completadas} línea(s) de ventas anteriores."
        messagebox.showinfo("Listo", mensaje)
        al_guardar()
        ventana.destroy()

    ctk.CTkButton(ventana, text="Guardar", width=160, height=36, command=guardar).pack(pady=5)


def _abrir_formulario_agregar_libro(padre, al_guardar, es_admin):
    ventana = ctk.CTkToplevel(padre)
    ventana.title("Agregar libro")
    ventana.geometry("400x670" if es_admin else "400x600")
    ventana.resizable(False, False)
    ventana.after(100, ventana.lift)
    ventana.after(150, ventana.grab_set)

    autores = obtener_autores()
    categorias = obtener_categorias()

    ctk.CTkLabel(ventana, text="Nuevo libro", font=("Arial", 18, "bold")).pack(pady=15)

    ctk.CTkLabel(ventana, text="Título").pack(anchor="w", padx=30)
    entrada_titulo = ctk.CTkEntry(ventana, width=340)
    entrada_titulo.pack(pady=(0, 10), padx=30)

    ctk.CTkLabel(ventana, text="Autor").pack(anchor="w", padx=30)
    combo_autor = ctk.CTkComboBox(ventana, width=340, values=[a["nombre"] for a in autores])
    combo_autor.set("")
    combo_autor.pack(padx=30)
    ctk.CTkLabel(ventana, text="Elegí uno de la lista o escribí uno nuevo",
                 text_color="gray", font=("Arial", 11)).pack(anchor="w", padx=30, pady=(0, 10))

    ctk.CTkLabel(ventana, text="Categoría").pack(anchor="w", padx=30)
    combo_categoria = ctk.CTkComboBox(ventana, width=340, values=[c["nombre"] for c in categorias])
    combo_categoria.set("")
    combo_categoria.pack(padx=30)
    ctk.CTkLabel(ventana, text="Elegí una de la lista o escribí una nueva",
                 text_color="gray", font=("Arial", 11)).pack(anchor="w", padx=30, pady=(0, 10))

    entrada_costo = None
    if es_admin:
        ctk.CTkLabel(ventana, text="Costo (lo que te cuesta a vos)").pack(anchor="w", padx=30)
        entrada_costo = ctk.CTkEntry(ventana, width=340,
                                     placeholder_text="Opcional, se puede cargar después")
        entrada_costo.pack(pady=(0, 10), padx=30)

    ctk.CTkLabel(ventana, text="Precio de venta").pack(anchor="w", padx=30)
    entrada_precio = ctk.CTkEntry(ventana, width=340)
    entrada_precio.pack(pady=(0, 10), padx=30)

    ctk.CTkLabel(ventana, text="Stock inicial").pack(anchor="w", padx=30)
    entrada_stock = ctk.CTkEntry(ventana, width=340)
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
            if not math.isfinite(precio) or precio < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "El precio debe ser un número mayor o igual a 0.")
            return

        costo = None
        if entrada_costo is not None:
            try:
                costo = _leer_costo(entrada_costo.get())
            except ValueError:
                messagebox.showwarning("Dato inválido", "El costo debe ser un número mayor o igual a 0.")
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

        agregar_libro(titulo, id_autor, id_categoria, precio, stock_inicial, costo)
        messagebox.showinfo("Listo", f"'{titulo}' se agregó correctamente.")
        al_guardar()
        ventana.destroy()

    ctk.CTkButton(ventana, text="Guardar", width=160, height=36, command=guardar).pack(pady=5)