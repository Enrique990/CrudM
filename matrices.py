class Matriz:
    def __init__(self, datos):
        # datos: tiene que ser la matriz aumentada lista de listas
        self.datos = datos
        self.procedimiento = [] 
        
    # Orientado al GUARDADO DE DATOS en JSON
    def to_list(self):
        """Devuelve los datos de la matriz como lista de listas (para JSON)."""
        return [list(fila) for fila in self.datos]

    @classmethod
    def from_list(cls, datos):
        """Crea una matriz a partir de una lista de listas (desde JSON)."""
        return cls(datos)
    
    
    #METODO DE GAUSS
    
    def es_cuadrada_aumentada(self):
        """Verifica que la matriz aumentada sea n x (n+1)."""
        if not self.datos:
            return False
        n = len(self.datos)
        m = len(self.datos[0])
        return n > 0 and m == n + 1
    
    def intercambiar_filas(self, i, j):
        """Intercambia las filas i y j de la matriz."""
        self.datos[i], self.datos[j] = self.datos[j], self.datos[i]
        self.procedimiento.append(f"  > Intercambio: F{i+1} <-> F{j+1}")
    
    def multiplicar_filas(self, i, factor):
        """Multiplica la fila i por un factor no nulo."""
        self.datos[i] = [val * factor for val in self.datos[i]]
        self.procedimiento.append(f"  > Normalización: F{i+1} -> ({factor:.3f}) * F{i+1}")
        
    def restar_filas_multiplicadas(self, fila_destino, fila_origen, factor):
        """Resta a la fila_destino la fila_origen multiplicada por un factor."""
        m = len(self.datos[0])
        self.datos[fila_destino] = [
            self.datos[fila_destino][j] - factor * self.datos[fila_origen][j]
            for j in range(m)
        ]
        self.procedimiento.append(f"  > Eliminación: F{fila_destino+1} -> F{fila_destino+1} - ({factor:.3f}) * F{fila_origen+1}")
    
    def imprimir_procedimiento(self):
        print("Procedimiento:")
        for paso in self.procedimiento:
            print(paso)
    
    def imprimir_matriz(self):
        for fila in self.datos:
            print("  ", [str(int(x)) if x == int(x) else "{:.1f}".format(x) for x in fila])
        print()
        
    def resolver_gauss(self):
            """Método principal para resolver el sistema de ecuaciones."""
            if not self.es_cuadrada_aumentada():
                raise ValueError("La matriz debe ser cuadrada aumentada (n x n+1).")

            n = len(self.datos)
            self.procedimiento.append("--- Paso 1: Eliminación progresiva (forma triangular superior) ---")
            
            # Eliminación hacia forma triangular
            for i in range(n):
                # Pivoteo parcial: buscar el elemento más grande en valor absoluto
                pivote_idx = i
                for k in range(i + 1, n):
                    if abs(self.datos[k][i]) > abs(self.datos[pivote_idx][i]):
                        pivote_idx = k
                
                if pivote_idx != i:
                    self.intercambiar_filas(i, pivote_idx)

                pivote = self.datos[i][i]
                
                # Manejo de sistemas singulares
                if pivote == 0:
                    raise ValueError("El sistema no tiene solución única (es singular).")
                
                # Normalizar la fila pivote para que el pivote sea 1
                if pivote != 1:
                    factor_normalizacion = 1.0 / pivote
                    self.multiplicar_filas(i, factor_normalizacion)

                # Eliminar debajo del pivote
                for k in range(i + 1, n):
                    factor = self.datos[k][i]
                    if factor != 0:
                        self.restar_filas_multiplicadas(k, i, factor)

            self.procedimiento.append("\n--- Paso 2: Sustitución regresiva ---")
            
            # Sustitución hacia atrás
            sol = [0.0] * n
            for i in range(n - 1, -1, -1):
                suma = sum(self.datos[i][j] * sol[j] for j in range(i + 1, n))
                sol[i] = (self.datos[i][-1] - suma)

            return sol
        
if __name__ == "__main__":
    # Definir la matriz aumentada para el sistema de ecuaciones:
    # 2x + y - z = 8
    # -3x - y + 2z = -11
    # -2x + y + 2z = -3

    matriz_aumentada = [
        [2, 1, -1, 8],
        [-3, -1, 2, -11],
        [-2, 1, 2, -3]
    ]

    print("--- Resolviendo un sistema de ecuaciones lineales con el Método de Gauss ---")
    print("\nMatriz inicial:")
    matriz = Matriz(matriz_aumentada)
    matriz.imprimir_matriz()

    try:
        soluciones = matriz.resolver_gauss()

        print("\nProcedimiento completo:")
        matriz.imprimir_procedimiento()
        
        print("\nMatriz final (forma triangular superior):")
        matriz.imprimir_matriz()
        
        # Formatear soluciones: entero si lo es, 1 decimal si no
        soluciones_fmt = [str(int(x)) if x == int(x) else "{:.1f}".format(x) for x in soluciones]
        print(f"\nSoluciones del sistema (x, y, z): {soluciones_fmt}")
        
    except ValueError as e:
        print(f"\nError: {e}")

    # Ejemplo de un sistema singular (sin solución única)
    print("\n--- Probando un sistema singular ---")
    matriz_singular = [
        [1, 2, 3, 4],
        [2, 4, 6, 8],
        [5, 1, 2, 3]
    ]

    matriz_singular_test = Matriz(matriz_singular)
    print("\nMatriz singular inicial:")
    matriz_singular_test.imprimir_matriz()
    
    try:
        matriz_singular_test.resolver_gauss()
    except ValueError as e:
        print(f"\nError: {e}")