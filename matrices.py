from fractions import Fraction  # Importa Fraction para trabajar con fracciones exactas

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

    # Recorre cada columna (excepto la última, que es el término independiente)
    for col in range(n):
        # 1. Buscar el pivote en la posición (col, col)
        pivote = matriz[col][col]
        if abs(pivote) < 1e-12:
            # Si el pivote es cero, busca una fila más abajo con un pivote no nulo y la intercambia
            for fila_buscada in range(col + 1, n):
                if abs(matriz[fila_buscada][col]) > 1e-12:
                    matriz[col], matriz[fila_buscada] = matriz[fila_buscada], matriz[col]  # Intercambio de filas
                    print(f"R{col+1} ← R{fila_buscada+1}")
                    imprimir_matriz(matriz)
                    pivote = matriz[col][col]
                    break
            else:
                # Si no encuentra un pivote válido, el sistema no tiene solución única
                raise Exception("El sistema no tiene solución única (pivote cero).")

        # 2. Hacer el pivote igual a 1 dividiendo toda la fila por el valor del pivote
        if pivote != 1:
            factor = pivote
            matriz[col] = [v / factor for v in matriz[col]]
            print(f"R{col+1} ← R{col+1} / {factor}")
            imprimir_matriz(matriz)

        # 3. Hacer ceros en la columna actual para todas las demás filas
        for fila in range(n):
            if fila != col:
                factor = matriz[fila][col]
                if abs(factor) > 1e-12:
                    # Restar un múltiplo de la fila pivote para hacer cero el elemento actual
                    matriz[fila] = [
                        v - factor * matriz[col][i]
                        for i, v in enumerate(matriz[fila])
                    ]
                    print(f"R{fila+1} ← R{fila+1} - ({factor})·R{col+1}")
                    imprimir_matriz(matriz)

    # La solución está en la última columna de la matriz reducida
    solucion = [matriz[i][-1] for i in range(n)]
    print("Solución encontrada (fracciones):")
    for i, valor in enumerate(solucion):
        print(f"x{i+1} = {valor}   (≈ {float(valor):.6f})")
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