class Matriz:
    def __init__(self, datos):
        self.A = [row[:] for row in datos]  # copia de la matriz
        self.n = len(datos)
        self.m = len(datos[0])
        self.variables = [f"x{i+1}" for i in range(self.m-1)]

    def print_matrix(self):
        for row in self.A:
            print([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row])
        print()

    def gauss(self):
        print("Matriz inicial:")
        self.print_matrix()

        for i in range(self.n):
            print(f"\n--- Paso {i+1} ---")
            # Buscar pivote no cero
            pivot_row = None
            for r in range(i, self.n):
                if abs(self.A[r][i]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                print(f"Columna {i+1}: pivote cero, variable libre")
                continue  # posible variable libre
            if pivot_row != i:
                self.A[i], self.A[pivot_row] = self.A[pivot_row], self.A[i]
                print(f"Intercambio: F{i+1} <-> F{pivot_row+1}")
                self.print_matrix()

            pivot = self.A[i][i]
            if pivot == int(pivot):
                pivote_str = str(int(pivot))
            else:
                pivote_str = f"{pivot:.3f}"
            print(f"Pivote en F{i+1}: {pivote_str}")
            for j in range(i+1, self.n):
                if abs(self.A[j][i]) > 1e-10:
                    factor = self.A[j][i] / pivot
                    print(f"F{j+1} -> F{j+1} - ({factor:.3f})*F{i+1}")
                    for k in range(self.m):
                        self.A[j][k] -= factor * self.A[i][k]
                    self.print_matrix()
            print(f"Fin del paso {i+1}:")
            self.print_matrix()

        print("\nMatriz final en forma triangular superior:")
        self.print_matrix()
        self.sustitucion_adelante()

    def sustitucion_adelante(self):
        # Detectar pivotes y variables libres
        pivotes = {}
        libres = set(range(self.m-1))

        # Verificar incompatibilidad y redundancia
        incompatible = False
        filas_redundantes = False
        for idx, fila in enumerate(self.A):
            coeficientes = fila[:-1]
            termino_indep = fila[-1]
            if all(abs(c) < 1e-10 for c in coeficientes) and abs(termino_indep) > 1e-10:
                print("\nEl sistema NO tiene solución.")
                print(f"Fila {idx+1}: todos los coeficientes son cero y el término independiente es {termino_indep} ≠ 0.")
                print("Esto representa una ecuación imposible del tipo 0 = b (b ≠ 0).")
                incompatible = True
            if all(abs(c) < 1e-10 for c in coeficientes) and abs(termino_indep) < 1e-10:
                filas_redundantes = True
        if incompatible:
            print("\nResumen: Un sistema lineal no tiene solución cuando alguna ecuación es imposible (0 = b, b ≠ 0), es decir, las rectas/planos no se cruzan en ningún punto común.")
            print("Esto puede ocurrir por errores en los datos, ecuaciones contradictorias, o sistemas sobredeterminados.")
            return
        if filas_redundantes:
            print("\nEl sistema tiene ecuaciones redundantes (del tipo 0 = 0), lo que puede indicar infinitas soluciones o variables libres.")
            print("Esto ocurre cuando una fila de la matriz es todo ceros, incluyendo el término independiente.")
            print("Matemáticamente, esto representa ecuaciones dependientes o que no aportan información nueva.")

        # Continuar con el método clásico
        for i in range(self.n):
            for j in range(self.m-1):
                if abs(self.A[i][j]) > 1e-10:
                    pivotes[j] = i
                    if j in libres:
                        libres.remove(j)
                    break

        if libres:
            print("Variables libres:", [self.variables[i] for i in libres])
            sol = {v: f"{v}" for v in libres}

            # Resolver hacia atrás (expresión general)
            for col in reversed(range(self.m-1)):
                if col in libres:
                    continue
                fila = pivotes[col]
                expr = f"{self.A[fila][-1]:.1f}"
                for j in range(col+1, self.m-1):
                    if abs(self.A[fila][j]) > 1e-10:
                        coef = -self.A[fila][j]
                        if j in libres:
                            expr += f" + ({coef:.1f})*{self.variables[j]}"
                        else:
                            expr += f" + ({coef:.1f})*({sol[self.variables[j]]})"
                expr = f"({expr}) / {self.A[fila][col]:.1f}"
                sol[self.variables[col]] = expr

            print("Solución general:")
            for var in self.variables:
                valor = sol.get(var, "Indeterminado")
                print(f"{var} = {valor}")
        else:
            # No hay variables libres: solución única
            sol = [0.0] * (self.m-1)
            # Solo recorrer las filas que corresponden a incógnitas
            for i in range(self.m-2, -1, -1):
                suma = sum(self.A[i][j] * sol[j] for j in range(i+1, self.m-1))
                sol[i] = (self.A[i][-1] - suma) / self.A[i][i] if abs(self.A[i][i]) > 1e-10 else 0.0
            print("Solución única:")
            for idx, val in enumerate(sol):
                if val == int(val):
                    print(f"{self.variables[idx]} = {int(val)}")
                else:
                    print(f"{self.variables[idx]} = {val:.3f}")
if __name__ == "__main__":
    # Ejemplo de uso
    datos = [
        [2, -1, 1, 0], [1, 3, 2, 12], [1, -1, 2, 1]
    ]

    m = Matriz(datos)
    m.gauss()
