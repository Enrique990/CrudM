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

def actualizar_matriz(nombre):
    print("Función de actualizar no implementada aún.")
    pass

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