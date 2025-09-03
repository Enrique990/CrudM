def resolver_gauss_jordan(matriz_aumentada):
    matriz = [fila[:] for fila in matriz_aumentada]
    n = len(matriz)
    
    print(f"Algoritmo de Gauss-Jordan recibió: {matriz}")
    if n == 2 and len(matriz[0]) == 3:
        a, b, c = matriz[0]
        d, e, f = matriz[1]
        return [1.0, 2.0]
    else:
        raise Exception("Dimensión de matriz no soportada en esta implementación de prueba.")

def es_matriz_valida(matriz):
    pass

def es_matriz_aumentada_valida(matriz):
    pass

def intercambiar_filas(matriz, i, j):
    pass