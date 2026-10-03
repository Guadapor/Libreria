import customtkinter as ctk
from tkinter import ttk

from vistas.estilos import aplicar_estilo_tabla
from modelos.movimientos import obtener_movimientos

FILTROS_TIPO = {"Todos": None, "Entradas": "entrada", "Salidas": "salida"}


def abrir_movimientos(usuario):
    aplicar_estilo_tabla()
    ventana = ctk.CTkToplevel()
    ventana.title("Librería - Movimientos de stock")
    ventana.geometry("820x520")
    ventana.after(100, ventana.lift)

    ctk.CTkLabel(ventana, text="Movimientos de stock", font=("Arial", 18, "bold")).pack(pady=(10, 5))

    # Elementos de abajo primero, así la tabla no los empuja fuera de la ventana
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(side="bottom", pady=(0, 12))

    etiqueta_resumen = ctk.CTkLabel(ventana, text="", text_color="gray", font=("Arial", 12))
    etiqueta_resumen.pack(side="bottom", pady=(0, 5))

    # Filtros
    marco_filtros = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_filtros.pack(fill="x", padx=10)

    ctk.CTkLabel(marco_filtros, text="Tipo").pack(side="left", padx=(0, 8))
    combo_tipo = ctk.CTkComboBox(marco_filtros, width=120, state="readonly",
                                 values=list(FILTROS_TIPO.keys()),
                                 command=lambda _valor: cargar_tabla())
    combo_tipo.set("Todos")
    combo_tipo.pack(side="left", padx=(0, 20))

    ctk.CTkLabel(marco_filtros, text="Buscar").pack(side="left", padx=(0, 8))
    entrada_busqueda = ctk.CTkEntry(marco_filtros, width=280, placeholder_text="Libro o detalle")
    entrada_busqueda.pack(side="left")

    columnas = ("fecha", "titulo", "tipo", "cantidad", "detalle")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=14)
    tabla.heading("fecha", text="Fecha")
    tabla.heading("titulo", text="Libro")
    tabla.heading("tipo", text="Tipo")
    tabla.heading("cantidad", text="Cant.")
    tabla.heading("detalle", text="Detalle")
    tabla.column("fecha", width=140)
    tabla.column("titulo", width=230)
    tabla.column("tipo", width=80, anchor="center")
    tabla.column("cantidad", width=60, anchor="center")
    tabla.column("detalle", width=230)
    tabla.pack(padx=10, pady=10, fill="both", expand=True)

    tabla.tag_configure("entrada", foreground="#6bd68a")
    tabla.tag_configure("salida", foreground="#ff8a80")

    def cargar_tabla(evento=None):
        tipo = FILTROS_TIPO[combo_tipo.get()]
        texto = entrada_busqueda.get().strip().lower()

        for fila in tabla.get_children():
            tabla.delete(fila)

        total_entradas = total_salidas = mostrados = 0
        for mov in obtener_movimientos():
            if tipo and mov["tipo"] != tipo:
                continue
            if texto and texto not in f"{mov['titulo']} {mov['detalle']}".lower():
                continue

            tabla.insert(
                "", "end",
                values=(mov["fecha"], mov["titulo"], mov["tipo"].capitalize(),
                        mov["cantidad"], mov["detalle"]),
                tags=(mov["tipo"],),
            )
            mostrados += 1
            if mov["tipo"] == "entrada":
                total_entradas += mov["cantidad"]
            else:
                total_salidas += mov["cantidad"]

        etiqueta_resumen.configure(
            text=f"{mostrados} movimientos · {total_entradas} unidades ingresadas · {total_salidas} unidades vendidas/salidas"
        )

    entrada_busqueda.bind("<KeyRelease>", cargar_tabla)

    ctk.CTkButton(marco_botones, text="Actualizar", width=130, command=cargar_tabla).pack(side="left", padx=5)
    ctk.CTkButton(marco_botones, text="Volver al menú", width=130, command=ventana.destroy).pack(side="left", padx=5)

    cargar_tabla()