from database.db import iniciar_base_datos
from modelos.usuarios import crear_admin_inicial
from vistas.menu_principal import abrir_login
from vistas.menu_princiapal import abrir_menu


def main(): 
    iniciar_base_datos() 
    crear_admin_inicial()

    usuario = abrir_login() 
    if usuario:
        abrir_menu(usuario)
        

if __name__ == "__main__":
    main()