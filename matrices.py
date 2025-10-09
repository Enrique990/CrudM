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

        # Reutilizar el forward elimination privado
        A, pivotes, pasos_elim = self._forward_elimination(A)
        pasos.extend(pasos_elim)

        return {"pasos": pasos, "solucion": self._resolver_sustitucion(A)}

    def _forward_elimination(self, A):
        """Realiza eliminación hacia adelante (como en Gauss), retorna la matriz transformada,
        el dict de pivotes (col -> fila) y la lista de pasos (mismo formato que gauss/gauss_jordan).
        """
        n, m = self.n, self.m
        pasos = []
        pivotes = {}
        fila = 0

        pasos.append({"descripcion": "Matriz inicial", "matriz": self._mat_str(A)})

        for col in range(min(n, m-1)):
            pivot_row = None
            for r in range(fila, n):
                if abs(A[r][col]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                pasos.append({"descripcion": f"{self.variables[col]}: columna sin pivote (variable libre)", "matriz": self._mat_str(A)})
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

            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        return A, pivotes, pasos

    def independencia(self):
        """Determina si las columnas (coeficientes) son linealmente independientes.
        Reutiliza _forward_elimination para obtener pivotes y pasos.
        """
        A = [row[:] for row in self.A]
        A_after, pivotes, pasos = self._forward_elimination(A)

        num_cols = self.m - 1
        rango = len(pivotes)
        pivot_cols = sorted(pivotes.keys())
        libres = [c for c in range(num_cols) if c not in pivotes]

        independiente = (rango == num_cols)

        if independiente:
            mensaje = f"La matriz de coeficientes tiene rango {rango} y {num_cols} columna(s): es linealmente independiente."
        else:
            libres_nombres = ", ".join(self.variables[c] for c in libres) if libres else "ninguna"
            mensaje = (f"La matriz es linealmente dependiente: rango {rango} < {num_cols}. "
                       f"Columnas sin pivote (libres): {libres_nombres}.")

        solucion = {
            "independiente": independiente,
            "rango": rango,
            "pivotes": [c + 1 for c in pivot_cols],
            "libres": [c + 1 for c in libres]
        }

        return {"pasos": pasos, "solucion": solucion, "mensaje": mensaje}

    def trasponer(self):
        """Devuelve una nueva instancia de Matriz que es la traspuesta de la actual.
        No modifica la matriz original.
        """
        # Construir la traspuesta: filas -> columnas
        trans = [[self.A[r][c] for r in range(self.n)] for c in range(self.m)]
        return Matriz(trans)

    # alias en inglés por conveniencia
    transpose = trasponer

    # -------------------- OPERACIONES ENTRE MATRICES --------------------
    def _ensure_matriz_input(self, other):
        """Acepta otra Matriz o una lista de listas y devuelve una instancia de Matriz."""
        if isinstance(other, Matriz):
            return other
        if isinstance(other, list):
            return Matriz(other)
        raise ValueError("El operando debe ser una Matriz o una lista de listas.")

    def sumar(self, other):
        """Suma elemento a elemento con otra matriz de igual tamaño.
        Devuelve dict con pasos, datos (lista) y una instancia de Matriz en 'resultado_matriz'.
        """
        B = self._ensure_matriz_input(other)
        if self.n != B.n or self.m != B.m:
            raise ValueError("Las dimensiones deben coincidir para sumar matrices.")

        result = [[self.A[i][j] + B.A[i][j] for j in range(self.m)] for i in range(self.n)]
        pasos = [
            {"descripcion": "Matriz A", "matriz": self._mat_str(self.A)},
            {"descripcion": "Matriz B", "matriz": B._mat_str(B.A)},
            {"descripcion": "Resultado de A + B", "matriz": self._mat_str(result)}
        ]
        return {"pasos": pasos, "datos": result, "resultado_matriz": Matriz(result), "mensaje": "Suma realizada."}

    def restar(self, other):
        """Resta elemento a elemento con otra matriz de igual tamaño.
        """
        B = self._ensure_matriz_input(other)
        if self.n != B.n or self.m != B.m:
            raise ValueError("Las dimensiones deben coincidir para restar matrices.")

        result = [[self.A[i][j] - B.A[i][j] for j in range(self.m)] for i in range(self.n)]
        pasos = [
            {"descripcion": "Matriz A", "matriz": self._mat_str(self.A)},
            {"descripcion": "Matriz B", "matriz": B._mat_str(B.A)},
            {"descripcion": "Resultado de A - B", "matriz": self._mat_str(result)}
        ]
        return {"pasos": pasos, "datos": result, "resultado_matriz": Matriz(result), "mensaje": "Resta realizada."}

    def multiplicar(self, other):
        """Multiplica la matriz por otra (A * B). Valida conformabilidad (m == other.n).
        Devuelve pasos (explicación breve por matrices), datos y Matriz resultante.
        """
        B = self._ensure_matriz_input(other)
        if self.m != B.n:
            raise ValueError("Dimensiones no conformables para multiplicación (A.m debe ser igual a B.n).")

        # Producto (n x m) * (m x p) -> (n x p) where p = B.m
        n = self.n
        p = B.m
        result = [[0.0 for _ in range(p)] for _ in range(n)]
        pasos = [{"descripcion": "Matriz A", "matriz": self._mat_str(self.A)},
                 {"descripcion": "Matriz B", "matriz": B._mat_str(B.A)}]

        # Calcular cada elemento y añadir un paso resumido por fila calculada
        for i in range(n):
            for j in range(p):
                s = 0.0
                terminos = []
                for k in range(self.m):
                    a = self.A[i][k]
                    b = B.A[k][j]
                    s += a * b
                    terminos.append(f"({self._format_number(a)})*({self._format_number(b)})")
                result[i][j] = s
            # agregar paso parcial con la fila i calculada
            pasos.append({"descripcion": f"Fila {i+1} calculada: sumar productos elemento-a-elemento -> {' + '.join(terminos)}", "matriz": self._mat_str(result)})

        pasos.append({"descripcion": "Resultado A * B", "matriz": self._mat_str(result)})
        return {"pasos": pasos, "datos": result, "resultado_matriz": Matriz(result), "mensaje": "Multiplicación realizada."}

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

            