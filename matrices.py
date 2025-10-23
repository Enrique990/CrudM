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
        pasos = []
        # (Evitar duplicar "Matriz inicial": lo agrega _forward_elimination)
        # Reutilizar el forward elimination privado
        A, pivotes, pasos_elim = self._forward_elimination(A)
        pasos.extend(pasos_elim)

        sol = self._resolver_sustitucion(A)
        # Mensaje coherente con Gauss-Jordan
        if isinstance(sol, str):
            mensaje = "El sistema es inconsistente (no tiene solución)."
        else:
            if any(v == "libre" for v in sol.values()):
                mensaje = "El sistema tiene infinitas soluciones (variables libres presentes)."
            else:
                mensaje = "El sistema tiene solución única."
        return {"pasos": pasos, "solucion": sol, "mensaje": mensaje}

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

    def independencia_vectores(self, vectores, mostrar_pasos=True):
        """Comprueba la independencia lineal de una lista de vectores.

        - vectores: lista de listas, cada lista es un vector de misma dimensión (longitud n).
        - mostrar_pasos: si True se devuelven los pasos de eliminación (en formato consistente con
          los otros métodos). Si False, la clave "pasos" será una lista vacía.

        Retorna un dict con las mismas claves que `independencia`: {"pasos", "solucion", "mensaje"}.
        """
        # Validaciones básicas
        if vectores is None:
            raise ValueError("Se requiere una lista de vectores.")

        k = len(vectores)
        if k == 0:
            return {"pasos": [] if not mostrar_pasos else [],
                    "solucion": {"independiente": True, "rango": 0, "pivotes": [], "libres": []},
                    "mensaje": "No hay vectores: por convención el conjunto vacío es independiente."}

        n = len(vectores[0])
        for v in vectores:
            if len(v) != n:
                raise ValueError("Todos los vectores deben tener la misma dimensión")

        # Construir la matriz cuyo número de columnas = número de vectores
        A = [[vectores[c][r] for c in range(k)] for r in range(n)]

        pasos = []
        pivotes = {}
        libres = set()
        fila = 0

        pasos.append({"descripcion": "Matriz (vectores como columnas) - matriz inicial", "matriz": self._mat_str(A)})

        for col in range(k):
            pivot_row = None
            for r in range(fila, n):
                if abs(A[r][col]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                libres.add(col)
                pasos.append({"descripcion": f"v{col+1}: columna sin pivote (libre)", "matriz": self._mat_str(A)})
                continue

            if pivot_row != fila:
                A[fila], A[pivot_row] = A[pivot_row], A[fila]
                valor_pivote = self._format_number(A[fila][col])
                pasos.append({"descripcion": f"(*Pivote*, Fila: {fila+1}; Columna: {col+1}; Valor: {valor_pivote})\nF{fila+1} ↔ F{pivot_row+1}", "matriz": self._mat_str(A)})

            pivot = A[fila][col]
            if abs(pivot - 1) > 1e-10:
                A[fila] = [x / pivot for x in A[fila]]
                valor_pivote = self._format_number(pivot)
                pasos.append({"descripcion": f"(*Pivote*, Fila: {fila+1}; Columna: {col+1}; Valor: {valor_pivote})\nF{fila+1} → F{fila+1} / {valor_pivote}", "matriz": self._mat_str(A)})

            for r in range(n):
                if r != fila and abs(A[r][col]) > 1e-10:
                    factor = A[r][col]
                    A[r] = [A[r][c] - factor * A[fila][c] for c in range(k)]
                    valor_pivote = self._format_number(A[fila][col])
                    pasos.append({"descripcion": f"(*Pivote*, Fila: {fila+1}; Columna: {col+1}; Valor: {valor_pivote})\nF{r+1} → F{r+1} - ({self._format_number(factor)})*F{fila+1}", "matriz": self._mat_str(A)})

            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        pivot_cols = sorted(pivotes.keys())
        libres = [c for c in range(k) if c not in pivotes]
        rango = len(pivotes)
        independiente = (rango == k)

        if independiente:
            mensaje = f"Linealmente independientes "
        else:
            libres_nombres = ", ".join(f"v{c+1}" for c in libres) if libres else "ninguna"
            mensaje = (f"Linealmente dependientes. "
                       f"Columnas sin pivote (libres): {libres_nombres}.")

        solucion = {
            "independiente": independiente,
            "rango": rango,
            "pivotes": [c + 1 for c in pivot_cols],
            "libres": [c + 1 for c in libres]
        }

        return {"pasos": pasos if mostrar_pasos else [], "solucion": solucion, "mensaje": mensaje}

    def trasponer(self):
        """Devuelve una nueva instancia de Matriz que es la traspuesta de la actual.
        No modifica la matriz original.
        """
        # Construir la traspuesta: filas -> columnas
        trans = [[self.A[r][c] for r in range(self.n)] for c in range(self.m)]
        return Matriz(trans)

    # alias en inglés por conveniencia
    transpose = trasponer

    def inversa(self, mostrar_pasos=True):
        """Calcula la inversa de la matriz usando Gauss-Jordan sobre [A | I].

        - Validaciones: la matriz debe ser cuadrada (n == m).
        - Si la matriz es singular devuelve {'pasos': pasos, 'inversa': None, 'mensaje': ...}.
        - Si tiene inversa devuelve la matriz inversa formateada y los pasos (si mostrar_pasos).
        """
        # Solo para matrices cuadradas
        if self.n != self.m:
            raise ValueError("La inversa sólo está definida para matrices cuadradas (n == m).")

        n = self.n
        # Construir la matriz aumentada [A | I]
        A = [row[:] for row in self.A]
        Aug = [A[i] + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        pasos = []
        pasos.append({"descripcion": "Matriz inicial (A | I)", "matriz": self._mat_str(Aug)})

        fila = 0
        for col in range(n):
            pivot_row = None
            for r in range(fila, n):
                if abs(Aug[r][col]) > 1e-10:
                    pivot_row = r
                    break
            if pivot_row is None:
                # No hay pivote en esta columna -> singular
                return {"pasos": pasos, "inversa": None, "mensaje": "La matriz es singular y no tiene inversa."}

            if pivot_row != fila:
                Aug[fila], Aug[pivot_row] = Aug[pivot_row], Aug[fila]
                pasos.append({"descripcion": f"F{fila+1} ↔ F{pivot_row+1}", "matriz": self._mat_str(Aug)})

            pivot = Aug[fila][col]
            if abs(pivot - 1) > 1e-10:
                Aug[fila] = [x / pivot for x in Aug[fila]]
                pasos.append({"descripcion": f"F{fila+1} → F{fila+1} / {self._format_number(pivot)}", "matriz": self._mat_str(Aug)})

            for r in range(n):
                if r != fila and abs(Aug[r][col]) > 1e-10:
                    factor = Aug[r][col]
                    Aug[r] = [Aug[r][k] - factor * Aug[fila][k] for k in range(2 * n)]
                    pasos.append({"descripcion": f"F{r+1} → F{r+1} - ({self._format_number(factor)})*F{fila+1}", "matriz": self._mat_str(Aug)})

            fila += 1

        # Extraer la inversa (la mitad derecha de la matriz aumentada)
        inv = [row[n:] for row in Aug]

        return {"pasos": pasos if mostrar_pasos else [], "inversa": self._mat_str(inv), "mensaje": "Inversa calculada correctamente."}

    # alias en inglés
    inverse = inversa

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

    # -------------------- OPERADOR DE MATRICES --------------------
    def _ensure_matrix_like(self, other):
        if isinstance(other, Matriz):
            return other
        if isinstance(other, (list, tuple)):
            return Matriz([list(row) for row in other])
        raise ValueError("El operando debe ser una Matriz o una lista de listas numéricas.")

    def sumar(self, other):
        B = self._ensure_matrix_like(other)
        if self.n != B.n or self.m != B.m:
            raise ValueError("Dimensiones incompatibles para suma: deben ser iguales.")
        C = [[self.A[i][j] + B.A[i][j] for j in range(self.m)] for i in range(self.n)]
        return Matriz(C)

    def restar(self, other):
        B = self._ensure_matrix_like(other)
        if self.n != B.n or self.m != B.m:
            raise ValueError("Dimensiones incompatibles para resta: deben ser iguales.")
        C = [[self.A[i][j] - B.A[i][j] for j in range(self.m)] for i in range(self.n)]
        return Matriz(C)

    def multiplicar(self, other):
        # Escalar
        if isinstance(other, (int, float)):
            C = [[self.A[i][j] * other for j in range(self.m)] for i in range(self.n)]
            return Matriz(C)
        B = self._ensure_matrix_like(other)
        if self.m != B.n:
            raise ValueError(f"Dimensiones incompatibles para multiplicación: {self.n}x{self.m} * {B.n}x{B.m}")
        C = [[0.0 for _ in range(B.m)] for __ in range(self.n)]
        for i in range(self.n):
            for j in range(B.m):
                s = 0.0
                for k in range(self.m):
                    s += self.A[i][k] * B.A[k][j]
                C[i][j] = s
        return Matriz(C)

    # Sobrecargas convenientes
    # Sirve para usar los operadores +, -, @, * directamente
    
    def __add__(self, other):
        return self.sumar(other)

    def __sub__(self, other):
        return self.restar(other)

    def __matmul__(self, other):
        return self.multiplicar(other)

    def __mul__(self, other):
        return self.multiplicar(other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.multiplicar(other)
        return NotImplemented

    def to_list(self):
        return [row[:] for row in self.A]

def determinante_por_gauss(A):
    """
    Calcula el determinante de una matriz cuadrada A (lista de listas)
    mediante reducción a triangular superior por eliminación de Gauss.
    No modifica A (trabaja sobre una copia). Devuelve un número (float).
    """
    eps = 1e-12
    if A is None or len(A) == 0:
        raise ValueError("La matriz no puede estar vacía.")
    n = len(A)
    # verificar cuadrada
    for row in A:
        if len(row) != n:
            raise ValueError("La matriz debe ser cuadrada para calcular el determinante.")
    # trabajar sobre una copia en coma flotante para no alterar la original
    M = [list(map(float, row[:])) for row in A]
    det_sign = 1  # guarda el signo que cambia cuando se intercambian filas
    for i in range(n):
        # Buscar la fila con el mayor valor absoluto en la columna i (pivote)
        max_row = max(range(i, n), key=lambda r: abs(M[r][i]))
        # Si el mejor pivote es (prácticamente) cero, el determinante es 0
        if abs(M[max_row][i]) < eps:
            return 0.0
        # Si hay intercambio de filas, invertimos el signo del determinante
        if max_row != i:
            M[i], M[max_row] = M[max_row], M[i]
            det_sign *= -1
        pivot = M[i][i]
        # Eliminar (poner a cero) los elementos debajo del pivote
        for r in range(i + 1, n):
            if abs(M[r][i]) < eps:
                continue
            factor = M[r][i] / pivot
            # Restamos factor * fila_pivote a la fila r (no cambia el determinante)
            for c in range(i, n):
                M[r][c] -= factor * M[i][c]
    # El determinante es el producto de la diagonal por el signo de los swaps
    det = det_sign
    for i in range(n):
        det *= M[i][i]
    return det


def cramer(A, b):
    """
    Resuelve el sistema A x = b usando la regla de Cramer.
    - A: matriz de coeficientes (lista de listas) cuadrada n x n
    - b: vector de resultados (lista de longitud n)
    Devuelve la lista [x1, x2, ..., xn].
    Lanza ValueError si no hay solución única (determinante cero) o si dimensiones no coinciden.
    """
    eps = 1e-12
    if A is None or b is None:
        raise ValueError("A y b son requeridos.")
    n = len(A)
    if n == 0:
        return []
    for row in A:
        if len(row) != n:
            raise ValueError("La matriz A debe ser cuadrada.")
    if len(b) != n:
        raise ValueError("El vector b debe tener la misma dimensión que A.")
    # Determinante de la matriz de coeficientes
    detA = determinante_por_gauss(A)
    if abs(detA) < eps:
        # Si es cero, no hay solución única y la regla de Cramer no aplica
        raise ValueError("Determinante de A es cero: no existe solución única (regla de Cramer no aplicable).")
    solucion = []
    # Para cada variable reemplazamos la columna correspondiente por b y calculamos su determinante
    for col in range(n):
        Ai = [row[:] for row in A]  # copia de A
        for i in range(n):
            Ai[i][col] = b[i]  # sustituir la columna col por b
        detAi = determinante_por_gauss(Ai)
        solucion.append(detAi / detA)  # xi = det(Ai) / det(A)
    return solucion
