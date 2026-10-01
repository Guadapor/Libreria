import customtkinter as ctk
from tkinter import ttk, messagebox

from vistas.estilos import aplicar_estilo_tabla
from modelos.libros import obtener_libros
from modelos.stock import agregar_stock

STOCK_BAJO = 5  # a partir de esta cantidad (inclusive hacia abajo) se avisa "Stock bajo"


def _estado(stock):
    if stock == 0:
        return "Sin stock"
    if stock <= STOCK_BAJO:
        return "Stock bajo"
    return "OK"


def abrir_stock(usuario):
    aplicar_estilo_tabla()
    ventana = ctk.CTkToplevel()
    ventana.title("Librería - Stock")
    ventana.geometry("760x520")
    ventana.after(100, ventana.lift)

    ctk.CTkLabel(ventana, text="Control de stock", font=("Arial", 18, "bold")).pack(pady=(10, 5))

    # Botones abajo (se empaquetan primero para que la tabla no los empuje)
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(side="bottom", pady=(0, 12))

    etiqueta_resumen = ctk.CTkLabel(ventana, text="", text_color="gray", font=("Arial", 12))
    etiqueta_resumen.pack(side="bottom", pady=(0, 5))

    # Buscador
    marco_busqueda = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_busqueda.pack(fill="x", padx=10)
    ctk.CTkLabel(marco_busqueda, text="Buscar").pack(side="left", padx=(0, 8))
    entrada_busqueda = ctk.CTkEntry(marco_busqueda, width=300, placeholder_text="Título, autor o categoría")
    entrada_busqueda.pack(side="left")

    columnas = ("titulo", "autor", "categoria", "stock", "estado")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=14)
    tabla.heading("titulo", text="Título")
    tabla.heading("autor", text="Autor")
    tabla.heading("categoria", text="Categoría")
    tabla.heading("stock", text="Stock")
    tabla.heading("estado", text="Estado")
    tabla.column("titulo", width=250)
    tabla.column("autor", width=150)
    tabla.column("categoria", width=120)
    tabla.column("stock", width=60, anchor="center")
    tabla.column("estado", width=100, anchor="center")
    tabla.pack(padx=10, pady=10, fill="both", expand=True)

    tabla.tag_configure("agotado", foreground="#ff6b6b")
    tabla.tag_configure("bajo", foreground="#ffc857")

    def cargar_tabla(evento=None):
        texto = entrada_busqueda.get().strip().lower()
        for fila in tabla.get_children():
            tabla.delete(fila)

        libros = obtener_libros()
        agotados = bajos = 0
        for libro in libros:
            if texto and texto not in f"{libro['titulo']} {libro['autor']} {libro['categoria']}".lower():
                continue
            estado = _estado(libro["stock_actual"])
            etiqueta = ()
            if estado == "Sin stock":
                etiqueta = ("agotado",)
            elif estado == "Stock bajo":
                etiqueta = ("bajo",)
            tabla.insert(
                "", "end", iid=str(libro["id_libro"]),
                values=(libro["titulo"], libro["autor"], libro["categoria"],
                        libro["stock_actual"], estado),
                tags=etiqueta,
            )

        for libro in libros:
            if libro["stock_actual"] == 0:
                agotados += 1
            elif libro["stock_actual"] <= STOCK_BAJO:
                bajos += 1
        etiqueta_resumen.configure(
            text=f"{len(libros)} libros en total · {bajos} con stock bajo (≤ {STOCK_BAJO}) · {agotados} sin stock"
        )

    entrada_busqueda.bind("<KeyRelease>", cargar_tabla)

    def abrir_formulario_ingreso():
        seleccion = tabla.selection()
        id_preseleccionado = int(seleccion[0]) if seleccion else None
        _abrir_formulario_ingreso(ventana, id_preseleccionado, al_guardar=cargar_tabla)

    ctk.CTkButton(marco_botones, text="Registrar ingreso", width=150,
                  command=abrir_formulario_ingreso).pack(side="left", padx=5)
    ctk.CTkButton(marco_botones, text="Actualizar", width=130, command=cargar_tabla).pack(side="left", padx=5)
    ctk.CTkButton(marco_botones, text="Volver al menú", width=130, command=ventana.destroy).pack(side="left", padx=5)

    cargar_tabla()


def _abrir_formulario_ingreso(padre, id_preseleccionado, al_guardar):
    ventana = ctk.CTkToplevel(padre)
    ventana.title("Registrar ingreso de stock")
    ventana.geometry("440x380")
    ventana.resizable(False, False)
    ventana.after(100, ventana.lift)
    ventana.after(150, ventana.grab_set)

    libros = obtener_libros()
    libros_por_clave = {f"{l['titulo']} - {l['autor']} (stock: {l['stock_actual']})": l for l in libros}

    ctk.CTkLabel(ventana, text="Ingreso de stock", font=("Arial", 18, "bold")).pack(pady=15)

    ctk.CTkLabel(ventana, text="Libro").pack(anchor="w", padx=30)
    combo_libro = ctk.CTkComboBox(ventana, width=380, state="readonly",
                                  values=list(libros_por_clave.keys()))
    combo_libro.set("")
    if id_preseleccionado is not None:
        for clave, libro in libros_por_clave.items():
            if libro["id_libro"] == id_preseleccionado:
                combo_libro.set(clave)
                break
    combo_libro.pack(padx=30, pady=(0, 10))

    ctk.CTkLabel(ventana, text="Cantidad que ingresa").pack(anchor="w", padx=30)
    entrada_cantidad = ctk.CTkEntry(ventana, width=380)
    entrada_cantidad.pack(padx=30, pady=(0, 10))

    ctk.CTkLabel(ventana, text="Detalle (opcional)").pack(anchor="w", padx=30)
    entrada_detalle = ctk.CTkEntry(ventana, width=380, placeholder_text="Ej: Pedido a distribuidora")
    entrada_detalle.pack(padx=30, pady=(0, 15))

    def guardar():
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

        libro = libros_por_clave[clave]
        try:
            agregar_stock(libro["id_libro"], cantidad, entrada_detalle.get().strip() or "Reposición")
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        messagebox.showinfo("Listo", f"Se sumaron {cantidad} unidades a '{libro['titulo']}'.")
        al_guardar()
        ventana.destroy()

    ctk.CTkButton(ventana, text="Guardar", width=160, height=36, command=guardar).pack(pady=5)