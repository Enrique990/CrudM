import json
import os

ARCHIVO_MATRICES = "matriz.json"
ARCHIVO_VECTORES = "vectores.json"

def _cargar_todos(archivo):
    if not os.path.exists(archivo):
        return {}
    try:
        with open(archivo, 'r') as file:
            datos = json.load(file)
        return datos
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _guardar_todos(datos, archivo):
    try:
        with open(archivo, 'w') as file:
            json.dump(datos, file, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar en el archivo {archivo}: {e}")
        return False

# --- Funciones para Matrices ---

def cargar_todas_matrices():
    return _cargar_todos(ARCHIVO_MATRICES)

def guardar_matriz(nombre, matriz_data):
    todas_las_matrices = cargar_todas_matrices()
    todas_las_matrices[nombre] = matriz_data
    return _guardar_todos(todas_las_matrices, ARCHIVO_MATRICES)

def cargar_matriz(nombre):
    todas_las_matrices = cargar_todas_matrices()
    return todas_las_matrices.get(nombre)

def eliminar_matriz(nombre):
    todas_las_matrices = cargar_todas_matrices()
    if nombre not in todas_las_matrices:
        return False
    del todas_las_matrices[nombre]
    return _guardar_todos(todas_las_matrices, ARCHIVO_MATRICES)

# --- Funciones para Vectores ---

def cargar_todos_vectores():
    return _cargar_todos(ARCHIVO_VECTORES)

def guardar_conjunto_vectores(nombre, vector_data):
    todos_los_vectores = cargar_todos_vectores()
    todos_los_vectores[nombre] = vector_data
    return _guardar_todos(todos_los_vectores, ARCHIVO_VECTORES)

def cargar_conjunto_vectores(nombre):
    todos_los_vectores = cargar_todos_vectores()
    return todos_los_vectores.get(nombre)

def eliminar_conjunto_vectores(nombre):
    todos_los_vectores = cargar_todos_vectores()
    if nombre not in todos_los_vectores:
        return False
    del todos_los_vectores[nombre]
    return _guardar_todos(todos_los_vectores, ARCHIVO_VECTORES)