import json
import os

ARCHIVO_DATOS = "matriz.json"

def cargar_todas_matrices():
    if not os.path.exists(ARCHIVO_DATOS):
        return {}
    
    try:
        with open(ARCHIVO_DATOS, 'r') as file:
            datos = json.load(file)
        return datos
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def guardar_matriz(nombre, matriz_data):
    todas_las_matrices = cargar_todas_matrices()
    
    todas_las_matrices[nombre] = matriz_data
    
    try:
        with open(ARCHIVO_DATOS, 'w') as file:
            json.dump(todas_las_matrices, file, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar en el archivo: {e}")
        return False

def cargar_matriz(nombre):
    todas_las_matrices = cargar_todas_matrices()
    return todas_las_matrices.get(nombre)

def eliminar_matriz(nombre):
    todas_las_matrices = cargar_todas_matrices()
    
    if nombre not in todas_las_matrices:
        return False
    
    del todas_las_matrices[nombre]
    
    try:
        with open(ARCHIVO_DATOS, 'w') as file:
            json.dump(todas_las_matrices, file, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar los cambios: {e}")
        return False