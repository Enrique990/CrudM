class Matriz:
    def __init__(self, datos):
        # Validación: matriz no vacía
        if not datos or not all(datos):
            raise ValueError("La matriz no puede estar vacía.")
        # Validación: todas las filas de igual longitud
        cols = len(datos[0])
        for idx, fila in enumerate(datos):
            if len(fila) != cols:
                raise ValueError(f"La fila {idx+1} tiene {len(fila)} columnas, pero se esperaban {cols}.")
        # Validación: todos los datos numéricos
        for idx, fila in enumerate(datos):
            for jdx, val in enumerate(fila):
                if not isinstance(val, (int, float)):
                    raise ValueError(f"El valor en la fila {idx+1}, columna {jdx+1} ('{val}') no es numérico.")
        # Validación: matriz aumentada n x (n+1)
        n = len(datos)
        if cols != n + 1:
            raise ValueError(f"La matriz debe ser aumentada: {n} filas y {n+1} columnas.")
        self.A = [row[:] for row in datos]  # copia de la matriz
        self.n = n
        self.m = cols
        self.variables = [f"x{i+1}" for i in range(self.m-1)]

    def print_matrix(self):
        for row in self.A:
            print([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row])
        print()

    def gauss(self):
        # Validar que todas las filas tengan la misma longitud
        cols = len(self.A[0])
        for idx, fila in enumerate(self.A):
            if len(fila) != cols:
                msg = f"Error: La fila {idx+1} tiene {len(fila)} columnas, pero se esperaban {cols}. Todas las filas deben tener la misma longitud."
                print(msg)
                return
        print("Matriz inicial:")
        self.print_matrix()
        pasos = []
        pasos.append("Matriz inicial:")
        pasos.append([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in self.A)

        for i in range(self.n):
            operaciones = []
            # Buscar pivote no cero
            pivot_row = None
            for r in range(i, self.n):
                if abs(self.A[r][i]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                operaciones.append(f"Columna {i+1}: pivote cero, variable libre")
                if operaciones:
                    print(f"\n--- Paso {i+1} ---")
                    for op in operaciones:
                        print(op)
                continue  # posible variable libre
            if pivot_row != i:
                self.A[i], self.A[pivot_row] = self.A[pivot_row], self.A[i]
                operaciones.append(f"Intercambio: F{i+1} <-> F{pivot_row+1}")
                operaciones.append([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in self.A)

            pivot = self.A[i][i]
            if pivot == int(pivot):
                pivote_str = str(int(pivot))
            else:
                pivote_str = f"{pivot:.3f}"
            operaciones.append(f"Pivote en F{i+1}: {pivote_str}")
            hubo_operacion = False
            for j in range(i+1, self.n):
                if abs(self.A[j][i]) > 1e-10:
                    factor = self.A[j][i] / pivot
                    operaciones.append(f"F{j+1} -> F{j+1} - ({factor:.3f})*F{i+1}")
                    for k in range(self.m):
                        self.A[j][k] -= factor * self.A[i][k]
                    operaciones.append([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in self.A[j]])
                    hubo_operacion = True
            if operaciones:
                print(f"\n--- Paso {i+1} ---")
                for op in operaciones:
                    print(op)
                pasos.append(f"--- Paso {i+1} ---")
                pasos.extend(operaciones)
            if hubo_operacion:
                print(f"Fin del paso {i+1}:")
                self.print_matrix()
                pasos.append("Fin del paso {i+1}:")
                pasos.append([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in self.A)

        print("\nMatriz final en forma triangular superior:")
        self.print_matrix()
        pasos.append("Matriz final en forma triangular superior:")
        pasos.append([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in self.A)
        self.pasos = pasos
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
    try:
        # Ejemplo de uso
        datos = [
            [1, 0, -5, 1],[0,1,1,4],[0,0,0,0]
        ]
        m = Matriz(datos)
        m.gauss()
    except NameError as e:
        print(f"Error: Hay una variable no definida en la matriz de entrada. {e}")
    except TypeError as e:
        print(f"Error: Hay un dato no numérico en la matriz de entrada. {e}")
    except ValueError as e:
        print(f"Error al inicializar la matriz: {e}")
        