import json
import os

ARCHIVO_MATRICES = "matriz.json"
ARCHIVO_VECTORES = "vectores.json"
ARCHIVO_CONJUNTOS_MATRICES = "conjuntos_matrices.json"
ARCHIVO_ECUACIONES = "ecuaciones.json"

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

# Refactorización: helper para guardar todas las matrices
def guardar_todas_matrices(matrices_data):
    return _guardar_todos(matrices_data, ARCHIVO_MATRICES)

# Refactorización: helper para guardar todos los conjuntos de vectores
def guardar_todos_vectores(vectores_data):
    return _guardar_todos(vectores_data, ARCHIVO_VECTORES)

# Refactorización: helper para guardar todas las ecuaciones
def guardar_todas_ecuaciones(ecuaciones_data):
    return _guardar_todos(ecuaciones_data, ARCHIVO_ECUACIONES)

# --- Funciones para Matrices ---

def cargar_todas_matrices():
    return _cargar_todos(ARCHIVO_MATRICES)

def guardar_matriz(nombre, matriz_data):
    todas_las_matrices = cargar_todas_matrices()
    todas_las_matrices[nombre] = matriz_data
    return guardar_todas_matrices(todas_las_matrices)

# Refactorización: actualización centralizada de matrices
def actualizar_matriz(nombre, matriz_data):
    todas_las_matrices = cargar_todas_matrices()
    if nombre not in todas_las_matrices:
        return False
    todas_las_matrices[nombre] = matriz_data
    return guardar_todas_matrices(todas_las_matrices)

def cargar_matriz(nombre):
    todas_las_matrices = cargar_todas_matrices()
    return todas_las_matrices.get(nombre)

def eliminar_matriz(nombre):
    todas_las_matrices = cargar_todas_matrices()
    if nombre not in todas_las_matrices:
        return False
    del todas_las_matrices[nombre]
    return guardar_todas_matrices(todas_las_matrices)

# --- Funciones para Vectores ---

def cargar_todos_vectores():
    return _cargar_todos(ARCHIVO_VECTORES)

def guardar_conjunto_vectores(nombre, vector_data):
    todos_los_vectores = cargar_todos_vectores()
    todos_los_vectores[nombre] = vector_data
    return guardar_todos_vectores(todos_los_vectores)

# Refactorización: actualización centralizada de conjuntos de vectores
def actualizar_conjunto_vectores(nombre, vector_data):
    todos_los_vectores = cargar_todos_vectores()
    if nombre not in todos_los_vectores:
        return False
    todos_los_vectores[nombre] = vector_data
    return guardar_todos_vectores(todos_los_vectores)

def cargar_conjunto_vectores(nombre):
    todos_los_vectores = cargar_todos_vectores()
    return todos_los_vectores.get(nombre)

def eliminar_conjunto_vectores(nombre):
    todos_los_vectores = cargar_todos_vectores()
    if nombre not in todos_los_vectores:
        return False
    del todos_los_vectores[nombre]
    return guardar_todos_vectores(todos_los_vectores)

# --- Funciones para Conjuntos de Matrices ---

def cargar_todos_conjuntos_matrices():
    return _cargar_todos(ARCHIVO_CONJUNTOS_MATRICES)

def guardar_conjunto_matrices(nombre, conjunto_data):
    todos = cargar_todos_conjuntos_matrices()
    todos[nombre] = conjunto_data
    return _guardar_todos(todos, ARCHIVO_CONJUNTOS_MATRICES)

def actualizar_conjunto_matrices(nombre, conjunto_data):
    todos = cargar_todos_conjuntos_matrices()
    if nombre not in todos:
        return False
    todos[nombre] = conjunto_data
    return _guardar_todos(todos, ARCHIVO_CONJUNTOS_MATRICES)

def cargar_conjunto_matrices(nombre):
    todos = cargar_todos_conjuntos_matrices()
    return todos.get(nombre)

def eliminar_conjunto_matrices(nombre):
    todos = cargar_todos_conjuntos_matrices()
    if nombre not in todos:
        return False
    del todos[nombre]
    return _guardar_todos(todos, ARCHIVO_CONJUNTOS_MATRICES)

# --- Funciones para Ecuaciones (Métodos numéricos) ---

def cargar_todas_ecuaciones():
    return _cargar_todos(ARCHIVO_ECUACIONES)

def guardar_ecuacion(nombre, ecuacion_data):
    todas = cargar_todas_ecuaciones()
    todas[nombre] = ecuacion_data
    return guardar_todas_ecuaciones(todas)

def actualizar_ecuacion(nombre, ecuacion_data):
    todas = cargar_todas_ecuaciones()
    if nombre not in todas:
        return False
    todas[nombre] = ecuacion_data
    return guardar_todas_ecuaciones(todas)

def cargar_ecuacion(nombre):
    todas = cargar_todas_ecuaciones()
    return todas.get(nombre)

def eliminar_ecuacion(nombre):
    todas = cargar_todas_ecuaciones()
    if nombre not in todas:
        return False
    del todas[nombre]
    return guardar_todas_ecuaciones(todas)