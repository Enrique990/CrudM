"""metodo_newton_raph.py
Implementa la lógica del método de Newton–Raphson sin modificar la interfaz.

API principal (similar a los otros solvers):

    from metodo_newton_raph import NewtonRaphsonSolver
    solver = NewtonRaphsonSolver(max_iter=100)
    rows, result = solver.solve(expr_or_callable, x0, tol)

Salida:
    - rows: lista de dicts por iteración, sin columna 'error'. Incluye claves:
        'Iteración', 'x', 'f(x)', "f'(x)", 'x_next', 'delta_x'
      Nota: 'f(x)' se reporta en valor absoluto para consistencia con el contrato reciente (|f(c)|).
    - result: dict con claves:
        'root' (float), 'abs_error' (|f(root)|), 'f_root' (|f(root)|),
        'iteraciones' (int), 'iterations' (int), 'mensaje' (str)

No se realizan cambios de UI; esta lógica es consumible por la misma interfaz
que usa Bisección y Falsa Posición.
"""

from typing import Callable, List, Dict, Tuple, Optional
import sympy as sp
import numpy as np


class NewtonRaphsonSolver:
    def __init__(self, max_iter: int = 100):
        self.max_iter = int(max_iter)

    # --------------------
    # Utilidades / parsing
    # --------------------
    @staticmethod
    def _normalize_expr(expr_str: str) -> str:
        # Igual que en Falsa Posición: normalizar '=' y '^'
        if '=' in expr_str:
            left, right = expr_str.split('=', 1)
            expr_str = f"({left}) - ({right})"
        txt = expr_str.replace('^', '**')
        # Normalizar llaves usadas en notación matemática
        txt = txt.replace('{', '(').replace('}', ')')
        # Normalizar notación frecuente e^(...) -> exp(...), e^x -> e**x
        import re
        txt = re.sub(r"\be\^\s*\(", "exp(", txt)
        txt = re.sub(r"\be\^", "e**", txt)
        # Aliases comunes en español (opcionales)
        txt = re.sub(r"\bsen\s*\(", 'sin(', txt, flags=re.IGNORECASE)
        txt = re.sub(r"\bln\s*\(", 'log(', txt, flags=re.IGNORECASE)
        return txt

    @staticmethod
    def parse_expression(expr_str: str) -> Tuple[sp.Expr, Callable, Optional[Callable]]:
        """Devuelve (sympy_expr, f_callable, df_callable) o lanza ValueError.

        df_callable puede ser None si no se logra derivar.
        """
        txt = NewtonRaphsonSolver._normalize_expr(expr_str)
        x = sp.Symbol('x')
        locals_map = {'e': sp.E, 'pi': sp.pi}
        try:
            sym_f = sp.sympify(txt, locals=locals_map, convert_xor=True)
        except Exception as e:
            raise ValueError(f"Expresión inválida: {e}")
        # Crear funciones numéricas para f y f'
        try:
            f_num = sp.lambdify(x, sym_f, modules=[{'e': np.e, 'pi': np.pi, 'exp': np.exp}, 'numpy'])
        except Exception as e:
            raise ValueError(f"No se pudo crear función numérica: {e}")

        df_num = None
        try:
            dsym = sp.diff(sym_f, x)
            df_num = sp.lambdify(x, dsym, modules=[{'e': np.e, 'pi': np.pi, 'exp': np.exp}, 'numpy'])
        except Exception:
            df_num = None

        return sym_f, f_num, df_num

    @staticmethod
    def parse_tolerance(tol_str: str) -> float:
        s = str(tol_str).strip().lower().replace('×', 'x')
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

    # --------------------
    # Método: Newton–Raphson
    # --------------------
    def solve(self, expr_or_callable, x0: float, tol: float, return_dataframe: bool = False):
        """Ejecuta Newton–Raphson.

        - expr_or_callable: cadena (se parsea y deriva) o callable f(x)
        - x0: punto inicial
        - tol: tolerancia (float)
        - return_dataframe: si True e instalado pandas, devuelve DataFrame como primer valor
        """
        # Preparar f y df
        df_callable = None
        if isinstance(expr_or_callable, str):
            _, f, df_callable = self.parse_expression(expr_or_callable)
        elif callable(expr_or_callable):
            f = expr_or_callable
        else:
            raise ValueError('expr_or_callable debe ser una cadena o una función callable')

        # Derivada numérica si no tenemos df simbólica
        def _num_derivative(g: Callable, x: float) -> float:
            h = 1e-6 if abs(x) <= 1 else 1e-6 * abs(x)
            return (float(g(x + h)) - float(g(x - h))) / (2.0 * h)

        def _df(x: float) -> float:
            if df_callable is not None:
                return float(df_callable(x))
            return _num_derivative(f, x)

        rows: List[Dict] = []
        x = float(x0)
        fx = None
        iters = 0
        mensaje = ""

        for i in range(1, self.max_iter + 1):
            iters = i
            try:
                fx_val = float(f(x))
            except Exception as e:
                raise ValueError(f"Error al evaluar f(x) en x={x}: {e}")

            fx_abs = abs(fx_val)
            # Criterio de parada basado en |f(x)|
            if fx_abs <= tol and i == 1:
                # Registrar igualmente una fila mínima
                rows.append({'Iteración': i, 'x': float(x), 'f(x)': float(fx_abs), "f'(x)": float(_df(x)), 'x_next': float(x), 'delta_x': 0.0})
                mensaje = 'Convergencia alcanzada por criterio |f(x)|'
                fx = fx_val
                break

            try:
                dfx = float(_df(x))
            except Exception as e:
                raise ValueError(f"Error al evaluar f'(x) en x={x}: {e}")

            if dfx == 0.0:
                mensaje = "Derivada nula; no es posible continuar"
                rows.append({'Iteración': i, 'x': float(x), 'f(x)': float(fx_abs), "f'(x)": float(dfx), 'x_next': float(x), 'delta_x': 0.0})
                fx = fx_val
                break

            x_next = x - fx_val / dfx
            delta_x = abs(x_next - x)

            rows.append({
                'Iteración': i,
                'x': float(x),
                'f(x)': float(fx_abs),
                "f'(x)": float(dfx),
                'x_next': float(x_next),
                'delta_x': float(delta_x)
            })

            x = float(x_next)
            fx = fx_val

            # Parada por residual |f(x)| en el nuevo x
            try:
                fx_new = float(f(x))
            except Exception as e:
                raise ValueError(f"Error al evaluar f(x) luego de actualizar x={x}: {e}")
            if abs(fx_new) <= tol:
                mensaje = 'Convergencia alcanzada por criterio |f(x)|'
                fx = fx_new
                break

        if fx is None:
            # si por alguna razón no se evaluó, intentarlo
            try:
                fx = float(f(x))
            except Exception:
                fx = np.nan

        result = {
            'root': float(x),
            'abs_error': float(abs(fx)),
            'f_root': float(abs(fx)),
            'iteraciones': int(iters),
            'iterations': int(iters),
            'mensaje': mensaje or ('No convergió en el máximo de iteraciones' if iters >= self.max_iter else 'Finalizado')
        }

        if return_dataframe:
            try:
                import pandas as pd
                return pd.DataFrame(rows), result
            except Exception:
                pass

        return rows, result


__all__ = [
    'NewtonRaphsonSolver',
]
