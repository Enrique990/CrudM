# matrices.py

import re

def parse_vectors_text(text):
    """Parsea texto con un vector por línea (componentes separados por espacios o comas)."""
    if not text or not text.strip():
        raise ValueError("Entrada vacía")
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    vectors = []
    for ln in lines:
        parts = [p for p in re.split(r'[,\s]+', ln.strip()) if p != ""]
        vec = [float(p) for p in parts]
        vectors.append(vec)
    if not vectors:
        raise ValueError("No se encontraron vectores.")
    dim = len(vectors[0])
    for v in vectors:
        if len(v) != dim:
            raise ValueError("Todos los vectores deben tener la misma cantidad de componentes.")
    return vectors

def vectors_to_row_matrix(vectors):
    """Cada vector como fila."""
    return [v[:] for v in vectors]

def vectors_to_column_matrix(vectors):
    """Construye matriz con vectores como columnas (m x n)."""
    n = len(vectors)
    m = len(vectors[0]) if n else 0
    return [[vectors[j][i] for j in range(n)] for i in range(m)]

def _rref(M, eps=1e-12):
    """Reduce M a RREF. Devuelve (R, pivots)."""
    A = [row[:] for row in M]
    rows = len(A)
    cols = len(A[0]) if rows else 0
    r = 0
    pivots = []
    for c in range(cols):
        # buscar fila con mayor valor absoluto en columna c desde r
        sel = None
        maxv = 0.0
        for i in range(r, rows):
            val = abs(A[i][c])
            if val > maxv:
                maxv = val
                sel = i
        if sel is None or maxv <= eps:
            continue
        A[r], A[sel] = A[sel], A[r]
        pivot = A[r][c]
        A[r] = [val / pivot for val in A[r]]
        for i in range(rows):
            if i != r:
                factor = A[i][c]
                if abs(factor) > eps:
                    A[i] = [A[i][j] - factor * A[r][j] for j in range(cols)]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    # limpieza numérica
    for i in range(rows):
        for j in range(cols):
            if abs(A[i][j]) < eps:
                A[i][j] = 0.0
    return A, pivots

def matrix_rank(M):
    """Devuelve el rango de la matriz M (lista de listas)."""
    _, piv = _rref(M)
    return len(piv)

def nullspace_basis(M, eps=1e-12):
    """
    Calcula una base del núcleo de M (M * x = 0).
    Retorna lista de vectores (cada uno longitud n). Si no hay variables libres retorna [].
    """
    if not M:
        return []
    R, pivots = _rref(M, eps)
    rows = len(R)
    cols = len(R[0]) if rows else 0
    piv_set = set(pivots)
    free_cols = [c for c in range(cols) if c not in piv_set]
    basis = []
    if not free_cols:
        return basis
    # Para cada variable libre construimos vector del núcleo
    for free in free_cols:
        vec = [0.0] * cols
        vec[free] = 1.0
        for row_i, pivot_col in enumerate(pivots):
            # en RREF, R[row_i][pivot_col] = 1, y R[row_i][free] es el coef para la libre
            val = -R[row_i][free] if free < len(R[row_i]) else 0.0
            vec[pivot_col] = val
        basis.append(vec)
    return basis

def analyze_vectors(vectors):
    """
    Analiza lista de vectores (cada vector es lista de floats).
    Retorna dict con A_columns, rank, independent, nullspace y relation (primer vector no trivial del núcleo).
    """
    if not vectors:
        raise ValueError("Lista de vectores vacía")
    A_cols = vectors_to_column_matrix(vectors)
    rank = matrix_rank(A_cols)
    n = len(vectors)
    independent = (rank == n)
    ns = nullspace_basis(A_cols)
    relation = ns[0] if (not independent and ns) else None
    return {
        "vectors": vectors,
        "A_columns": A_cols,
        "m": len(A_cols),
        "n": n,
        "rank": rank,
        "independent": independent,
        "nullspace": ns,
        "relation": relation
    }

