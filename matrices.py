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
        # Validación: matriz aumentada n x m (m > n)
        n = len(datos)
        if cols <= n:
            raise ValueError(f"La matriz debe tener más columnas que filas: {n} filas y al menos {n+1} columnas.")
        self.A = [row[:] for row in datos]  # copia de la matriz
        self.n = n
        self.m = cols
        self.variables = [f"x{i+1}" for i in range(self.m-1)]

    def print_matrix(self):
        for row in self.A:
            print([str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row])
        print()

    def gauss_jordan(self):
        import copy
        cols = len(self.A[0])
        pasos = []
        n = self.n
        m = self.m
        libres = set()
        incompatible = False

        # Guardar matriz inicial
        pasos.append("Matriz inicial:")
        pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in self.A])

        for i in range(n):
            # Buscar pivote no cero
            pivot_row = None
            for r in range(i, n):
                if abs(self.A[r][i]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                pasos.append(f"--- Paso {i+1} ---")
                pasos.append(f"Columna {i+1}: pivote cero, variable libre")
                pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in self.A])
                libres.add(i)
                continue
            if pivot_row != i:
                self.A[i], self.A[pivot_row] = self.A[pivot_row], self.A[i]
                pasos.append(f"--- Paso {i+1} ---")
                pasos.append(f"Intercambio: F{i+1} <-> F{pivot_row+1}")
                pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in copy.deepcopy(self.A)])

            pivot = self.A[i][i]
            if abs(pivot) < 1e-10:
                pasos.append(f"--- Paso {i+1} ---")
                pasos.append(f"Pivote en F{i+1} es cero, variable libre")
                pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in copy.deepcopy(self.A)])
                libres.add(i)
                continue
            # Normalizar fila pivote
            if abs(pivot - 1) > 1e-10:
                pasos.append(f"--- Paso {i+1} ---")
                pasos.append(f"F{i+1} -> F{i+1} / {pivot:.3f}")
                for k in range(m):
                    self.A[i][k] /= pivot
                pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in copy.deepcopy(self.A)])
            # Eliminar arriba y abajo
            for j in range(n):
                if j != i and abs(self.A[j][i]) > 1e-10:
                    factor = self.A[j][i]
                    pasos.append(f"--- Paso {i+1} ---")
                    pasos.append(f"F{j+1} -> F{j+1} - ({factor:.3f})*F{i+1}")
                    for k in range(m):
                        self.A[j][k] -= factor * self.A[i][k]
                    pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in copy.deepcopy(self.A)])

        # Marcar como libres todas las variables desde la columna n en adelante
        for i in range(n, m-1):
            libres.add(i)
        pasos.append("Matriz final en forma reducida por filas:")
        pasos.append([[str(int(x)) if x == int(x) else "{:.3f}".format(x) for x in row] for row in copy.deepcopy(self.A)])
        self.pasos = pasos

        # Mostrar en consola
        for paso in pasos:
            if isinstance(paso, str):
                print(paso)
            else:
                for fila in paso:
                    print(fila)

        # Verificar incompatibilidad (fila de ceros y término independiente no cero)
        for idx, fila in enumerate(self.A):
            if all(abs(fila[j]) < 1e-10 for j in range(m-1)) and abs(fila[-1]) > 1e-10:
                print(f"\nEl sistema NO tiene solución. Fila {idx+1}: todos los coeficientes son cero y el término independiente es {fila[-1]} ≠ 0.")
                print("Esto representa una ecuación imposible del tipo 0 = b (b ≠ 0).")
                incompatible = True
        if incompatible:
            print("\nResumen: Un sistema lineal no tiene solución cuando alguna ecuación es imposible (0 = b, b ≠ 0), es decir, las rectas/planos no se cruzan en ningún punto común.")
            print("Esto puede ocurrir por errores en los datos, ecuaciones contradictorias, o sistemas sobredeterminados.")
            return

        # Mostrar solución
        print("Solución:")
        if libres:
            print("Variables libres:", [self.variables[i] for i in sorted(libres)])
            for i in range(m-1):
                if i in libres:
                    print(f"{self.variables[i]} = libre")
                elif i < n:
                    expr = f"{self.A[i][-1]:.3f}"
                    for j in sorted(libres):
                        coef = -self.A[i][j] if j < m-1 else 0
                        if abs(coef) > 1e-10:
                            expr += f" + ({coef:.3f})*{self.variables[j]}"
                    print(f"{self.variables[i]} = {expr}")
                else:
                    print(f"{self.variables[i]} = libre")
        else:
            for i in range(m-1):
                if i < n:
                    val = self.A[i][-1]
                    if val == int(val):
                        print(f"{self.variables[i]} = {int(val)}")
                    else:
                        print(f"{self.variables[i]} = {val:.3f}")
                else:
                    print(f"{self.variables[i]} = libre")

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
            [1,6,2,-5,-2,-4],[0,0,2,-8,-1,3],[0,0,0,0,1,7]
        ]
        m = Matriz(datos)
        m.gauss_jordan()
    except NameError as e:
        print(f"Error: Hay una variable no definida en la matriz de entrada. {e}")
    except TypeError as e:
        print(f"Error: Hay un dato no numérico en la matriz de entrada. {e}")
    except ValueError as e:
        print(f"Error al inicializar la matriz: {e}")
        