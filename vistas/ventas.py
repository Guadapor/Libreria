import customtkinter as ctk
from tkinter import ttk, messagebox

from vistas.estilos import aplicar_estilo_tabla
from modelos.libros import obtener_libros
from modelos.ventas import registrar_venta, obtener_ventas, obtener_detalle_venta, StockInsuficiente


def abrir_ventas(usuario):
    aplicar_estilo_tabla()
    ventana = ctk.CTkToplevel()
    ventana.title("Librería - Ventas")
    ventana.geometry("620x480")
    ventana.after(100, ventana.lift)

    ctk.CTkLabel(ventana, text="Ventas registradas", font=("Arial", 18, "bold")).pack(pady=10)

    # Elementos de abajo primero, así la tabla no los empuja fuera de la ventana
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(side="bottom", pady=(0, 12))
    ctk.CTkLabel(ventana, text="Doble clic en una venta para ver el detalle",
                 text_color="gray", font=("Arial", 11)).pack(side="bottom")

    columnas = ("id", "fecha", "total", "vendedor")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=14)
    tabla.heading("id", text="N°")
    tabla.heading("fecha", text="Fecha")
    tabla.heading("total", text="Total")
    tabla.heading("vendedor", text="Vendedor")
    tabla.column("id", width=50, anchor="center")
    tabla.column("fecha", width=170)
    tabla.column("total", width=100, anchor="e")
    tabla.column("vendedor", width=170)
    tabla.pack(padx=10, pady=10, fill="both", expand=True)

    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)
        for venta in obtener_ventas():
            tabla.insert("", "end", values=(
                venta["id_venta"],
                venta["fecha"],
                f"{venta['total']:.2f}",
                venta["vendedor"],
            ))

    def ver_detalle(evento=None):
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_venta = tabla.item(seleccion[0])["values"][0]
        detalle = obtener_detalle_venta(id_venta)
        texto = "\n".join(
            f"{d['cantidad']} x {d['titulo']}  ->  ${d['cantidad'] * d['precio_unitario']:.2f}"
            for d in detalle
        )
        messagebox.showinfo(f"Detalle de la venta #{id_venta}", texto or "Sin ítems.")

    tabla.bind("<Double-1>", ver_detalle)

    def abrir_formulario_nueva_venta():
        _abrir_formulario_nueva_venta(ventana, usuario, al_guardar=cargar_tabla)

    ctk.CTkButton(marco_botones, text="Nueva venta", width=130, command=abrir_formulario_nueva_venta).pack(side="left", padx=5)
    ctk.CTkButton(marco_botones, text="Actualizar", width=130, command=cargar_tabla).pack(side="left", padx=5)

    cargar_tabla()


def _abrir_formulario_nueva_venta(padre, usuario, al_guardar):
    ventana = ctk.CTkToplevel(padre)
    ventana.title("Nueva venta")
    ventana.geometry("620x560")
    ventana.after(100, ventana.lift)
    ventana.after(150, ventana.grab_set)

    libros = obtener_libros()
    libros_por_titulo = {f"{l['titulo']} (stock: {l['stock_actual']})": l for l in libros}

    ctk.CTkLabel(ventana, text="Nueva venta", font=("Arial", 18, "bold")).pack(pady=10)

    marco_agregar = ctk.CTkFrame(ventana)
    marco_agregar.pack(pady=5, padx=10)

    ctk.CTkLabel(marco_agregar, text="Libro").grid(row=0, column=0, padx=8, pady=8)
    combo_libro = ctk.CTkComboBox(marco_agregar, width=280, state="readonly",
                                  values=list(libros_por_titulo.keys()))
    combo_libro.set("")
    combo_libro.grid(row=0, column=1, padx=8, pady=8)

    ctk.CTkLabel(marco_agregar, text="Cantidad").grid(row=1, column=0, padx=8, pady=8)
    entrada_cantidad = ctk.CTkEntry(marco_agregar, width=80)
    entrada_cantidad.insert(0, "1")
    entrada_cantidad.grid(row=1, column=1, sticky="w", padx=8, pady=8)

    # Abajo: total y botón de confirmar (se empaquetan antes que la tabla)
    boton_confirmar_marco = ctk.CTkFrame(ventana, fg_color="transparent")
    boton_confirmar_marco.pack(side="bottom", pady=10)
    etiqueta_total = ctk.CTkLabel(ventana, text="Total: $0.00", font=("Arial", 14, "bold"))
    etiqueta_total.pack(side="bottom")

    columnas = ("titulo", "cantidad", "precio_unitario", "subtotal")
    tabla_items = ttk.Treeview(ventana, columns=columnas, show="headings", height=8)
    tabla_items.heading("titulo", text="Libro")
    tabla_items.heading("cantidad", text="Cant.")
    tabla_items.heading("precio_unitario", text="Precio u.")
    tabla_items.heading("subtotal", text="Subtotal")
    tabla_items.column("titulo", width=240)
    tabla_items.column("cantidad", width=60, anchor="center")
    tabla_items.column("precio_unitario", width=90, anchor="e")
    tabla_items.column("subtotal", width=100, anchor="e")
    tabla_items.pack(padx=10, pady=10, fill="both", expand=True)

    items_venta = []  # lista de dicts {id_libro, titulo, cantidad, precio_unitario}

    def recalcular_total():
        total = sum(i["cantidad"] * i["precio_unitario"] for i in items_venta)
        etiqueta_total.configure(text=f"Total: ${total:.2f}")

    def agregar_item():
        clave = combo_libro.get()
        if not clave:
            messagebox.showwarning("Datos incompletos", "Elegí un libro.")
            return
        try:
            cantidad = int(entrada_cantidad.get().strip())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "La cantidad debe ser un entero mayor a 0.")
            return

        libro = libros_por_titulo[clave]
        ya_agregado = sum(i["cantidad"] for i in items_venta if i["id_libro"] == libro["id_libro"])
        if cantidad + ya_agregado > libro["stock_actual"]:
            messagebox.showwarning("Stock insuficiente",
                                   f"Solo hay {libro['stock_actual']} unidades de '{libro['titulo']}' "
                                   f"(ya agregaste {ya_agregado}).")
            return

        items_venta.append({
            "id_libro": libro["id_libro"],
            "titulo": libro["titulo"],
            "cantidad": cantidad,
            "precio_unitario": libro["precio"],
        })
        tabla_items.insert("", "end", values=(
            libro["titulo"], cantidad, f"{libro['precio']:.2f}", f"{cantidad * libro['precio']:.2f}"
        ))
        recalcular_total()

    ctk.CTkButton(marco_agregar, text="Agregar a la venta", command=agregar_item).grid(
        row=0, column=2, rowspan=2, padx=10)

    def confirmar_venta():
        if not items_venta:
            messagebox.showwarning("Venta vacía", "Agregá al menos un libro a la venta.")
            return
        try:
            id_venta = registrar_venta(usuario["id_usuario"], items_venta)
        except StockInsuficiente as error:
            messagebox.showerror("Stock insuficiente", str(error))
            return
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        messagebox.showinfo("Venta registrada", f"Venta #{id_venta} guardada correctamente.")
        al_guardar()
        ventana.destroy()

    ctk.CTkButton(boton_confirmar_marco, text="Confirmar venta", width=180, height=36,
                  command=confirmar_venta).pack()