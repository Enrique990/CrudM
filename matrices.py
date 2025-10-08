# matrices.py

class Matriz:
    def __init__(self, datos):
        # Validaciones básicas
        # - Datos no vacíos
        #
        if not datos or not all(datos):
            raise ValueError("La matriz no puede estar vacía.")
        cols = len(datos[0])

        # - Todas las filas, igual cantidad de columnas
        for fila in datos:
            if len(fila) != cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas")
        
        # Guardo mi matriz(A), numero de filas y columnas tambn
        
        self.A = [row[:] for row in datos]
        self.n = len(datos)
        self.m = cols
        
        # Me crea el nombre de las variables x1, x2, ..., x(m-1)
        self.variables = [f"x{i+1}" for i in range(self.m-1)]

    """ Si es un numero entero, asi se muestra. Si tiene decimales, se muestra con 4 decimales"""
    def _format_number(self, x):
        if abs(x - int(x)) < 1e-10:
            return str(int(x))
        else:
            return f"{x:.4f}"
    # utiliza la funcion de arriba, pero la aplica a toda la matriz
    def _mat_str(self, mat):
        return [[self._format_number(x) for x in row] for row in mat]
    
    

    """ -------------------- MÉTODO GAUSS-JORDAN -------------------- """
    def gauss_jordan(self):
        A = [row[:] for row in self.A]  # trabajar sobre copia (para hacer distintas operaciones)
        n, m = self.n, self.m
        pasos = []
        pivotes = {}
        libres = set()
        fila = 0

        pasos.append({"descripcion": "Matriz inicial", "matriz": self._mat_str(A)})

        for col in range(m-1):
            pivot_row = None
            for r in range(fila, n):
                if abs(A[r][col]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                libres.add(col)
                pasos.append({"descripcion": f"{self.variables[col]}: variable libre (columna {col+1})", "matriz": self._mat_str(A)})
                continue

            if pivot_row != fila:
                A[fila], A[pivot_row] = A[pivot_row], A[fila]
                valor_pivote = self._format_number(A[fila][col])
                pasos.append({"descripcion": f"(*Pivote*, Fila: {fila+1}; Columna: {col+1}; Valor: {valor_pivote})\nF{fila+1} ↔ F{pivot_row+1}", "matriz": self._mat_str(A)})

            pivot = A[fila][col]
            # Solo agrego pivote en los pasos que ya existen
            if abs(pivot - 1) > 1e-10:
                A[fila] = [x/pivot for x in A[fila]]
                valor_pivote = self._format_number(pivot)
                pasos.append({"descripcion": f"(*Pivote*, Fila: {fila+1}; Columna: {col+1}; Valor: {valor_pivote})\nF{fila+1} → F{fila+1} / {valor_pivote}", "matriz": self._mat_str(A)})

            for r in range(n):
                if r != fila and abs(A[r][col]) > 1e-10:
                    factor = A[r][col]
                    A[r] = [A[r][k] - factor*A[fila][k] for k in range(m)]
                    valor_pivote = self._format_number(A[fila][col])
                    pasos.append({"descripcion": f"(*Pivote*, Fila: {fila+1}; Columna: {col+1}; Valor: {valor_pivote})\nF{r+1} → F{r+1} - ({self._format_number(factor)})*F{fila+1}", "matriz": self._mat_str(A)})

            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        # Detectar inconsistencia
        for r in range(n):
            if all(abs(A[r][c]) < 1e-10 for c in range(m-1)) and abs(A[r][-1]) > 1e-10:
                return {"pasos": pasos, "solucion": "Sin solución"}

        # Variables libres
        for col in range(m-1):
            if col not in pivotes:
                libres.add(col)

        # Construir solución
        solucion = {}
        if libres:
            for i in range(m-1):
                if i in libres:
                    solucion[self.variables[i]] = "libre"
                else:
                    fila = pivotes[i]
                    expr = self._format_number(A[fila][-1])
                    for j in sorted(libres):
                        coef = -A[fila][j]
                        if abs(coef) > 1e-10:
                            expr += f" + ({self._format_number(coef)})*{self.variables[j]}"
                    solucion[self.variables[i]] = expr
        else:
            for i in range(m-1):
                val = A[pivotes[i]][-1]
                solucion[self.variables[i]] = self._format_number(val)

        # Mensaje sobre el tipo de solución
        if libres:
            tipo_sol = "El sistema tiene infinitas soluciones (variables libres presentes)."
        else:
            tipo_sol = "El sistema tiene solución única."
        return {"pasos": pasos, "solucion": solucion, "mensaje": tipo_sol}

    # -------------------- MÉTODO GAUSS --------------------
    def gauss(self):
        A = [row[:] for row in self.A]  # trabajar sobre copia
        n, m = self.n, self.m
        pasos = []
        fila = 0

        pasos.append({"descripcion": "Matriz inicial", "matriz": self._mat_str(A)})

        for col in range(min(n, m-1)):
            pivot_row = None
            for r in range(fila, n):
                if abs(A[r][col]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                pasos.append({"descripcion": f"Columna {col+1}: variable libre", "matriz": self._mat_str(A)})
                continue

            if pivot_row != fila:
                A[fila], A[pivot_row] = A[pivot_row], A[fila]
                pasos.append({"descripcion": f"F{fila+1} ↔ F{pivot_row+1}", "matriz": self._mat_str(A)})

            pivot = A[fila][col]
            if abs(pivot-1) > 1e-10:
                A[fila] = [x/pivot for x in A[fila]]
                pasos.append({"descripcion": f"F{fila+1} → F{fila+1} / {self._format_number(pivot)}", "matriz": self._mat_str(A)})

            for r in range(fila+1, n):
                if abs(A[r][col]) > 1e-10:
                    factor = A[r][col]
                    A[r] = [A[r][k] - factor*A[fila][k] for k in range(m)]
                    pasos.append({"descripcion": f"F{r+1} → F{r+1} - ({self._format_number(factor)})*F{fila+1}", "matriz": self._mat_str(A)})

            fila += 1
            if fila >= n:
                break

        return {"pasos": pasos, "solucion": self._resolver_sustitucion(A)}

    def _resolver_sustitucion(self, A):
        eps = 1e-10
        n_vars = self.m - 1
        n_rows = self.n

        # 1) Detectar incompatibilidad y pivotes (columna -> fila)
        pivotes = {}
        for i in range(n_rows):
            fila = A[i]
            if all(abs(c) < eps for c in fila[:n_vars]) and abs(fila[-1]) > eps:
                return "Sistema incompatible, no tiene solución."
            # primer no-cero de la fila = pivote
            for j in range(n_vars):
                if abs(fila[j]) > eps:
                    pivotes[j] = i
                    break

        pivot_cols = sorted(pivotes.keys())
        free_cols = [j for j in range(n_vars) if j not in pivotes]

        # 2) Expresiones de variables pivote en términos de libres (y constante)
        #    Representamos una expresión como: {"const": c, <col_libre>: coef, ...}
        expr = {}  # expr[col_pivote] -> dict

        # Procesar de abajo hacia arriba (filas con pivote descendente)
        rows_by_desc = sorted(((row, col) for col, row in pivotes.items()), reverse=True)
        for row, pcol in rows_by_desc:
            piv = A[row][pcol]
            # RHS inicial (constante)
            cte = A[row][-1]
            terms = {}  # coeficientes para libres

            # Restar contribución de columnas libres
            for j in free_cols:
                coef = A[row][j]
                if abs(coef) > eps:
                    terms[j] = terms.get(j, 0.0) - coef

            # Restar contribución de pivotes "inferiores" (columnas de pivote mayores)
            for qcol, qrow in pivotes.items():
                if qcol <= pcol:
                    continue
                coef = A[row][qcol]
                if abs(coef) <= eps:
                    continue
                # expr[qcol] ya calculada
                qexpr = expr[qcol]
                cte -= coef * qexpr.get("const", 0.0)
                for lj, lcoef in qexpr.items():
                    if lj == "const":
                        continue
                    terms[lj] = terms.get(lj, 0.0) - coef * lcoef

            # Dividir todo por el pivote
            cte /= piv
            for k in list(terms.keys()):
                terms[k] /= piv

            e = {"const": cte}
            e.update({j: terms[j] for j in terms})
            expr[pcol] = e

        # 3) Formatear solución igual que gauss_jordan
        def fmt(v):
            return self._format_number(v)

        solucion = {}
        for j in range(n_vars):
            var = self.variables[j]
            if j in free_cols:
                solucion[var] = "libre"
            else:
                e = expr[j]
                partes = [fmt(e.get("const", 0.0))]
                for lj in sorted([k for k in e.keys() if k != "const"]):
                    coef = e[lj]
                    if abs(coef) > eps:
                        partes.append(f"+ ({fmt(coef)})*{self.variables[lj]}")
                # Siempre dejamos la constante primero (aunque sea 0) para que coincida con Gauss-Jordan
                solucion[var] = " ".join(partes) if partes else "0"

        return solucion

            