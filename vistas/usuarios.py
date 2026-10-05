import customtkinter as ctk
from tkinter import ttk, messagebox

from vistas.estilos import aplicar_estilo_tabla
from modelos.usuarios import (
    ROLES,
    obtener_usuarios,
    agregar_usuario,
    actualizar_usuario,
    cambiar_contrasena,
    eliminar_usuario,
    UsuarioDuplicado,
    UsuarioConVentas,
    UltimoAdministrador,
)

LARGO_MINIMO_CONTRASENA = 6


def abrir_usuarios(usuario):
    aplicar_estilo_tabla()
    ventana = ctk.CTkToplevel()
    ventana.title("Librería - Usuarios")
    ventana.geometry("820x500")
    ventana.after(100, ventana.lift)

    ctk.CTkLabel(ventana, text="Usuarios", font=("Arial", 18, "bold")).pack(pady=10)

    # Botones abajo (se empaquetan primero para que la tabla no los empuje)
    marco_botones = ctk.CTkFrame(ventana, fg_color="transparent")
    marco_botones.pack(side="bottom", pady=(0, 12))

    columnas = ("nombre", "usuario", "rol", "telefono", "domicilio")
    tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=14)
    tabla.heading("nombre", text="Nombre")
    tabla.heading("usuario", text="Usuario")
    tabla.heading("rol", text="Rol")
    tabla.heading("telefono", text="Teléfono")
    tabla.heading("domicilio", text="Domicilio")
    tabla.column("nombre", width=190)
    tabla.column("usuario", width=130)
    tabla.column("rol", width=110, anchor="center")
    tabla.column("telefono", width=120)
    tabla.column("domicilio", width=210)
    tabla.pack(padx=10, pady=10, fill="both", expand=True)

    datos = {}

    def cargar_tabla():
        for fila in tabla.get_children():
            tabla.delete(fila)
        datos.clear()
        for u in obtener_usuarios():
            datos[u["id_usuario"]] = u
            nombre = u["nombre"] + (" (vos)" if u["id_usuario"] == usuario["id_usuario"] else "")
            tabla.insert("", "end", iid=str(u["id_usuario"]),
                         values=(nombre, u["nombre_usuario"], u["rol"], u["telefono"], u["domicilio"]))

    def seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccioná un usuario de la tabla.")
            return None
        return datos[int(seleccion[0])]

    def nuevo():
        _abrir_formulario_usuario(ventana, al_guardar=cargar_tabla)

    def editar():
        elegido = seleccionado()
        if elegido:
            _abrir_formulario_usuario(
                ventana, al_guardar=cargar_tabla, editar=elegido,
                es_propio=elegido["id_usuario"] == usuario["id_usuario"],
            )

    def contrasena():
        elegido = seleccionado()
        if elegido:
            _abrir_formulario_contrasena(ventana, elegido)

    def eliminar():
        elegido = seleccionado()
        if not elegido:
            return
        if elegido["id_usuario"] == usuario["id_usuario"]:
            messagebox.showwarning("No permitido", "No podés eliminar tu propio usuario.")
            return
        if not messagebox.askyesno(
                "Confirmar",
                f"¿Eliminar a '{elegido['nombre']}' ({elegido['nombre_usuario']})?\n"
                "Esta acción no se puede deshacer."):
            return
        try:
            eliminar_usuario(elegido["id_usuario"])
        except (UsuarioConVentas, UltimoAdministrador) as error:
            messagebox.showwarning("No se puede eliminar", str(error))
            return
        cargar_tabla()

    ctk.CTkButton(marco_botones, text="Nuevo usuario", width=120, command=nuevo).pack(side="left", padx=4)
    ctk.CTkButton(marco_botones, text="Editar", width=100, command=editar).pack(side="left", padx=4)
    ctk.CTkButton(marco_botones, text="Cambiar contraseña", width=150, command=contrasena).pack(side="left", padx=4)
    ctk.CTkButton(marco_botones, text="Eliminar", width=100,
                  fg_color="#8B2E2E", hover_color="#6E2323", command=eliminar).pack(side="left", padx=4)
    ctk.CTkButton(marco_botones, text="Volver al menú", width=120, command=ventana.destroy).pack(side="left", padx=4)

    cargar_tabla()


def _campo(ventana, etiqueta, **opciones):
    ctk.CTkLabel(ventana, text=etiqueta).pack(anchor="w", padx=30)
    entrada = ctk.CTkEntry(ventana, width=340, **opciones)
    entrada.pack(pady=(0, 10), padx=30)
    return entrada


