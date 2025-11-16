"""Combina una implementación Fraction-aware del método de bisección con
una capa de compatibilidad orientada a GUI.

Este archivo expone funciones top-level `find_bracketing_interval` y
`bisection` (implementaciones que usan Fraction para mayor exactitud),
y la clase `MetodoBiseccion` al final del archivo como wrapper amigable
para las interfaces (parse_expression, plot_data, biseccion_dict, ...).
"""


"""Implementación Fraction-aware del método de bisección.

Reemplaza la versión previa basada en sympy/numpy/pandas. Esta implementación
acepta `f` como callable o como expresión en cadena y usa `fractions.Fraction`
internamente para preservar exactitud en constantes.
"""
from typing import Any, Dict, List
import math
import ast
from fractions import Fraction
import re
import sympy as sp
import numpy as np


class _NumToFraction(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant):
        # convert only float literals to Fraction; keep ints as int so operations like x**3 keep integer exponent
        if isinstance(node.value, float):
            return ast.copy_location(
                ast.Call(func=ast.Name(id='Fraction', ctx=ast.Load()), args=[ast.Constant(value=str(node.value))], keywords=[]),
                node,
            )
        return node

    def visit_Num(self, node: ast.Num):
        # Num is legacy for older Python AST; only convert floats
        if isinstance(node.n, float):
            return ast.copy_location(
                ast.Call(func=ast.Name(id='Fraction', ctx=ast.Load()), args=[ast.Constant(value=str(node.n))], keywords=[]),
                node,
            )
        return node


