import customtkinter as ctk
from tkinter import messagebox

COLOR_FONDO = "#1B2A4A"
COLOR_TARJETA = "#24365C"
COLOR_ACENTO = "#E8833A"
COLOR_TEXTO = "#F2F2F2"

opciones = [(" Libros", "Libros", ["administrador", "vendedor"]),
            (" Ventas", "Ventas", ["administrador", "vendedor"]),
            (" Stock", "Stock", ["administrador", "vendedor"]),
            (" Movimientos", "Movimientos", ["administrador"]),
            (" Ganancias", "Ganancias", ["administrador"]),
            (" Usuarios", "Usuarios", ["administrador"]),
            ]


def abrir_menu(usuario):
    ventana = ctk.CTk()
    ventana.title("Librería - Menú principal")
    ventana.geometry("460x480")
    ventana.configure(fg_color=COLOR_FONDO)

    ctk.CTkLabel(
        ventana, text="Menú Principal",
        font=("Arial", 22, "bold"), text_color=COLOR_ACENTO,
    ).pack(pady=(25, 5))

    ctk.CTkLabel(
        ventana, text=f"{usuario['nombre']} ({usuario['rol']})",
        font=("Arial", 13), text_color=COLOR_TEXTO,
    ).pack(pady=(0, 20))

    marco = ctk.CTkFrame(ventana, fg_color="transparent")
    marco.pack()

    def abrir_pantalla(nombre):
        messagebox.showinfo(nombre, f"La pantalla de {nombre} todavía no esta hecha.")

    visible = [(texto, nombre) for texto, nombre, roles in opciones if usuario["rol"] in roles]

    for i, (texto, nombre) in enumerate(visible):
        ctk.CTkButton(
            marco, text=texto, width=180, height=70, corner_radius=12,
            fg_color=COLOR_TARJETA, hover_color=COLOR_ACENTO,
            font=("Arial", 14, "bold"),
            command=lambda n=nombre: abrir_pantalla(n),
        ).grid(row=i // 2, column=i % 2, padx=10, pady=10)

    ctk.CTkButton(
        ventana, text="Salir", width=180, height=36, corner_radius=8,
        fg_color="#8C3B3B", hover_color="#B04C4C",
        command=ventana.destroy,
    ).pack(pady=25)

    ventana.mainloop()