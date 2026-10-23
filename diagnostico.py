"""Diagnóstico de la Librería. Solo LEE: no modifica la base de datos ni ningún archivo.
Ponelo en la carpeta Libreria (al lado de main.py) y ejecutalo con:  python diagnostico.py
"""
import sys
import sqlite3
import traceback
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
problemas = []


def titulo(texto):
    print("\n=== " + texto + " ===")


def pista_de(error):
    texto = str(error)
    if "no such column" in texto:
        return ("La base de datos no tiene una columna que el código espera (probablemente 'costo'). "
                "Verificá que database/db.py sea la versión nueva y volvé a abrir la app: la base se actualiza sola.")
    if "no such table" in texto:
        return "Falta una tabla en la base de datos. Verificá database/db.py y volvé a abrir la app."
    if "syntax error" in texto.lower():
        return "Hay un error de sintaxis en una consulta SQL de ese archivo del modelo."
    return "Mandame este error completo."

titulo("1. Versiones de los archivos")
marcas = [
    ("database/db.py", "_agregar_columna_si_falta", "versión con costo (actualiza la base sola)"),
    ("modelos/libros.py", "l.costo", "versión con costo"),
    ("modelos/ventas.py", "costo_unitario", "versión con costo"),
    ("modelos/ganancias.py", "unidades_sin_costo", "versión con ganancia neta"),
    ("modelos/usuarios.py", "UltimoAdministrador", "versión con pantalla de usuarios"),
    ("modelos/stock.py", "agregar_stock", ""),
    ("modelos/movimientos.py", "obtener_movimientos", ""),
    ("vistas/estilos.py", "aplicar_estilo_tabla", ""),
    ("vistas/libros.py", "Editar costo", "versión con costo"),
    ("vistas/ventas.py", "estilos", "versión corregida para customtkinter"),
    ("vistas/stock.py", "abrir_stock", ""),
    ("vistas/movimientos.py", "abrir_movimientos", ""),
    ("vistas/ganancias.py", "abrir_ganancias", ""),
    ("vistas/usuarios.py", "abrir_usuarios", ""),
    ("vistas/menu_principal.py", "abrir_usuarios", "menú con las 6 pantallas conectadas"),
]
for ruta, marca, descripcion in marcas:
    archivo = RAIZ / ruta
    if not archivo.exists():
        print(f"FALTA  {ruta}")
        problemas.append(f"Falta el archivo {ruta}")
        continue
    contenido = archivo.read_text(encoding="utf-8", errors="replace")
    if marca in contenido:
        print(f"OK     {ruta}")
    else:
        print(f"VIEJO  {ruta}  <- no es la versión nueva ({descripcion})")
        problemas.append(f"{ruta} parece ser una versión anterior")
if (RAIZ / "vistas" / "estilo.py").exists():
    print("AVISO  existe vistas/estilo.py (sin 's'); sobra, podés borrarlo")

titulo("2. Base de datos")
try:
    from database import db
    ruta_db = Path(db.RUTA_DB).resolve()
    print("La app usa esta base:", ruta_db)
    print("Existe:", ruta_db.exists(), "| tamaño:", ruta_db.stat().st_size if ruta_db.exists() else 0, "bytes")
    otras = [p for p in RAIZ.rglob("libreria.db") if ".venv" not in p.parts and p.resolve() != ruta_db]
    for p in otras:
        print("AVISO  hay OTRA base en:", p)
        problemas.append(f"Hay otra libreria.db en {p}")

    con = sqlite3.connect(ruta_db)
    cur = con.cursor()
    esperadas = {"libros": "costo", "detalle_ventas": "costo_unitario"}
    for tabla in ("libros", "autores", "categorias", "usuarios", "ventas", "detalle_ventas", "movimientos_stock"):
        try:
            cur.execute(f"PRAGMA table_info({tabla})")
            columnas = [f[1] for f in cur.fetchall()]
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            filas = cur.fetchone()[0]
            print(f"  {tabla}: {filas} filas | columnas: {', '.join(columnas)}")
            if tabla in esperadas and esperadas[tabla] not in columnas:
                print(f"  >>> A la tabla '{tabla}' le falta la columna '{esperadas[tabla]}'")
                problemas.append(f"La tabla {tabla} no tiene la columna {esperadas[tabla]}")
        except sqlite3.Error as error:
            print(f"  {tabla}: ERROR {error}")
            problemas.append(f"Tabla {tabla}: {error}")
    try:
        cur.execute("SELECT COUNT(*) FROM libros l LEFT JOIN autores a ON l.id_autor = a.id_autor WHERE a.id_autor IS NULL")
        sin_autor = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM libros l LEFT JOIN categorias c ON l.id_categoria = c.id_categoria WHERE c.id_categoria IS NULL")
        sin_cat = cur.fetchone()[0]
        print(f"  libros sin autor válido: {sin_autor} | sin categoría válida: {sin_cat}")
        if sin_autor or sin_cat:
            problemas.append("Hay libros que apuntan a un autor o categoría que no existe")
    except sqlite3.Error:
        pass
    con.close()
except Exception:
    print("No se pudo revisar la base:")
    traceback.print_exc(file=sys.stdout)
    problemas.append("No se pudo abrir la base de datos")


titulo("3. Lo que leen las pantallas")
pruebas = [
    ("modelos.libros", "obtener_libros", "lista de libros (Libros, Ventas y Stock)"),
    ("modelos.libros", "obtener_autores", "autores"),
    ("modelos.libros", "obtener_categorias", "categorías"),
    ("modelos.movimientos", "obtener_movimientos", "movimientos"),
    ("modelos.ventas", "obtener_ventas", "ventas"),
    ("modelos.usuarios", "obtener_usuarios", "usuarios"),
]
for modulo, funcion, descripcion in pruebas:
    try:
        modulo_cargado = __import__(modulo, fromlist=[funcion])
        resultado = getattr(modulo_cargado, funcion)()
        print(f"OK     {funcion}() -> {len(resultado)} registros  [{descripcion}]")
        if funcion == "obtener_libros":
            for libro in resultado[:5]:
                print("          ", libro)
    except Exception as error:
        print(f"FALLA  {funcion}()  [{descripcion}]")
        traceback.print_exc(file=sys.stdout)
        print("   PISTA:", pista_de(error))
        problemas.append(f"{funcion}() falla: {error}")


titulo("RESUMEN")
if problemas:
    print("Encontré", len(problemas), "problema(s):")
    for p in problemas:
        print(" -", p)
else:
    print("No encontré problemas en los archivos, la base ni las consultas.")
    print("Entonces el problema está en las ventanas: contame exactamente qué ves y qué dice la terminal.")
print("\nCopiá TODO este texto y pegámelo en el chat.")