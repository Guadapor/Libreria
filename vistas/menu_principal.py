import tkinter as tk
from tkinter import messagebox

opciones = [("Libros", ["administrador", "vendedor"]), 
            ("Ventas", ["administrador", "vendedor"]), 
            ("Stock", ["administrador", "vendedor"]),
            ("Movimientos", ["administrador"]),
            ("Ganancias", ["administrador"]),
            ("Usuarios", ["administrador"]),
            ]

def abrir_menu(usuario):
    ventana = tk.Tk()
    ventana.title("Librería - Menú principal")
    ventana.geometry("420x420")

    tk.Label(ventana, text= "Menú Principal", font=("Arial", 18, "bold")).pack(pady=20, padx=5)
    tk.Label(ventana, text = f"{usuario['nombre']} ({usuario['rol']})").pack(pady=0, padx=15)

    marco = tk.Frame(ventana)
    marco.pack()

    def abrir_pantalla(nombre):
        messagebox.showinfo(nombre, f"La pantalla de {nombre} todavía no esta hecha.")

    visible = [nombre for nombre, roles in opciones if usuario["rol"] in roles]

    for i, nombre in enumerate(visible):
        tk.Button(
            marco, text= nombre, width= 16, height = 3, 
            command = lambda n= nombre: abrir_pantalla(n),
        ).grid(row=i // 2, column= i % 2, padx= 8, pady = 8)

    tk.Button(ventana, text="Salir", width= 16, command= ventana.destroy).pack(pady= 20)

    ventana.mainloop()