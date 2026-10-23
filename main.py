from database.db import iniciar_base_datos
from modelos.usuarios import crear_admin_inicial
from vistas.login import abrir_login
from vistas.menu_principal import abrir_menu


def main(): 
    print("Iniciando base de datos...")
    iniciar_base_datos() 
    crear_admin_inicial()

    while True:
        print("Abriendo ventana de login...")
        usuario = abrir_login() 
        if not usuario:
            print("Login cancelado o cerrado.")
            break  
        
        print(f"Usuario logueado: {usuario['nombre']}. Abriendo menú...")
        cerro_sesion = abrir_menu(usuario)
        if not cerro_sesion:
            print("Saliendo del sistema...")
            break


if __name__ == "__main__":
    main()