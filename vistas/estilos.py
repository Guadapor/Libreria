from tkinter import ttk


def aplicar_estilo_tabla():
    """Hace que los ttk.Treeview combinen con el tema oscuro de customtkinter."""
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure(
        "Treeview",
        background="#2b2b2b", foreground="#f2f2f2",
        fieldbackground="#2b2b2b", borderwidth=0, rowheight=26,
    )
    estilo.configure(
        "Treeview.Heading",
        background="#1f538d", foreground="white",
        relief="flat", font=("Arial", 10, "bold"),
    )
    estilo.map("Treeview",
               background=[("selected", "#E8833A")],
               foreground=[("selected", "white")])
    estilo.map("Treeview.Heading", background=[("active", "#2a6bb5")])