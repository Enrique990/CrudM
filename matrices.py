from fractions import Fraction

def imprimir_matriz(matriz, mensaje="Matriz actual:"):
    print(f"\n{mensaje}")
    for fila in matriz:
        print("  [" + " ".join(f"{str(v):>5}" for v in fila) + "]")
    print()

def resolver_gauss_jordan(matriz_aumentada):
    # Convertir todos los valores a fracciones
    matriz = [[Fraction(v) for v in fila] for fila in matriz_aumentada]
    n = len(matriz)
    m = len(matriz[0])

    imprimir_matriz(matriz, "Matriz aumentada inicial:")

    for col in range(n):
        # 1. Buscar el pivote
        pivote = matriz[col][col]
        if abs(pivote) < 1e-12:
            # Buscar una fila abajo con un pivote no nulo
            for fila_buscada in range(col + 1, n):
                if abs(matriz[fila_buscada][col]) > 1e-12:
                    matriz[col], matriz[fila_buscada] = matriz[fila_buscada], matriz[col]
                    print(f"R{col+1} ← R{fila_buscada+1}")
                    imprimir_matriz(matriz)
                    pivote = matriz[col][col]
                    break
            else:
                raise Exception("El sistema no tiene solución única (pivote cero).")

        # 2. Hacer el pivote igual a 1
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
                    matriz[fila] = [
                        v - factor * matriz[col][i]
                        for i, v in enumerate(matriz[fila])
                    ]
                    print(f"R{fila+1} ← R{fila+1} - ({factor})·R{col+1}")
                    imprimir_matriz(matriz)

    # Solución: última columna
    solucion = [matriz[i][-1] for i in range(n)]
    print("Solución encontrada (fracciones):")
    for i, valor in enumerate(solucion):
        print(f"x{i+1} = {valor}   (≈ {float(valor):.6f})")
    return solucion

def es_matriz_valida(matriz):
    # Verifica que todas las filas tengan la misma longitud
    if not matriz or not all(len(fila) == len(matriz[0]) for fila in matriz):
        return False
    return True

def es_matriz_aumentada_valida(matriz):
    # Debe tener n filas y n+1 columnas
    if not matriz or len(matriz[0]) != len(matriz) + 1:
        return False
    return True

def intercambiar_filas(matriz, i, j):
    matriz[i], matriz[j] = matriz[j], matriz[i]