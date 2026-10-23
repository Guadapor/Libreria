import customtkinter as ctk
from tkinter import messagebox

from vistas.libros import abrir_libros
from vistas.ventas import abrir_ventas
from vistas.stock import abrir_stock
from vistas.movimientos import abrir_movimientos
from vistas.ganancias import abrir_ganancias
from vistas.usuarios import abrir_usuarios

opciones = [
    ("Libros", ["administrador", "vendedor"]),
    ("Ventas", ["administrador", "vendedor"]),
    ("Stock", ["administrador", "vendedor"]),
    ("Movimientos", ["administrador"]),
    ("Ganancias", ["administrador"]),
    ("Usuarios", ["administrador"]),
]

pantallas = {
    "Libros": abrir_libros,
    "Ventas": abrir_ventas,
    "Stock": abrir_stock,
    "Movimientos": abrir_movimientos,
    "Ganancias": abrir_ganancias,
    "Usuarios": abrir_usuarios,
}


def abrir_menu(usuario):
    resultado = {"cerrar_sesion": False}

    ventana = ctk.CTk()
    ventana.title("Librería - Menú principal")
    ventana.geometry("420x460")
    ventana.resizable(False, False)

    ctk.CTkLabel(ventana, text="Menú Principal", font=("Arial", 22, "bold")).pack(pady=(25, 5))
    ctk.CTkLabel(ventana, text=f"{usuario['nombre']} ({usuario['rol']})",
                 text_color="gray").pack(pady=(0, 15))

    marco = ctk.CTkFrame(ventana, fg_color="transparent")
    marco.pack()

    def abrir_pantalla(nombre):
        funcion = pantallas.get(nombre)
        if funcion is None:
            messagebox.showinfo(nombre, f"La pantalla de {nombre} todavía no está hecha.")
            return
        funcion(usuario)

    visible = [nombre for nombre, roles in opciones if usuario["rol"] in roles]

    for i, nombre in enumerate(visible):
        ctk.CTkButton(
            marco, text=nombre, width=160, height=50,
            font=("Arial", 14),
            command=lambda n=nombre: abrir_pantalla(n),
        ).grid(row=i // 2, column=i % 2, padx=8, pady=8)

    def cerrar_sesion():
        if messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que querés cerrar sesión?"):
            resultado["cerrar_sesion"] = True
            ventana.destroy()

    # Botones inferiores: Cerrar sesión y Salir del sistema
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(pady=20)

    ctk.CTkButton(
        marco_botones, text="Cerrar sesión", width=130, height=36,
        fg_color="#3A608F", hover_color="#2A4870",
        command=cerrar_sesion,
    ).pack(side="left", padx=5) # type: ignore

    ctk.CTkButton(
        marco_botones, text="Salir", width=120, height=36,
        fg_color="#8B2E2E", hover_color="#6E2323",
        command=ventana.destroy,
    ).pack(side="left", padx=5)

    ventana.mainloop()
    return resultado["cerrar_sesion"]
    


   