# matrices.py

from copy import deepcopy

class Matriz:
    def __init__(self, datos):
        # Validaciones básicas
        if not datos or not all(isinstance(row, list) and row for row in datos):
            raise ValueError("datos debe ser una lista no vacía de filas (listas)")

        cols = len(datos[0])
        # - Todas las filas, igual cantidad de columnas
        for fila in datos:
            if len(fila) != cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas")

        # Guardo mi matriz(A), numero de filas y columnas tambn
        self.A = [row[:] for row in datos]
        self.n = len(datos)
        self.m = cols

        # Me crea el nombre de las variables x1, x2, ..., x(m-1) (útil si la última columna es término independiente)
        self.variables = [f"x{i+1}" for i in range(max(0, self.m - 1))]

    """ Si es un numero entero, asi se muestra. Si tiene decimales, se muestra con 4 decimales"""
    def _format_number(self, x):
        try:
            xf = float(x)
        except Exception:
            return str(x)
        if abs(xf - int(round(xf))) < 1e-10:
            return str(int(round(xf)))
        else:
            return f"{xf:.4f}".rstrip('0').rstrip('.') if '.' in f"{xf:.4f}" else f"{xf:.4f}"

    # utiliza la funcion de arriba, pero la aplica a toda la matriz
    def _mat_str(self, mat):
        return [[self._format_number(x) for x in row] for row in mat]

    """ -------------------- MÉTODO GAUSS-JORDAN -------------------- """
    def gauss_jordan(self):
        A = [list(map(float, row)) for row in deepcopy(self.A)]
        n, m = self.n, self.m
        pasos = []
        pivotes = {}
        fila = 0
        tol = 1e-12

        pasos.append({"descripcion": "Matriz inicial", "matriz": deepcopy(A)})

        for col in range(m - 1):
            # 1) Preferir un 1 exacto en la columna (desde fila hacia abajo)
            sel = None
            for r in range(fila, n):
                if abs(A[r][col] - 1.0) < tol:
                    sel = r
                    break
            # 2) si no hay 1, seleccionar el mayor absoluto
            if sel is None:
                maxval = 0.0
                for r in range(fila, n):
                    if abs(A[r][col]) > maxval:
                        maxval = abs(A[r][col])
                        sel = r
            if sel is None or abs(A[sel][col]) < tol:
                continue  # no pivote en esta columna

            # intercambiar filas si hace falta
            if sel != fila:
                A[fila], A[sel] = A[sel], A[fila]
                pasos.append({"descripcion": f"F{fila+1} ↔ F{sel+1}", "matriz": deepcopy(A)})

            # normalizar pivote a 1 si no lo está
            pivot_val = A[fila][col]
            if abs(pivot_val - 1.0) > tol:
                formatted_pivot = self._format_number(pivot_val)
                A[fila] = [val / pivot_val for val in A[fila]]
                pasos.append({"descripcion": f"F{fila+1} → F{fila+1} / {formatted_pivot}", "matriz": deepcopy(A)})

            # eliminar todas las demás filas (Gauss-Jordan: arriba y abajo)
            for r in range(n):
                if r != fila and abs(A[r][col]) > tol:
                    factor = A[r][col]
                    formatted_factor = self._format_number(factor)
                    A[r] = [A[r][c] - factor * A[fila][c] for c in range(m)]
                    pasos.append({"descripcion": f"F{r+1} → F{r+1} - {formatted_factor}*F{fila+1}", "matriz": deepcopy(A)})

            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        # Detectar inconsistencia (fila 0 ... 0 | b != 0)
        for r in range(n):
            if all(abs(A[r][c]) < tol for c in range(m - 1)) and abs(A[r][m - 1]) > tol:
                return {"pasos": pasos, "solucion": "Sin solución", "mensaje": "Sistema incompatible, no tiene solución."}

        # Variables libres y construir solución
        pivot_cols = sorted(pivotes.keys())
        libres = [c for c in range(m - 1) if c not in pivotes]

        solucion = {}
        if libres:
            # expresar variables de pivote en función de libres
            for col, row in pivotes.items():
                val = A[row][m - 1]
                expr_terms = []
                for c in libres:
                    coef = -A[row][c]
                    if abs(coef) > tol:
                        expr_terms.append(f"{self._format_number(coef)}*x{c+1}")
                expr = f"{self._format_number(val)}"
                if expr_terms:
                    expr += " + " + " + ".join(expr_terms)
                solucion[f"x{col+1}"] = expr
            for c in libres:
                solucion[f"x{c+1}"] = f"t{c+1}"
            tipo_sol = "Infinitas soluciones (sistema subdeterminado)."
        else:
            for col, row in pivotes.items():
                solucion[f"x{col+1}"] = self._format_number(A[row][m - 1])
            tipo_sol = "Solución única."

        solucion.update({"rango": len(pivotes)})
        return {"pasos": pasos, "solucion": solucion, "mensaje": tipo_sol}

    # -------------------- MÉTODO GAUSS --------------------
    def gauss(self):
        A = [list(map(float, row)) for row in deepcopy(self.A)]
        n, m = self.n, self.m
        pasos = []
        pasos.append({"descripcion": "Matriz inicial", "matriz": deepcopy(A)})

        # Reutilizar el forward elimination privado
        A_after, pivotes, pasos_elim = self._forward_elimination(deepcopy(A))
        pasos.extend(pasos_elim)

        # Detectar inconsistencia
        tol = 1e-12
        for r in range(n):
            if all(abs(A_after[r][c]) < tol for c in range(m - 1)) and abs(A_after[r][m - 1]) > tol:
                return {"pasos": pasos, "solucion": "Sin solución", "mensaje": "Sistema incompatible, no tiene solución."}

        solucion = self._resolver_sustitucion(A_after)
        if isinstance(solucion, dict):
            solucion.update({"rango": len(pivotes)})
        return {"pasos": pasos, "solucion": solucion}

    def _forward_elimination(self, A):
        """Realiza eliminación hacia adelante (como en Gauss), retorna la matriz transformada,
        el dict de pivotes (col -> fila) y la lista de pasos (mismo formato que gauss/gauss_jordan).
        Prioriza traer un 1 como pivote si existe en la columna.
        """
        n = len(A)
        m = len(A[0]) if n else 0
        pasos = []
        pivotes = {}
        fila = 0
        tol = 1e-12

        pasos.append({"descripcion": "Matriz inicial", "matriz": deepcopy(A)})

        for col in range(min(n, m - 1)):
            # buscar 1 en la columna desde fila hacia abajo
            sel = None
            for r in range(fila, n):
                if abs(A[r][col] - 1.0) < tol:
                    sel = r
                    break
            # si no hay 1, elegir mayor absoluto
            if sel is None:
                maxval = 0.0
                for r in range(fila, n):
                    if abs(A[r][col]) > maxval:
                        maxval = abs(A[r][col])
                        sel = r
            if sel is None or abs(A[sel][col]) < tol:
                continue

            if sel != fila:
                A[fila], A[sel] = A[sel], A[fila]
                pasos.append({"descripcion": f"F{fila+1} ↔ F{sel+1}", "matriz": deepcopy(A)})

            # eliminar filas debajo
            for r in range(fila+1, n):
                if abs(A[r][col]) > tol:
                    factor = A[r][col] / A[fila][col]
                    formatted_factor = self._format_number(factor)
                    A[r] = [A[r][c] - factor * A[fila][c] for c in range(m)]
                    pasos.append({"descripcion": f"F{r+1} → F{r+1} - {formatted_factor}*F{fila+1}", "matriz": deepcopy(A)})

            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        return A, pivotes, pasos

    # -------------------- INDEPENDENCIA LINEAL --------------------
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
        if not isinstance(other, Matriz):
            raise ValueError("Entrada debe ser otra Matriz")
        return other

    def sumar(self, other):
        other = self._ensure_matriz_input(other)
        if self.n != other.n or self.m != other.m:
            raise ValueError("Dimensiones incompatibles para suma")
        R = [[self.A[i][j] + other.A[i][j] for j in range(self.m)] for i in range(self.n)]
        pasos = [{"descripcion": "Suma A + B", "matriz": deepcopy(R)}]
        return {"datos": R, "pasos": pasos}

    def restar(self, other):
        other = self._ensure_matriz_input(other)
        if self.n != other.n or self.m != other.m:
            raise ValueError("Dimensiones incompatibles para resta")
        R = [[self.A[i][j] - other.A[i][j] for j in range(self.m)] for i in range(self.n)]
        pasos = [{"descripcion": "Resta A - B", "matriz": deepcopy(R)}]
        return {"datos": R, "pasos": pasos}

    def multiplicar(self, other):
        other = self._ensure_matriz_input(other)
        if self.m != other.n:
            raise ValueError("Dimensiones incompatibles para multiplicación")
        R = [[sum(self.A[i][k] * other.A[k][j] for k in range(self.m)) for j in range(other.m)] for i in range(self.n)]
        pasos = [{"descripcion": "Multiplicación A * B", "matriz": deepcopy(R)}]
        return {"datos": R, "pasos": pasos}

    def _resolver_sustitucion(self, A):
        """Back substitution para matriz aumentada triangular superior A (n x m, m = vars+1)."""
        n = len(A)
        m = len(A[0]) if n else 0
        vars_n = m - 1
        tol = 1e-12
        x = [0.0] * vars_n
        # buscar pivotes (suponer rol de columnas de 0..vars_n-1)
        # asumimos fila i corresponde a variable i en solución si hay pivote en diagonal; si no, se deja como libre
        for i in range(vars_n-1, -1, -1):
            # encontrar fila que tiene pivote en columna i (desde top)
            pivot_row = None
            for r in range(n):
                if abs(A[r][i]) > tol:
                    pivot_row = r
                    break
            if pivot_row is None:
                # variable libre -> 0 por defecto aquí (caller puede tratar libres)
                x[i] = 0.0
                continue
            s = A[pivot_row][m-1]
            for c in range(i+1, vars_n):
                s -= A[pivot_row][c] * x[c]
            x[i] = s / A[pivot_row][i] if abs(A[pivot_row][i]) > tol else 0.0
        # formatear solución
        sol = {f"x{i+1}": self._format_number(x[i]) for i in range(vars_n)}
        return sol

