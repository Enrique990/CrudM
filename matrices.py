class Matriz:
    def __init__(self, datos):
        if not datos or not all(datos):
            raise ValueError("La matriz no puede estar vacía.")
        cols = len(datos[0])
        for fila in datos:
            if len(fila) != cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas")
        if cols <= len(datos):
            raise ValueError("La matriz debe tener más columnas que filas")
        self.A = [row[:] for row in datos]
        self.n = len(datos)
        self.m = cols
        self.variables = [f"x{i+1}" for i in range(self.m-1)]

    def _format_number(self, x):
        if abs(x - int(x)) < 1e-10:
            return str(int(x))
        else:
            return f"{x:.4f}"

    def _mat_str(self, mat):
        return [[self._format_number(x) for x in row] for row in mat]

    def print_matrix(self, mat):
        for row in self._mat_str(mat):
            print(row)
        print()

    def gauss_jordan(self):
        A = self.A
        n, m = self.n, self.m
        pasos = []
        pivotes = {}
        libres = set()
        fila = 0

        pasos.append(("Inicial:", [row[:] for row in A]))

        for col in range(m-1):
            pivot_row = None
            for r in range(fila, n):
                if abs(A[r][col]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                libres.add(col)
                pasos.append((f"Columna {col+1}: variable libre", [row[:] for row in A]))
                continue

            if pivot_row != fila:
                A[fila], A[pivot_row] = A[pivot_row], A[fila]
                pasos.append((f"F{fila+1} ↔ F{pivot_row+1}", [row[:] for row in A]))

            pivot = A[fila][col]
            if abs(pivot - 1) > 1e-10:
                A[fila] = [x/pivot for x in A[fila]]
                pasos.append((f"F{fila+1} → F{fila+1} / {self._format_number(pivot)}", [row[:] for row in A]))

            for r in range(n):
                if r != fila and abs(A[r][col]) > 1e-10:
                    factor = A[r][col]
                    A[r] = [A[r][k] - factor*A[fila][k] for k in range(m)]
                    pasos.append((f"F{r+1} → F{r+1} - ({self._format_number(factor)})*F{fila+1}", [row[:] for row in A]))

            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        for r in range(n):
            if all(abs(A[r][c]) < 1e-10 for c in range(m-1)) and abs(A[r][-1]) > 1e-10:
                print("Sistema sin solución: fila", r+1, "da 0 =", self._format_number(A[r][-1]))
                return

        for col in range(m-1):
            if col not in pivotes:
                libres.add(col)

        for desc, mat in pasos:
            print(desc)
            self.print_matrix(mat)

        print("Solución:")
        if libres:
            print("Variables libres:", [self.variables[i] for i in sorted(libres)])
            for i in range(m-1):
                if i in libres:
                    print(f"{self.variables[i]} = libre")
                else:
                    fila = pivotes[i]
                    expr = self._format_number(A[fila][-1])
                    for j in sorted(libres):
                        coef = -A[fila][j]
                        if abs(coef) > 1e-10:
                            expr += f" + ({self._format_number(coef)})*{self.variables[j]}"
                    print(f"{self.variables[i]} = {expr}")
        else:
            for i in range(m-1):
                val = A[pivotes[i]][-1]
                print(f"{self.variables[i]} = {self._format_number(val)}")


