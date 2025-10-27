import persistencia
import matrices

def crear_matriz(nombre, filas, columnas, datos):
    nueva_matriz = {
        "nombre": nombre,
        "filas": filas,
        "columnas": columnas,
        "datos": datos
    }
    
    if persistencia.guardar_matriz(nombre, nueva_matriz):
        print(f"Matriz '{nombre}' creada y guardada exitosamente.")
    else:
        print(f"Error: No se pudo guardar la matriz '{nombre}'. ¿Ya existe?")

def listar_matrices():
    matrices = persistencia.cargar_todas_matrices()
    if not matrices:
        print("No hay matrices almacenadas.")
        return
    
    print("\nMatrices almacenadas:")
    for nombre_matriz in matrices.keys():
        print(f"- {nombre_matriz}")

def ver_matriz(nombre):
    matriz = persistencia.cargar_matriz(nombre)
    if matriz is None:
        print(f"Error: No se encontró la matriz '{nombre}'.")
        return
    
    print(f"\nMatriz: {matriz['nombre']}")
    print(f"Dimensiones: {matriz['filas']}x{matriz['columnas']}")
    print("Datos:")
    for fila in matriz['datos']:
        print(fila)

def actualizar_matriz(nombre_matriz, nuevos_datos, nuevas_filas, nuevas_columnas):
    matriz_actualizada = {
        "nombre": nombre_matriz,
        "filas": nuevas_filas,
        "columnas": nuevas_columnas,
        "datos": nuevos_datos
    }
    if persistencia.actualizar_matriz(nombre_matriz, matriz_actualizada):
        print(f"Matriz '{nombre_matriz}' actualizada exitosamente.")
        return True
    print(f"Error: No se pudo actualizar la matriz '{nombre_matriz}'.")
    return False

def eliminar_matriz(nombre):
    if persistencia.eliminar_matriz(nombre):
        print(f"Matriz '{nombre}' eliminada exitosamente.")
    else:
        print(f"Error: No se pudo eliminar la matriz '{nombre}'. ¿Existe?")

def resolver_matriz(nombre):
    matriz = persistencia.cargar_matriz(nombre)
    if matriz is None:
        print(f"Error: No se encontró la matriz '{nombre}'.")
        return
    
    try:
        solucion = matrices.resolver_gauss_jordan(matriz['datos'])
        print(f"Solución del sistema para la matriz '{nombre}':")
        for i, valor in enumerate(solucion):
            print(f"x{i+1} = {valor}")
    except Exception as e:
        print(f"Error durante la resolución: {e}")

# --- Funciones CRUD para Conjuntos de Vectores ---

def crear_conjunto_vectores(nombre, num_vectores, dimension, datos):
    nuevo_conjunto = {
        "nombre": nombre,
        "num_vectores": num_vectores,
        "dimension": dimension,
        "datos": datos
    }
    if persistencia.guardar_conjunto_vectores(nombre, nuevo_conjunto):
        print(f"Conjunto de vectores '{nombre}' creado y guardado exitosamente.")
        return True
    else:
        print(f"Error: No se pudo guardar el conjunto de vectores '{nombre}'.")
        return False

def actualizar_conjunto_vectores(nombre, nuevos_datos, nuevo_num_vectores, nueva_dimension):
    conjunto_actualizado = {
        "nombre": nombre,
        "num_vectores": nuevo_num_vectores,
        "dimension": nueva_dimension,
        "datos": nuevos_datos
    }
    if persistencia.actualizar_conjunto_vectores(nombre, conjunto_actualizado):
        return True
    print(f"Error: No se pudo actualizar el conjunto de vectores '{nombre}'.")
    return False

# --- Funciones CRUD para Conjuntos de Matrices (operadores) ---

def crear_conjunto_matrices(nombre, num_matrices, filas, columnas, datos):
    """Crea y guarda un conjunto de matrices con dimensiones uniformes.
    - datos: lista de 'num_matrices' matrices, cada una una lista de listas de tamaño filas x columnas.
    """
    conjunto = {
        "nombre": nombre,
        "num_matrices": num_matrices,
        "filas": filas,
        "columnas": columnas,
        "datos": datos
    }
    if persistencia.guardar_conjunto_matrices(nombre, conjunto):
        print(f"Conjunto de matrices '{nombre}' creado y guardado exitosamente.")
        return True
    else:
        print(f"Error: No se pudo guardar el conjunto de matrices '{nombre}'.")
        return False

def actualizar_conjunto_matrices(nombre, nuevos_datos, nuevo_num, nuevas_filas, nuevas_columnas):
    conjunto_actualizado = {
        "nombre": nombre,
        "num_matrices": nuevo_num,
        "filas": nuevas_filas,
        "columnas": nuevas_columnas,
        "datos": nuevos_datos
    }
    if persistencia.actualizar_conjunto_matrices(nombre, conjunto_actualizado):
        return True
    print(f"Error: No se pudo actualizar el conjunto de matrices '{nombre}'.")
    return False