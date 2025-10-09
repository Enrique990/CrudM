# matrices.py

from copy import deepcopy

class Matriz:
    def __init__(self, datos):
        # Validaciones básicas
        if not datos or not all(isinstance(row, list) and row for row in datos):
            raise ValueError("Datos de la matriz inválidos: debe ser una lista no vacía de filas (listas).")

        cols = len(datos[0])
        # - Todas las filas, igual cantidad de columnas
        for fila in datos:
            if len(fila) != cols:
                raise ValueError("Todas las filas deben tener la misma cantidad de columnas.")

        # Guardo mi matriz(A), numero de filas y columnas tambn
        
        self.A = [row[:] for row in datos]
        self.n = len(datos)
        self.m = cols
        
        # Me crea el nombre de las variables x1, x2, ..., x(m-1) (útil si la última columna es término independiente)
        self.variables = [f"x{i+1}" for i in range(max(0, self.m - 1))]

    """ Si es un numero entero, asi se muestra. Si tiene decimales, se muestra con 4 decimales"""
    def _format_number(self, x):
        try:
            x = float(x)
        except Exception:
            return str(x)
        if abs(x - int(x)) < 1e-10:
            return str(int(round(x)))
        else:
            return f"{x:.4f}".rstrip('0').rstrip('.')
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

        pasos.append({"descripcion": "Matriz inicial", "matriz": deepcopy(A)})

        for col in range(m - 1):  # la última columna se asume término independiente
            # Buscar pivote (fila con valor absoluto máximo en esta columna desde 'fila' hacia abajo)
            sel = None
            maxval = 0.0
            for r in range(fila, n):
                if abs(A[r][col]) > maxval:
                    maxval = abs(A[r][col])
                    sel = r
            if sel is None or abs(A[sel][col]) < 1e-12:
                continue  # no pivote en esta columna
            # intercambiar filas
            if sel != fila:
                A[fila], A[sel] = A[sel], A[fila]
                pasos.append({"descripcion": f"Intercambiar fila {fila+1} con fila {sel+1}", "matriz": deepcopy(A)})
            # normalizar pivote a 1
            pivot_val = A[fila][col]
            A[fila] = [val / pivot_val for val in A[fila]]
            pasos.append({"descripcion": f"Dividir fila {fila+1} por {pivot_val}", "matriz": deepcopy(A)})
            # eliminar otras filas
            for r in range(n):
                if r != fila and abs(A[r][col]) > 1e-12:
                    factor = A[r][col]
                    A[r] = [A[r][c] - factor * A[fila][c] for c in range(m)]
                    pasos.append({"descripcion": f"Restar {factor} * fila {fila+1} a fila {r+1}", "matriz": deepcopy(A)})
            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        # Detectar inconsistencia (fila 0 ... 0 | b != 0)
        for r in range(n):
            if all(abs(A[r][c]) < 1e-12 for c in range(m - 1)) and abs(A[r][m - 1]) > 1e-12:
                return {"pasos": pasos, "solucion": "Sin solución", "mensaje": "Sistema incompatible, no tiene solución."}

        # Variables libres
        pivot_cols = sorted(pivotes.keys())
        libres = [c for c in range(m - 1) if c not in pivotes]

        # Construir solución
        solucion = {}
        if libres:
            # expresar variables de pivote en función de libres
            for col, row in pivotes.items():
                # valor del término independiente
                val = A[row][m - 1]
                expr_terms = []
                for c in libres:
                    coef = -A[row][c]
                    if abs(coef) > 1e-12:
                        expr_terms.append(f"{self._format_number(coef)}*x{c+1}")
                expr = f"{self._format_number(val)}"
                if expr_terms:
                    expr += " + " + " + ".join(expr_terms)
                solucion[f"x{col+1}"] = expr
            for c in libres:
                solucion[f"x{c+1}"] = f"t{c+1}"  # parámetro libre
            tipo_sol = "Infinitas soluciones (sistema subdeterminado)."
        else:
            # solución única: tomar el valor en cada fila pivote
            for col, row in pivotes.items():
                solucion[f"x{col+1}"] = self._format_number(A[row][m - 1])
            tipo_sol = "Solución única."

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

        solucion = self._resolver_sustitucion(A_after)
        return {"pasos": pasos, "solucion": solucion}

    def _forward_elimination(self, A):
        """Realiza eliminación hacia adelante (como en Gauss), retorna la matriz transformada,
        el dict de pivotes (col -> fila) y la lista de pasos (mismo formato que gauss/gauss_jordan).
        """
        n = len(A)
        m = len(A[0]) if n else 0
        pasos = []
        pivotes = {}
        fila = 0

        pasos.append({"descripcion": "Matriz inicial", "matriz": deepcopy(A)})

        for col in range(min(n, m - 1)):
            # pivot parcial
            sel = None
            maxval = 0.0
            for r in range(fila, n):
                if abs(A[r][col]) > maxval:
                    maxval = abs(A[r][col])
                    sel = r
            if sel is None or abs(A[sel][col]) < 1e-12:
                continue
            if sel != fila:
                A[fila], A[sel] = A[sel], A[fila]
                pasos.append({"descripcion": f"Intercambiar fila {fila+1} con fila {sel+1}", "matriz": deepcopy(A)})
            # eliminar filas debajo
            for r in range(fila+1, n):
                if abs(A[r][col]) > 1e-12:
                    factor = A[r][col] / A[fila][col]
                    A[r] = [A[r][c] - factor * A[fila][c] for c in range(m)]
                    pasos.append({"descripcion": f"Restar {self._format_number(factor)} * fila {fila+1} a fila {r+1}", "matriz": deepcopy(A)})
            pivotes[col] = fila
            fila += 1
            if fila >= n:
                break

        return A, pivotes, pasos

    def independencia(self):
        """Determina si las columnas (coeficientes) son linealmente independientes.
        Reutiliza _forward_elimination para obtener pivotes y pasos.
        """
        # Usar toda la matriz (no tratamos última columna como término independiente aquí)
        A = [list(map(float, row)) for row in deepcopy(self.A)]
        # Si la matriz es n x m, consideramos las m columnas como columnas de vectores
        # (si se quiere excluir una columna independiente, crear la Matriz sin esa columna).
        A_after, pivotes, pasos = self._forward_elimination(A)

        num_cols = self.m
        rango = len(pivotes)
        pivot_cols = sorted(pivotes.keys())
        libres = [c for c in range(num_cols) if c not in pivotes]

        independiente = (rango == num_cols)

        if independiente:
            mensaje = "Las columnas son linealmente independientes (rango = número de columnas)."
        else:
            mensaje = f"Las columnas son linealmente dependientes (rango = {rango} < {num_cols})."

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
            raise ValueError("Para sumar, ambas matrices deben tener las mismas dimensiones.")

        # Resultado inicial con ceros
        result = [[0.0 for _ in range(self.m)] for __ in range(self.n)]
        pasos = []
        # Paso inicial (matrices A y B)
        pasos.append({"descripcion": "Matrices iniciales (A y B)", "matriz": deepcopy(self.A)})
        # Realizar suma elemento a elemento, guardando un paso por cada elemento calculado
        for i in range(self.n):
            for j in range(self.m):
                a = self.A[i][j]
                b = B.A[i][j]
                s = a + b
                result[i][j] = s
                desc = f"Calcular C[{i+1},{j+1}] = A[{i+1},{j+1}] + B[{i+1},{j+1}] = {self._format_number(a)} + {self._format_number(b)} = {self._format_number(s)}"
                pasos.append({"descripcion": desc, "matriz": deepcopy(result)})

        return {"pasos": pasos, "datos": result, "resultado_matriz": Matriz(result), "mensaje": "Suma realizada."}

    def restar(self, other):
        B = self._ensure_matriz_input(other)
        if self.n != B.n or self.m != B.m:
            raise ValueError("Para restar, ambas matrices deben tener las mismas dimensiones.")

        result = [[0.0 for _ in range(self.m)] for __ in range(self.n)]
        pasos = []
        pasos.append({"descripcion": "Matrices iniciales (A y B)", "matriz": deepcopy(self.A)})
        for i in range(self.n):
            for j in range(self.m):
                a = self.A[i][j]
                b = B.A[i][j]
                r = a - b
                result[i][j] = r
                desc = f"Calcular C[{i+1},{j+1}] = A[{i+1},{j+1}] - B[{i+1},{j+1}] = {self._format_number(a)} - {self._format_number(b)} = {self._format_number(r)}"
                pasos.append({"descripcion": desc, "matriz": deepcopy(result)})

        return {"pasos": pasos, "datos": result, "resultado_matriz": Matriz(result), "mensaje": "Resta realizada."}

    def multiplicar(self, other):
        B = self._ensure_matriz_input(other)
        if self.m != B.n:
            raise ValueError("Para multiplicar A*B, columnas de A deben igualar filas de B.")
        result = [[0.0 for _ in range(B.m)] for __ in range(self.n)]
        pasos = []
        pasos.append({"descripcion": f"Matrices iniciales (A {self.n}x{self.m} y B {B.n}x{B.m})", "matriz": deepcopy(self.A)})

        for i in range(self.n):
            for j in range(B.m):
                terms = []
                s = 0.0
                for k in range(self.m):
                    a = self.A[i][k]
                    b = B.A[k][j]
                    prod = a * b
                    terms.append(f"{self._format_number(a)}*{self._format_number(b)}")
                    s += prod
                result[i][j] = s
                expr = " + ".join(terms) if terms else "0"
                desc = f"Calcular C[{i+1},{j+1}] = Σ_k A[{i+1},k]*B[k,{j+1}] = {expr} = {self._format_number(s)}"
                pasos.append({"descripcion": desc, "matriz": deepcopy(result)})

        return {"pasos": pasos, "datos": result, "resultado_matriz": Matriz(result), "mensaje": "Multiplicación realizada."}

    def _resolver_sustitucion(self, A):
        """Asume A en forma escalonada superior (como resultado de forward elimination).
        Devuelve dict de solución, o mensaje string si incompatible.
        """
        n = len(A)
        m = len(A[0]) if n else 0
        pivotes = {}
        # detectar pivotes (col -> fila) en A (col < m-1)
        fila = 0
        for col in range(m - 1):
            found = False
            for r in range(fila, n):
                if abs(A[r][col]) > 1e-12:
                    pivotes[col] = r
                    fila = r + 1
                    found = True
                    break
            if not found:
                continue

        # detectar inconsistencia
        for r in range(n):
            if all(abs(A[r][c]) < 1e-12 for c in range(m - 1)) and abs(A[r][m - 1]) > 1e-12:
                return "Sistema incompatible, no tiene solución."

        libres = [c for c in range(m - 1) if c not in pivotes]
        solucion = {}

        if not libres and len(pivotes) == (m - 1):
            # solución única, back substitution
            x = [0.0] * (m - 1)
            for col in sorted(pivotes.keys(), reverse=True):
                row = pivotes[col]
                s = A[row][m - 1]
                for c in range(col + 1, m - 1):
                    s -= A[row][c] * x[c]
                x[col] = s / A[row][col]
            for i, val in enumerate(x):
                solucion[f"x{i+1}"] = self._format_number(val)
            return solucion
        else:
            # sistema con infinitas soluciones: expresar en función de libres
            for col in sorted(pivotes.keys()):
                row = pivotes[col]
                val = A[row][m - 1]
                expr_terms = []
                for c in libres:
                    coef = -A[row][c] / (A[row][col] if abs(A[row][col])>1e-12 else 1.0)
                    if abs(coef) > 1e-12:
                        expr_terms.append(f"{self._format_number(coef)}*x{c+1}")
                expr = self._format_number(val / (A[row][col] if abs(A[row][col])>1e-12 else 1.0))
                if expr_terms:
                    expr += " + " + " + ".join(expr_terms)
                solucion[f"x{col+1}"] = expr
            for c in libres:
                solucion[f"x{c+1}"] = f"t{c+1}"
            return solucion

