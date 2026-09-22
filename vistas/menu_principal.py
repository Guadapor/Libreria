import tkinter as tk
from tkinter import messagebox

from vistas.libros import abrir_libros  
from vistas.ventas import abrir_ventas

opciones = [("Libros", ["administrador", "vendedor"]), 
            ("Ventas", ["administrador", "vendedor"]), 
            ("Stock", ["administrador", "vendedor"]),
            ("Movimientos", ["administrador"]),
            ("Ganancias", ["administrador"]),
            ("Usuarios", ["administrador"]),
            ]
# Pantallas ya implementadas. Las que todavia no estás hechas siguen mostrando el mensaje de aviso, como antes.
pantallas = {
    "Libros": abrir_libros,
    "Ventas": abrir_ventas,
}


def abrir_menu(usuario):
    ventana = tk.Tk()
    ventana.title("Librería - Menú principal")
    ventana.geometry("420x420")

    tk.Label(ventana, text= "Menú Principal", font=("Arial", 18, "bold")).pack(pady=20, padx=5)
    tk.Label(ventana, text = f"{usuario['nombre']} ({usuario['rol']})").pack(pady=0, padx=15)

    marco = tk.Frame(ventana)
    marco.pack()

    def abrir_pantalla(nombre):
        funcion = pantallas.get(nombre)
        if funcion is None:
            messagebox.showinfo(nombre, f"La pantalla de {nombre} todavía no esta hecha.")
            return
        funcion(usuario)

    visible = [nombre for nombre, roles in opciones if usuario["rol"] in roles]

    for i, nombre in enumerate(visible):
        tk.Button(
            marco, text= nombre, width= 16, height = 3, 
            command = lambda n= nombre: abrir_pantalla(n),
        ).grid(row=i // 2, column= i % 2, padx= 8, pady = 8)

    tk.Button(ventana, text="Salir", width= 16, command= ventana.destroy).pack(pady= 20)

    ventana.mainloop()