def _to_callable(f: Any):
    if callable(f):
        def wrapper(x):
            res = f(x)
            if isinstance(res, Fraction):
                return res
            try:
                return Fraction(str(res))
            except Exception:
                return Fraction(res)
        return wrapper

    if isinstance(f, str):
        expr = f.strip()
        # normalize common user syntax:
        # caret for power, brackets to parentheses, spanish 'sen' -> 'sin', ln -> log
        expr = expr.replace('^', '**')
        # convert brackets and braces to parentheses so users can write [..] or {..}
        expr = expr.replace('[', '(').replace(']', ')')
        expr = expr.replace('{', '(').replace('}', ')')
        expr = re.sub(r"\bsen\s*\(", 'sin(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bln\s*\(", 'log(', expr, flags=re.IGNORECASE)
        # trig aliases: tg -> tan, arcsen/arctg -> asin/atan
        expr = re.sub(r"\btg\s*\(", 'tan(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\barcsen\s*\(", 'asin(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\barctg\s*\(", 'atan(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\barctan\s*\(", 'atan(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\barccos\s*\(", 'acos(', expr, flags=re.IGNORECASE)
        # reciprocal trig functions: cot(x) -> 1/tan(x), sec(x) -> 1/cos(x), csc(x) -> 1/sin(x)
        expr = re.sub(r"\bcot\s*\(", '1/tan(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bsec\s*\(", '1/cos(', expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bcsc\s*\(", '1/sin(', expr, flags=re.IGNORECASE)
        try:
            tree = ast.parse(expr, mode='eval')
            tree = _NumToFraction().visit(tree)
            ast.fix_missing_locations(tree)
            code = compile(tree, '<string>', 'eval')
        except Exception as e:
            raise ValueError(f"Error parseando la expresión '{expr}': {e}")

        ns = {'Fraction': Fraction}
        # expose math functions as wrappers that return Fraction
        for name in dir(math):
            if name.startswith('_'):
                continue
            attr = getattr(math, name)
            if callable(attr):
                def _make_wrapper(fn):
                    return lambda x, fn=fn: Fraction(str(fn(float(x))))
                ns[name] = _make_wrapper(attr)

        # add common constants as Fraction approximations
        ns['pi'] = Fraction(str(math.pi))
        ns['e'] = Fraction(str(math.e))

        # also provide some common aliases (if user writes sen/tg etc.)
        ns['sin'] = ns.get('sin')
        ns['cos'] = ns.get('cos')
        ns['tan'] = ns.get('tan')
        ns['asin'] = ns.get('asin')
        ns['acos'] = ns.get('acos')
        ns['atan'] = ns.get('atan')

        def _fun(x):
            try:
                return Fraction(str(eval(code, {"__builtins__": {}}, {**ns, 'x': x})))
            except Exception as e:
                raise ValueError(f"Error evaluando la expresión '{expr}' en x={x}: {e}")
        return _fun

    raise ValueError("f debe ser una función o una expresión en cadena válida.")


def _format_number(x: Any) -> str:
    if isinstance(x, Fraction):
        return str(x)
    try:
        if abs(x - int(x)) < 1e-12:
            return str(int(round(x)))
    except Exception:
        pass
    try:
        return f"{float(x):.10f}".rstrip('0').rstrip('.')
    except Exception:
        return str(x)


def find_bracketing_interval(f: Any, x0: float = 0.0, step: float = 1.0, max_steps: int = 50, samples: int = 50) -> Dict[str, Any]:
    """Expandir alrededor de x0 y muestrear puntos internos para buscar cambio de signo.

    Este enfoque es más robusto para funciones con dominios restringidos
    (ej: ln) donde los extremos del intervalo pueden ser inválidos, pero
    existe un cambio de signo entre puntos interiores (ej: entre 1 y 2).
    """
    fun = _to_callable(f)
    pasos: List[Dict[str, Any]] = []

    a = Fraction(x0)
    b = Fraction(x0) + Fraction(step)
    current_step = Fraction(step)

    # First try a set of heuristic ranges (positive-first) which helps functions
    # like ln(x) that are undefined at/near zero.
    candidate_ranges = [
        (Fraction('0.1'), Fraction(1)),
        (Fraction(1), Fraction(2)),
        (Fraction(2), Fraction(5)),
        (Fraction(5), Fraction(10)),
        (Fraction(-1), Fraction(1)),
        (Fraction(-10), Fraction(10)),
    ]

    for low, high in candidate_ranges:
        finite_points = []
        err_records = []
        for j in range(samples):
            if samples == 1:
                xj = low
            else:
                xj = low + (high - low) * Fraction(j, samples - 1)
            try:
                yj = fun(xj)
                finite_points.append((xj, yj))
            except Exception as e:
                err_records.append((xj, str(e)))
        # check adjacent finite points
        for k in range(len(finite_points) - 1):
            x1, y1 = finite_points[k]
            x2, y2 = finite_points[k + 1]
            try:
                if y1 * y2 < 0:
                    pasos.append({"iter": 0, "a": _format_number(low), "b": _format_number(high), "fa": _format_number(finite_points[0][1]) if finite_points else '', "fb": _format_number(finite_points[-1][1]) if finite_points else ''})
                    return {"interval": (x1, x2), "pasos": pasos, "mensaje": "Intervalo con cambio de signo encontrado (heurístico)."}
            except Exception:
                continue

    for i in range(max_steps):
        # build samples inside [a,b]
        finite_points: List[tuple] = []  # list of (x, y) for successfully evaluated samples
        err_records: List[tuple] = []
        for j in range(samples):
            # x_j = a + (b-a) * j/(samples-1)
            if samples == 1:
                xj = a
            else:
                xj = a + (b - a) * Fraction(j, samples - 1)
            try:
                yj = fun(xj)
                finite_points.append((xj, yj))
            except Exception as e:
                err_records.append((xj, str(e)))

        # record a summary paso: show endpoints and first few errors if any
        paso = {"iter": i + 1, "a": _format_number(a), "b": _format_number(b)}
        if finite_points:
            paso["fa"] = _format_number(finite_points[0][1])
            paso["fb"] = _format_number(finite_points[-1][1])
        else:
            paso["fa"] = f"ERR:{err_records[0][1]}" if err_records else "ERR:eval"
            paso["fb"] = f"ERR:{err_records[-1][1]}" if err_records else "ERR:eval"
        pasos.append(paso)

        # check for exact zero among finite points
        for xj, yj in finite_points:
            if yj == 0:
                return {"interval": (xj, xj), "pasos": pasos, "mensaje": f"Se encontró raíz exacta en x={_format_number(xj)}"}

        # check adjacent finite sample pairs for sign change
        for k in range(len(finite_points) - 1):
            x1, y1 = finite_points[k]
            x2, y2 = finite_points[k + 1]
            try:
                if y1 * y2 < 0:
                    return {"interval": (x1, x2), "pasos": pasos, "mensaje": "Intervalo con cambio de signo encontrado."}
            except Exception:
                # skip problematic multiplications
                continue

        # expand and try again
        a -= current_step
        b += current_step
        current_step *= 2

    return {"interval": None, "pasos": pasos, "mensaje": "No se encontró un intervalo con cambio de signo en las expansiones dadas."}


def bisection(f: Any, a: Any, b: Any, tol: float = 1e-10, max_iter: int = 100, mostrar_pasos: bool = True) -> Dict[str, Any]:
    fun = _to_callable(f)
    pasos: List[Dict[str, Any]] = []

    a = Fraction(a)
    b = Fraction(b)
    tol_frac = Fraction(str(tol)) if not isinstance(tol, Fraction) else tol

    try:
        fa = fun(a)
        fb = fun(b)
    except Exception as e:
        return {"pasos": pasos, "solucion": None, "mensaje": f"Error evaluando f en los extremos: {e}"}

    if fa == 0:
        return {"pasos": pasos, "solucion": {"root": _format_number(a), "f_root": _format_number(fa), "iteraciones": 0, "abs_error": 0.0}, "mensaje": "f(a) es 0: a es raíz."}
    if fb == 0:
        return {"pasos": pasos, "solucion": {"root": _format_number(b), "f_root": _format_number(fb), "iteraciones": 0, "abs_error": 0.0}, "mensaje": "f(b) es 0: b es raíz."}

    if fa * fb > 0:
        return {"pasos": pasos, "solucion": None, "mensaje": "Los extremos no encierran una raíz (f(a)*f(b) > 0). Usa find_bracketing_interval para encontrar un intervalo válido."}

    c = (a + b) / 2
    fc = fun(c)

    for i in range(1, max_iter + 1):
        error_est = abs(b - a) / 2
        paso = {
            "iter": i,
            "a": _format_number(a),
            "b": _format_number(b),
            "fa": _format_number(fa),
            "fb": _format_number(fb),
            "c": _format_number(c),
            "fc": _format_number(fc),
            "error": _format_number(error_est),
        }
        pasos.append(paso)

        if fc == 0 or error_est <= tol_frac:
            solucion = {"root": _format_number(c), "f_root": _format_number(fc), "iteraciones": i, "abs_error": float(error_est)}
            return {"pasos": pasos if mostrar_pasos else [], "solucion": solucion, "mensaje": "Convergencia alcanzada."}

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

        c = (a + b) / 2
        try:
            fc = fun(c)
        except Exception as e:
            return {"pasos": pasos, "solucion": None, "mensaje": f"Error evaluando f durante iteraciones: {e}"}

    # Si no convergió por tolerancia, reportar la cota de error por intervalo (b-a)/2
    final_error_est = abs(b - a) / 2
    solucion = {"root": _format_number(c), "f_root": _format_number(fc), "iteraciones": max_iter, "abs_error": float(final_error_est)}
    return {"pasos": pasos if mostrar_pasos else [], "solucion": solucion, "mensaje": "No convergió en el número máximo de iteraciones."}


__all__ = ["find_bracketing_interval", "bisection"]


class MetodoBiseccion:
    """Compat wrapper que expone la API esperada por try1.py.

    Métodos:
    - parse_tolerance(tol_str): convierte cadenas flexibles a float
    - find_sign_change_interval(expr_str, ranges=None, samples=400): intenta encontrar intervalo
    - biseccion(expr_or_callable, a, b, tol): ejecuta bisección y devuelve (rows, raiz, error)
    """
    def __init__(self, max_iter: int = 100):
        self.max_iter = max_iter

    def parse_expression(self, expr_str: str):
        """Parsea una expresión en cadena y devuelve (sympy_expr, numpy_callable).

        Útil para la interfaz de graficado que espera un callable vectorizable.
        """
        txt = expr_str.replace('^', '**')
        x = sp.Symbol('x')
        try:
            sym_f = sp.sympify(txt)
        except Exception as e:
            raise ValueError(f"Expresión inválida: {e}")
        try:
            f_num = sp.lambdify(x, sym_f, modules=['numpy'])
        except Exception as e:
            raise ValueError(f"No se pudo crear función numérica: {e}")
        return sym_f, f_num

    def plot_data(self, expr_or_callable, a: float, b: float, n: int = 400):
        """Devuelve (xs, ys) para graficar la función en [a,b].

        - Si `expr_or_callable` es cadena, se parsea con `parse_expression`.
        - Crea arrays numpy y sustituye evaluaciones inválidas por np.nan.
        """
        if isinstance(expr_or_callable, str):
            _, f = self.parse_expression(expr_or_callable)
        elif callable(expr_or_callable):
            f = expr_or_callable
        else:
            raise ValueError('expr_or_callable debe ser cadena o callable')

        xs = np.linspace(a, b, n)
        ys = np.empty_like(xs, dtype=float)
        for i, xv in enumerate(xs):
            try:
                yv = f(xv)
                # ensure scalar float
                ys[i] = float(yv)
            except Exception:
                ys[i] = np.nan
        return xs, ys

    @staticmethod
    def parse_tolerance(tol_str: str) -> float:
        s = tol_str.strip().lower().replace('×', 'x')
        if 'e' in s and not s.startswith('10'):
            return float(s)
        if '10^' in s:
            base, exp = s.split('10^', 1)
            return float(base or 1) * 10 ** float(exp)
        if '10-' in s:
            base, exp = s.split('10-', 1)
            return float(base or 1) * 10 ** (-float(exp))
        if 'x10^' in s:
            base, exp = s.split('x10^', 1)
            return float(base or 1) * 10 ** float(exp)
        return float(s)

    def find_sign_change_interval(self, expr_str: str, ranges=None, samples: int = 400):
        # Implementación simple sin numpy: muestrea en los rangos buscando cambio de signo
        if ranges is None:
            ranges = [(-1, 1), (-10, 10), (-100, 100), (-1000, 1000)]
        fun = _to_callable(expr_str)
        for low, high in ranges:
            step = (high - low) / max(1, samples - 1)
            xs = [low + i * step for i in range(samples)]
            try:
                ys = [float(fun(Fraction(x))) for x in xs]
            except Exception:
                continue
            for i in range(len(xs) - 1):
                yi, yj = ys[i], ys[i + 1]
                if yi == 0:
                    return float(xs[i]), float(xs[i])
                if yi * yj < 0:
                    return float(xs[i]), float(xs[i + 1])
        return None

    def biseccion(self, expr_or_callable, a: float, b: float, tol: float):
        # Implementación compatible que usa Fraction internamente pero devuelve floats
        if isinstance(expr_or_callable, str):
            fun = _to_callable(expr_or_callable)
        elif callable(expr_or_callable):
            fun = _to_callable(expr_or_callable)
        else:
            raise ValueError("expr_or_callable debe ser una cadena o una función callable")

        a_f = Fraction(a)
        b_f = Fraction(b)
        try:
            fa = fun(a_f)
            fb = fun(b_f)
        except Exception as e:
            raise ValueError(f"Error evaluando extremos: {e}")
        if fa * fb > 0:
            raise ValueError("f(a) y f(b) deben tener signos opuestos")

        rows = []
        for i in range(self.max_iter):
            c = (a_f + b_f) / 2
            fc = fun(c)
            prod = float(fa * fc)
            rows.append({'Iteración': i, 'a': float(a_f), 'b': float(b_f), 'c': float(c), 'f(a)': float(fa), 'f(b)': float(fb), 'f(c)': float(fc), 'f(a)*f(c)': prod})
            if abs(float(fc)) < tol or abs(float(b_f - a_f)) / 2.0 < tol:
                break
            if fa * fc < 0:
                b_f = c
                fb = fc
            else:
                a_f = c
                fa = fc

        raiz = float((a_f + b_f) / 2)
        # En compat, devolver como error la cota de bisección: (b-a)/2
        error = abs(float(b_f - a_f)) / 2.0
        return rows, raiz, error
    
    # -------------------
    # API amigable para GUI (Tkinter)
    # -------------------
    def biseccion_dict(self, expr_or_callable, a: float, b: float, tol: float, max_iter: int = None, mostrar_pasos: bool = True):
        """Devuelve la salida en formato dict {'pasos', 'solucion', 'mensaje'}

        - Compatible con las funciones top-level `bisection`/`find_bracketing_interval`
        - Útil para pasar directamente a widgets de Tkinter (mostrar pasos, root, mensaje)
        """
        # preferir la implementación top-level si existe (Fraction-aware)
        try:
            # usar max_iter si se pasa, si no usar self.max_iter
            mi = max_iter if max_iter is not None else self.max_iter
            # la función top-level se llama `bisection` en este archivo
            if 'bisection' in globals():
                return bisection(expr_or_callable, a, b, tol=tol, max_iter=mi, mostrar_pasos=mostrar_pasos)
        except Exception:
            pass

        # fallback: usar la implementación de la clase (compat) y convertir a dict
        rows, raiz, error = self.biseccion(expr_or_callable, a, b, tol)
        pasos = []
        for r in rows:
            pasos.append({
                'iter': r.get('Iteración'),
                'a': r.get('a'),
                'b': r.get('b'),
                'c': r.get('c'),
                'fa': r.get('f(a)'),
                'fb': r.get('f(b)'),
                'fc': r.get('f(c)'),
                'prod': r.get('f(a)*f(c)'),
            })
        # rows contain the signed f(c) values; `error` is abs(fc) returned by the compat biseccion
        f_root_signed = rows[-1].get('f(c)') if rows else None
        solucion = {'root': raiz, 'f_root': f_root_signed, 'abs_error': error, 'iteraciones': len(rows)} if rows else None
        mensaje = 'Convergencia (compat)' if solucion is not None else 'No hubo solución (compat)'
        return {'pasos': pasos if mostrar_pasos else [], 'solucion': solucion, 'mensaje': mensaje}

    def find_bracketing_interval(self, f: str, x0: float = 0.0, step: float = 1.0, max_steps: int = 50):
        """Alias amigable que usa la función top-level `find_bracketing_interval` si está disponible."""
        try:
            if 'find_bracketing_interval' in globals():
                # call top-level, prefer more samples for robustness
                return find_bracketing_interval(f, x0=x0, step=step, max_steps=max_steps, samples=100)
        except Exception:
            pass
        # fallback simple: reuse find_sign_change_interval
        return self.find_sign_change_interval(f, ranges=None, samples=400)