def _abrir_formulario_usuario(padre, al_guardar, editar=None, es_propio=False):
    ventana = ctk.CTkToplevel(padre)
    ventana.title("Editar usuario" if editar else "Nuevo usuario")
    ventana.geometry("400x640" if not editar else "400x520")
    ventana.resizable(False, False)
    ventana.after(100, ventana.lift)
    ventana.after(150, ventana.grab_set)

    ctk.CTkLabel(ventana, text="Editar usuario" if editar else "Nuevo usuario",
                 font=("Arial", 18, "bold")).pack(pady=15)

    entrada_nombre = _campo(ventana, "Nombre completo")
    entrada_usuario = _campo(ventana, "Nombre de usuario (para iniciar sesión)")

    entrada_clave = entrada_clave2 = None
    if not editar:
        entrada_clave = _campo(ventana, f"Contraseña (mínimo {LARGO_MINIMO_CONTRASENA} caracteres)", show="*")
        entrada_clave2 = _campo(ventana, "Repetir contraseña", show="*")

    ctk.CTkLabel(ventana, text="Rol").pack(anchor="w", padx=30)
    combo_rol = ctk.CTkComboBox(ventana, width=340, state="readonly", values=ROLES)
    combo_rol.set("vendedor")
    combo_rol.pack(pady=(0, 10), padx=30)

    entrada_telefono = _campo(ventana, "Teléfono (opcional)")
    entrada_domicilio = _campo(ventana, "Domicilio (opcional)")

    if editar:
        entrada_nombre.insert(0, editar["nombre"])
        entrada_usuario.insert(0, editar["nombre_usuario"])
        combo_rol.set(editar["rol"])
        entrada_telefono.insert(0, editar["telefono"])
        entrada_domicilio.insert(0, editar["domicilio"])
        if es_propio:
            # Evita que el administrador se quite el rol a sí mismo y se quede sin acceso
            combo_rol.configure(state="disabled")
            ctk.CTkLabel(ventana, text="No podés cambiar tu propio rol.",
                         text_color="gray", font=("Arial", 11)).pack(anchor="w", padx=30)

    def guardar():
        nombre = entrada_nombre.get().strip()
        nombre_usuario = entrada_usuario.get().strip()
        if not nombre or not nombre_usuario:
            messagebox.showwarning("Datos incompletos", "Completá el nombre y el nombre de usuario.")
            return
        if " " in nombre_usuario:
            messagebox.showwarning("Dato inválido", "El nombre de usuario no puede tener espacios.")
            return

        if not editar:
            clave = entrada_clave.get()
            if len(clave) < LARGO_MINIMO_CONTRASENA:
                messagebox.showwarning(
                    "Contraseña débil",
                    f"La contraseña debe tener al menos {LARGO_MINIMO_CONTRASENA} caracteres.")
                return
            if clave != entrada_clave2.get():
                messagebox.showwarning("Dato inválido", "Las contraseñas no coinciden.")
                entrada_clave2.delete(0, "end")
                return

        telefono = entrada_telefono.get().strip()
        domicilio = entrada_domicilio.get().strip()
        rol = editar["rol"] if (editar and es_propio) else combo_rol.get()

        try:
            if editar:
                actualizar_usuario(editar["id_usuario"], nombre, nombre_usuario, rol, domicilio, telefono)
            else:
                agregar_usuario(nombre, nombre_usuario, clave, rol, domicilio, telefono)
        except (UsuarioDuplicado, UltimoAdministrador) as error:
            messagebox.showwarning("No se pudo guardar", str(error))
            return

        messagebox.showinfo("Listo", f"Usuario '{nombre_usuario}' guardado correctamente.")
        al_guardar()
        ventana.destroy()

    ctk.CTkButton(ventana, text="Guardar", width=160, height=36, command=guardar).pack(pady=15)


def _abrir_formulario_contrasena(padre, usuario_elegido):
    ventana = ctk.CTkToplevel(padre)
    ventana.title("Cambiar contraseña")
    ventana.geometry("400x340")
    ventana.resizable(False, False)
    ventana.after(100, ventana.lift)
    ventana.after(150, ventana.grab_set)

    ctk.CTkLabel(ventana, text="Cambiar contraseña", font=("Arial", 18, "bold")).pack(pady=(15, 2))
    ctk.CTkLabel(ventana, text=f"{usuario_elegido['nombre']} ({usuario_elegido['nombre_usuario']})",
                 text_color="gray").pack(pady=(0, 12))

    entrada_clave = _campo(ventana, f"Nueva contraseña (mínimo {LARGO_MINIMO_CONTRASENA} caracteres)", show="*")
    entrada_clave2 = _campo(ventana, "Repetir contraseña", show="*")

    def guardar():
        clave = entrada_clave.get()
        if len(clave) < LARGO_MINIMO_CONTRASENA:
            messagebox.showwarning(
                "Contraseña débil",
                f"La contraseña debe tener al menos {LARGO_MINIMO_CONTRASENA} caracteres.")
            return
        if clave != entrada_clave2.get():
            messagebox.showwarning("Dato inválido", "Las contraseñas no coinciden.")
            entrada_clave2.delete(0, "end")
            return
        try:
            cambiar_contrasena(usuario_elegido["id_usuario"], clave)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Listo", "La contraseña se cambió correctamente.")
        ventana.destroy()

    ctk.CTkButton(ventana, text="Guardar", width=160, height=36, command=guardar).pack(pady=10)
    
    