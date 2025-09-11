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
    if not matriz:
        print(f"No se encontró la matriz '{nombre}'.")
        return
    datos = matriz['datos']
    print(f"Solución del sistema para la matriz '{nombre}':")
    try:
        matriz_reducida = matrices.resolver_gauss_jordan(datos)
        if matriz_reducida is None:
            return
        for fila in matriz_reducida:
            print(fila)
        print("\nSistema resuelto por variable:")
        mostrar_solucion_sistema(matriz_reducida)
    except Exception as e:
        print(f"Error durante la resolución: {e}")

def mostrar_solucion_sistema(matriz, nombres_variables=None):
    try:
        matriz = [[float(valor) for valor in fila] for fila in matriz]
    except Exception as e:
        print("Error: La matriz contiene valores no numéricos. Revisa los datos guardados.")
        return
    filas = len(matriz)
    columnas = len(matriz[0]) - 1  # última columna es el término independiente
    if not nombres_variables:
        nombres_variables = [f"x{i+1}" for i in range(columnas)]

    pivotes = [-1] * filas
    for i in range(filas):
        for j in range(columnas):
            if abs(matriz[i][j]) > 1e-10:
                pivotes[i] = j
                break

    variable_es_pivote = [False] * columnas
    for p in pivotes:
        if p != -1:
            variable_es_pivote[p] = True

    for idx_var in range(columnas):
        if variable_es_pivote[idx_var]:
            # Buscar la fila donde está el pivote de esta variable
            fila = pivotes.index(idx_var)
            coef_libres = []
            for j in range(idx_var+1, columnas):
                if abs(matriz[fila][j]) > 1e-10:
                    signo = '-' if matriz[fila][j] > 0 else '+'
                    valor = abs(matriz[fila][j])
                    if valor == 1:
                        coef_libres.append(f"{signo} {nombres_variables[j]}")
                    else:
                        coef_libres.append(f"{signo} {valor}{nombres_variables[j]}")
            rhs = matriz[fila][-1]
            expresion = f"{nombres_variables[idx_var]} = {rhs:.4g}"
            if coef_libres:
                expresion += ' ' + ' '.join(coef_libres)
            print(expresion)
        else:
            print(f"{nombres_variables[idx_var]} = {nombres_variables[idx_var]} (variable libre)")