import tkinter as tk
from tkinter import messagebox
from modelos.usuarios import validar_login, crear_admin_inicial

def abrir_login():
    
    resultado = {"usuario": None}

    ventana = tk.Tk()
    ventana.title ("Librería - Inicio de sesión")
    ventana.geometry("340x300")
    ventana.resizable(False, False)

    tk.Label(ventana, text= "Inicio de Sesión", font= ("Arial", 18, "bold")).pack(pady=20)

    tk.Label(ventana, text="Usuario").pack(anchor="w", padx=40)

    entrada_usuario = tk.Entry(ventana, width=30)
    entrada_usuario.pack(pady=(0, 10))

    tk.Label(ventana, text="Contraseña").pack(anchor="w", padx=40)
    entrada_contrasena = tk.Entry(ventana, width=30, show="*")
    entrada_contrasena.pack(pady=(0, 20))

    def ingresar(evento=None):
        usuario = entrada_usuario.get().strip()
        contrasena = entrada_contrasena.get()

        if usuario == "" or contrasena == "":
            messagebox.showwarning("Datos incompletos", "Completá usuario y contraseña.")
            return

        datos = validar_login(usuario, contrasena)
        if datos is None:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            entrada_contrasena.delete(0, tk.END)
            return

        resultado["usuario"] = datos
        ventana.destroy()

    tk.Button(ventana, text="Iniciar sesión", width=20, command=ingresar).pack()
    ventana.bind("<Return>", ingresar)
    entrada_usuario.focus() 

    ventana.mainloop()
    return resultado["usuario"] 

    


