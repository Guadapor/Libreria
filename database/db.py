import sqlite3

def iniciar_base_datos():
    conexion = sqlite3.connect("database/libreria.db")
    cursor = conexion.cursor() 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS autores (
            id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos y tabla 'categorias' creadas correctamente.")

    if __name__ == "__main__": 
        iniciar_base_datos()

