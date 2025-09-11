from fractions import Fraction

def imprimir_matriz(matriz, mensaje="Matriz actual:"):
    """
    Imprime la matriz en consola con un mensaje opcional.
    Cada número se muestra alineado y en formato de fracción.
    """
    print(f"\n{mensaje}")
    for fila in matriz:
        # Imprime cada fila con los valores alineados a la derecha (5 espacios)
        print("  [" + " ".join(f"{str(v):>5}" for v in fila) + "]")
    print()

def resolver_gauss_jordan(matriz_aumentada):
    """
    Resuelve un sistema de ecuaciones lineales usando el método de Gauss-Jordan.
    La matriz debe ser aumentada (n filas, n+1 columnas).
    Muestra el proceso paso a paso y devuelve la solución.
    """
    # Convierte todos los valores de la matriz a fracciones para mayor precisión
    matriz = [[Fraction(v) for v in fila] for fila in matriz_aumentada]
    n = len(matriz)      # Número de filas (y ecuaciones)
    m = len(matriz[0])   # Número de columnas (incógnitas + 1)

    imprimir_matriz(matriz, "Matriz aumentada inicial:")

    # Gauss-Jordan: reducción a forma escalonada reducida
    fila_actual = 0
    pivotes = [-1] * n  # Guarda la columna del pivote de cada fila
    for col in range(m-1):
        # Buscar fila con pivote no nulo
        pivote_encontrado = False
        for f in range(fila_actual, n):
            if matriz[f][col] != 0:
                matriz[fila_actual], matriz[f] = matriz[f], matriz[fila_actual]
                pivote_encontrado = True
                break
        if not pivote_encontrado:
            continue  # No hay pivote en esta columna, variable libre

        pivote = matriz[fila_actual][col]
        matriz[fila_actual] = [v / pivote for v in matriz[fila_actual]]
        print(f"R{fila_actual+1} ← R{fila_actual+1} / {pivote}")
        imprimir_matriz(matriz)

        # Hacer ceros en la columna actual para todas las demás filas
        for f in range(n):
            if f != fila_actual and matriz[f][col] != 0:
                factor = matriz[f][col]
                matriz[f] = [
                    v - factor * matriz[fila_actual][i]
                    for i, v in enumerate(matriz[f])
                ]
                print(f"R{f+1} ← R{f+1} - ({factor})·R{fila_actual+1}")
                imprimir_matriz(matriz)
        pivotes[fila_actual] = col
        fila_actual += 1
        if fila_actual == n:
            break

    # Detectar sistema incompatible
    for fila in matriz:
        if all(v == 0 for v in fila[:-1]) and fila[-1] != 0:
            return ["El sistema es incompatible y no tiene solución."]

    # Identificar variables libres y pivote
    var_libres = []
    var_pivote = {}
    for i, col in enumerate(pivotes):
        if col != -1:
            var_pivote[col] = i
    for j in range(m-1):
        if j not in var_pivote:
            var_libres.append(j)

    # Construir la solución general
    solucion = []
    for j in range(m-1):
        if j in var_libres:
            solucion.append(f"x{j+1} (libre), x{j+1}∈ℝ")
        else:
            fila_idx = var_pivote[j]
            val = matriz[fila_idx][-1]
            expr = f"{val}"
            for k in var_libres:
                coef = -matriz[fila_idx][k]
                if coef != 0:
                    if coef > 0:
                        expr += f" + {coef}*x{k+1}"
                    else:
                        expr += f" - {abs(coef)}*x{k+1}"
            solucion.append(f"x{j+1} = {expr}")
    return solucion

def es_matriz_valida(matriz):
    """
    Verifica que todas las filas de la matriz tengan la misma longitud.
    Devuelve True si es válida, False si no.
    """
    if not matriz or not all(len(fila) == len(matriz[0]) for fila in matriz):
        return False
    return True

def es_matriz_aumentada_valida(matriz):
    """
    Verifica que la matriz sea aumentada: n filas y n+1 columnas.
    Devuelve True si es válida, False si no.
    """
    if not matriz or len(matriz[0]) != len(matriz) + 1:
        return False
    return True

def intercambiar_filas(matriz, i, j):
    """
    Intercambia las filas i y j de la matriz.
    """
    matriz[i], matriz[j] = matriz[j], matriz[i]