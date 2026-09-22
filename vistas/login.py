import customtkinter as ctk
from tkinter import messagebox
from modelos.usuarios import validar_login


COLOR_FONDO = "#1B2A4A"      # azul oscuro, como la tapa de un libro
COLOR_TARJETA = "#24365C"    # un poco más claro, para las tarjetas
COLOR_ACENTO = "#E8833A"     # naranja cálido
COLOR_TEXTO = "#F2F2F2"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def abrir_login():
    resultado = {"usuario": None}

    ventana = ctk.CTk()
    ventana.title("Librería - Inicio de sesión")
    ventana.geometry("380x420")
    ventana.resizable(False, False)
    ventana.configure(fg_color=COLOR_FONDO)

    tarjeta = ctk.CTkFrame(ventana, fg_color=COLOR_TARJETA, corner_radius=16)
    tarjeta.pack(padx=30, pady=30, fill="both", expand=True)

    ctk.CTkLabel(
        tarjeta, text="Inicio de Sesión",
        font=("Arial", 18, "bold"), text_color=COLOR_TEXTO,
    ).pack(pady=(40, 25))

    entrada_usuario = ctk.CTkEntry(tarjeta, width=240, height=38, placeholder_text="Usuario")
    entrada_usuario.pack(pady=8)

    entrada_contrasena = ctk.CTkEntry(
        tarjeta, width=240, height=38, placeholder_text="Contraseña", show="*"
    )
    entrada_contrasena.pack(pady=8)

    def ingresar(evento=None):
        usuario = entrada_usuario.get().strip()
        contrasena = entrada_contrasena.get()

        if usuario == "" or contrasena == "":
            messagebox.showwarning("Datos incompletos", "Completá usuario y contraseña.")
            return

        datos = validar_login(usuario, contrasena)
        if datos is None:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            entrada_contrasena.delete(0, "end")
            return

        resultado["usuario"] = datos
        ventana.destroy()

    ctk.CTkButton(
        tarjeta, text="Iniciar sesión", command=ingresar,
        width=240, height=40, fg_color=COLOR_ACENTO, hover_color="#C96A28",
        font=("Arial", 14, "bold"),
    ).pack(pady=(20, 10))

    ventana.bind("<Return>", ingresar)
    entrada_usuario.focus()

    ventana.mainloop()
    return resultado["usuario"]
    