def parse_vectors_text(text):
    """Parsea texto con un vector por línea; componentes separadas por espacio o comma.
    Devuelve lista de vectores (listas de float).
    Lanza ValueError si hay formato inválido o dimensiones inconsistentes.
    """
    if text is None:
        raise ValueError("Texto vacío")

    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    vectors = []
    for ln in lines:
        parts = [p for p in (ln.replace(',', ' ').split()) if p]
        if not parts:
            continue
        try:
            vec = [float(p) for p in parts]
        except Exception:
            raise ValueError(f"Formato inválido en línea: '{ln}'")
        vectors.append(vec)

    if not vectors:
        raise ValueError("No se encontraron vectores en la entrada")

    dim = len(vectors[0])
    if any(len(v) != dim for v in vectors):
        raise ValueError("Vectores con dimensiones inconsistentes")

    return vectors

def analyze_vectors(vectors):
    """Analiza independencia lineal de una lista de vectores (cada vector es lista de números).
    Interpreta los vectores como columnas y usa Matriz.independencia().
    Devuelve dict con claves: rank (int), independent (bool), relation (None por ahora), pasos, mensaje.
    """
    if not vectors:
        raise ValueError("No hay vectores para analizar")

    # construir matriz con vectores como columnas: filas = dimensión, columnas = nº vectores
    try:
        Mmat = vectors_to_column_matrix(vectors)
        M = Matriz(Mmat)
    except Exception as e:
        raise

    res = M.independencia()
    sol = res.get("solucion", {}) if isinstance(res, dict) else {}
    rank = sol.get("rango", None) if isinstance(sol, dict) else None
    independent = sol.get("independiente", None) if isinstance(sol, dict) else None
    return {
        "rank": rank,
        "independent": independent,
        "relation": None,
        "pasos": res.get("pasos"),
        "mensaje": res.get("mensaje")
    }

def vectors_to_row_matrix(vectors):
    """Devuelve lista de filas donde cada vector es una fila."""
    return [list(v) for v in vectors]

def vectors_to_column_matrix(vectors):
    """Devuelve la matriz (lista de filas) en la que cada vector es una columna (transpuesta)."""
    if not vectors:
        return []
    return [list(row) for row in zip(*vectors)]

