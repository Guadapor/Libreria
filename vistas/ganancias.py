import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta

from vistas.estilos import aplicar_estilo_tabla
from modelos.ganancias import (
    obtener_resumen,
    obtener_libros_mas_vendidos,
    obtener_ventas_por_vendedor,
)

PERIODOS = ["Hoy", "Últimos 7 días", "Este mes", "Todo"]
COLOR_POSITIVO = "#6bd68a"
COLOR_NEGATIVO = "#ff8a80"
COLOR_AVISO = "#ffc857"


def _fecha_desde(periodo):
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if periodo == "Hoy":
        desde = hoy
    elif periodo == "Últimos 7 días":
        desde = hoy - timedelta(days=6)
    elif periodo == "Este mes":
        desde = hoy.replace(day=1)
    else:
        return None
    return desde.strftime("%Y-%m-%d %H:%M:%S")


def _dinero(valor):
    return "—" if valor is None else f"${valor:.2f}"


def _tarjeta(padre, titulo):
    marco = ctk.CTkFrame(padre, corner_radius=10)
    ctk.CTkLabel(marco, text=titulo, text_color="gray", font=("Arial", 12)).pack(padx=22, pady=(10, 0))
    valor = ctk.CTkLabel(marco, text="-", font=("Arial", 20, "bold"))
    valor.pack(padx=22, pady=(0, 10))
    return marco, valor


def abrir_ganancias(usuario):
    aplicar_estilo_tabla()
    ventana = ctk.CTkToplevel()
    ventana.title("Librería - Ganancias")
    ventana.geometry("780x680")
    ventana.after(100, ventana.lift)

    ctk.CTkLabel(ventana, text="Ganancias", font=("Arial", 18, "bold")).pack(pady=(10, 5))

    # Botones abajo (se empaquetan primero para que lo demás no los empuje)
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(side="bottom", pady=(0, 12))

    # Selector de período
    marco_periodo = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_periodo.pack(pady=5)
    ctk.CTkLabel(marco_periodo, text="Período").pack(side="left", padx=(0, 8))
    combo_periodo = ctk.CTkComboBox(marco_periodo, width=170, state="readonly",
                                    values=PERIODOS, command=lambda _v: cargar())
    combo_periodo.set("Este mes")
    combo_periodo.pack(side="left")

    # Tarjetas de resumen
    marco_tarjetas = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_tarjetas.pack(pady=10)
    tarjetas = {}
    for i, (clave, titulo) in enumerate([
        ("ingresos", "Ingresos"),
        ("costo", "Costos"),
        ("ganancia", "Ganancia"),
        ("margen", "Margen"),
    ]):
        marco, valor = _tarjeta(marco_tarjetas, titulo)
        marco.grid(row=0, column=i, padx=6)
        tarjetas[clave] = valor

    etiqueta_resumen = ctk.CTkLabel(ventana, text="", text_color="gray", font=("Arial", 12))
    etiqueta_resumen.pack()
    etiqueta_aviso = ctk.CTkLabel(ventana, text="", text_color=COLOR_AVISO,
                                  font=("Arial", 12), wraplength=700)
    etiqueta_aviso.pack(pady=(2, 0))

    # Pestañas con detalle
    pestanas = ctk.CTkTabview(ventana)
    pestanas.pack(padx=10, pady=8, fill="both", expand=True)
    tab_libros = pestanas.add("Libros más vendidos")
    tab_vendedores = pestanas.add("Por vendedor")

    tabla_libros = ttk.Treeview(tab_libros, columns=("titulo", "unidades", "ingresos", "ganancia"),
                                show="headings", height=10)
    tabla_libros.heading("titulo", text="Libro")
    tabla_libros.heading("unidades", text="Unidades")
    tabla_libros.heading("ingresos", text="Ingresos")
    tabla_libros.heading("ganancia", text="Ganancia")
    tabla_libros.column("titulo", width=300)
    tabla_libros.column("unidades", width=80, anchor="center")
    tabla_libros.column("ingresos", width=110, anchor="e")
    tabla_libros.column("ganancia", width=110, anchor="e")
    tabla_libros.pack(fill="both", expand=True, padx=5, pady=5)

    tabla_vendedores = ttk.Treeview(tab_vendedores, columns=("vendedor", "cantidad", "ingresos", "ganancia"),
                                    show="headings", height=10)
    tabla_vendedores.heading("vendedor", text="Vendedor")
    tabla_vendedores.heading("cantidad", text="Ventas")
    tabla_vendedores.heading("ingresos", text="Ingresos")
    tabla_vendedores.heading("ganancia", text="Ganancia")
    tabla_vendedores.column("vendedor", width=300)
    tabla_vendedores.column("cantidad", width=80, anchor="center")
    tabla_vendedores.column("ingresos", width=110, anchor="e")
    tabla_vendedores.column("ganancia", width=110, anchor="e")
    tabla_vendedores.pack(fill="both", expand=True, padx=5, pady=5)

    def cargar():
        desde = _fecha_desde(combo_periodo.get())

        r = obtener_resumen(desde)
        tarjetas["ingresos"].configure(text=_dinero(r["ingresos"]))
        tarjetas["costo"].configure(text=_dinero(r["costo"]))

        if r["ganancia"] is None:
            tarjetas["ganancia"].configure(text="—", text_color=("gray10", "gray90"))
            tarjetas["margen"].configure(text="—")
        else:
            color = COLOR_POSITIVO if r["ganancia"] >= 0 else COLOR_NEGATIVO
            tarjetas["ganancia"].configure(text=_dinero(r["ganancia"]), text_color=color)
            tarjetas["margen"].configure(text=f"{r['margen']:.1f}%")

        etiqueta_resumen.configure(
            text=f"{r['cantidad_ventas']} ventas · {r['unidades']} libros vendidos · "
                 f"ticket promedio ${r['ticket_promedio']:.2f}"
        )
        if r["unidades_sin_costo"]:
            etiqueta_aviso.configure(
                text=f"⚠ {r['unidades_sin_costo']} unidad(es) vendidas sin costo cargado: "
                     f"cuentan como ingreso pero no entran en costos ni ganancia. "
                     f"Cargá el costo en Libros → Editar costo."
            )
        else:
            etiqueta_aviso.configure(text="")

        for fila in tabla_libros.get_children():
            tabla_libros.delete(fila)
        for libro in obtener_libros_mas_vendidos(desde):
            tabla_libros.insert("", "end", values=(
                libro["titulo"], libro["unidades"],
                _dinero(libro["ingresos"]), _dinero(libro["ganancia"])))

        for fila in tabla_vendedores.get_children():
            tabla_vendedores.delete(fila)
        for v in obtener_ventas_por_vendedor(desde):
            tabla_vendedores.insert("", "end", values=(
                v["vendedor"], v["cantidad"],
                _dinero(v["ingresos"]), _dinero(v["ganancia"])))

    ctk.CTkButton(marco_botones, text="Actualizar", width=130, command=cargar).pack(side="left", padx=5)
    ctk.CTkButton(marco_botones, text="Volver al menú", width=130, command=ventana.destroy).pack(side="left", padx=5)

    cargar()