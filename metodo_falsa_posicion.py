"""metodo_falsa_posicion.py
Clase que encapsula la lógica del método de Falsa Posición (Regula Falsi).
Devuelve datos en formato fácilmente consumible por una interfaz (lista de dicts y un dict final).
"""

from typing import Callable, List, Dict, Optional, Tuple
import sympy as sp
import numpy as np


class FalsePositionSolver:
    """Encapsula la lógica del método de Falsa Posición.

    API principal:
      solver = FalsePositionSolver(max_iter=100)
      rows, result = solver.solve(expr_or_callable, a, b, tol)

    - rows: lista de dicts con claves: 'Iteración', 'a', 'b', 'c', 'f(a)', 'f(b)', 'f(c)', 'error'
    - result: dict con 'root', 'error', 'iterations', 'f_root'

    El método no realiza ninguna operación sobre UI; lanza excepciones en caso de errores.
    """

    def __init__(self, max_iter: int = 100):
        self.max_iter = int(max_iter)

    # --------------------
    # Utilidades / parsing
    # --------------------
    @staticmethod
    def _normalize_expr(expr_str: str) -> str:
        if '=' in expr_str:
            left, right = expr_str.split('=', 1)
            expr_str = f"({left}) - ({right})"
        return expr_str.replace('^', '**')

    @staticmethod
    def parse_expression(expr_str: str) -> Tuple[sp.Expr, Callable]:
        """Devuelve (sympy_expr, f_callable) o lanza ValueError si la expresión es inválida."""
        # Si el usuario pasó algo como 'f(x)= ...' extraer la parte derecha
        import re
        m = re.match(r"^\s*[A-Za-z_]\w*\s*\(x\)\s*=(.*)", expr_str, re.S)
        if m:
            expr_str = m.group(1)
        txt = FalsePositionSolver._normalize_expr(expr_str)
        # Normalizar llaves usadas en notación matemática (p.ej. e^{-x}) -> e^(-x)
        txt = txt.replace('{', '(').replace('}', ')')
        x = sp.Symbol('x')
        # permitir constantes comunes y exp(...) y mapear 'e' a E
        import re
    # Normalizar notación frecuente de potencia de e escrita como 'e^(-x)'
        # Preferimos 'exp(-x)' porque lambdify mapeará exp a numpy.exp sin ambigüedad.
        txt = re.sub(r"\be\^\s*\(", "exp(", txt)
        # También convertir formas como 'e^x' a 'e**x' para que '**' sea consistente
        txt = re.sub(r"\be\^", "e**", txt)
        locals_map = {'e': sp.E, 'pi': sp.pi}
        try:
            sym_f = sp.sympify(txt, locals=locals_map, convert_xor=True)
        except Exception as e:
            raise ValueError(f"Expresión inválida: {e}")
        try:
            # al crear la función numérica, exponer constantes y exp a numpy
            f_num = sp.lambdify(x, sym_f, modules=[{'e': np.e, 'pi': np.pi, 'exp': np.exp}, 'numpy'])
        except Exception as e:
            raise ValueError(f"No se pudo crear función numérica: {e}")
        return sym_f, f_num

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
    # Método: Falsa Posición
    # --------------------
    def solve(self, expr_or_callable, a: float, b: float, tol: float, return_dataframe: bool = False):
        """Ejecuta la Falsa Posición.

        - expr_or_callable: cadena (se parsea) o callable f(x)
        - a, b: extremos
        - tol: tolerancia (float)
        - return_dataframe: si True intenta devolver un pandas.DataFrame como primer elemento
        """
        # Preparar callable
        if isinstance(expr_or_callable, str):
            _, f = self.parse_expression(expr_or_callable)
        elif callable(expr_or_callable):
            f = expr_or_callable
        else:
            raise ValueError('expr_or_callable debe ser una cadena o una función callable')

        # evaluar extremos
        try:
            fa = float(f(a))
            fb = float(f(b))
        except Exception as e:
            raise ValueError(f"Error al evaluar f(a) o f(b): {e}")

        if not np.isfinite(fa) or not np.isfinite(fb):
            raise ValueError('f(a) o f(b) no es finito')
        if fa * fb > 0:
            raise ValueError('f(a) y f(b) deben tener signos opuestos')

        rows: List[Dict] = []
        c = a
        fc = None
        for i in range(1, self.max_iter + 1):
            # Fórmula de Regula Falsi
            denom = (fb - fa)
            if denom == 0:
                raise ZeroDivisionError('Denominador cero en fórmula de Falsa Posición')
            c = (a * fb - b * fa) / denom
            try:
                fc = float(f(c))
            except Exception as e:
                raise ValueError(f"Error al evaluar f(c): {e}")

            # Usar como "error" el residual |f(c)| para consistencia
            interval_error = abs(b - a) / 2.0
            residual = abs(fc)
            rows.append({
                'Iteración': i,
                'a': float(a),
                'b': float(b),
                'c': float(c),
                'f(a)': float(fa),
                'f(b)': float(fb),
                'f(c)': float(residual),
                'error': float(residual),
                'abs_error': float(residual),
                'interval_error': float(interval_error)
            })

            # Criterio de parada: |f(c)| <= tolerancia
            if residual <= tol:
                break

            # Actualizar extremos
            if fa * fc < 0:
                b, fb = c, fc
            else:
                a, fa = c, fc

        if fc is None:
            raise RuntimeError('No se obtuvo evaluación válida de f(c) durante la iteración')

        # Reportar como error final el residual |f(c)|
        interval_error = abs(b - a) / 2.0
        result = {
            'root': float(c),
            'error': float(abs(fc)),
            'abs_error': float(abs(fc)),
            'iterations': i,
            'f_root': float(abs(fc))
        }

        if return_dataframe:
            try:
                import pandas as pd
                return pd.DataFrame(rows), result
            except Exception:
                # si pandas no está disponible, caer en el comportamiento estándar
                pass

        return rows, result

    def find_sign_change_interval(self, expr_str: str, ranges=None, samples: int = 400):
        """Intentar encontrar un subintervalo [a,b] con cambio de signo para la expresión.

        Devuelve la primera pareja (a, b) encontrada o None si no encuentra.
        Evita puntos donde la evaluación falla o devuelve no finito.
        """
        if ranges is None:
            ranges = [(-1, 1), (-10, 10), (-100, 100), (-1000, 1000)]

        # preparar función callable (si falla, devolvemos None)
        try:
            sym_f, fnum = self.parse_expression(expr_str)
        except Exception:
            return None

        # intentar detectar raíces del denominador (singularidades) para evitar intervalos que las contengan
        denom_roots = []
        try:
            x = sp.Symbol('x')
            denom = sp.together(sym_f).as_numer_denom()[1]
            if denom != 1:
                # intentar resolver raíces exactas (polinomios simples)
                roots = sp.solve(sp.simplify(denom), x)
                for r in roots:
                    try:
                        rv = float(r)
                        denom_roots.append(rv)
                    except Exception:
                        # ignorar raíces no numéricas
                        pass
        except Exception:
            # falla la detección simbólica: seguir sin lista de singularidades
            denom_roots = []

        for low, high in ranges:
            xs = np.linspace(low, high, samples)
            try:
                ys = fnum(xs)
                ys = np.array(ys, dtype=float)
            except Exception:
                # evaluación vectorial falló; probar evaluaciones punto a punto
                ys = []
                for xi in xs:
                    try:
                        yi = float(fnum(xi))
                    except Exception:
                        yi = np.nan
                    ys.append(yi)
                ys = np.array(ys, dtype=float)

            finite = np.isfinite(ys)
            for i in range(len(xs) - 1):
                if not (finite[i] and finite[i + 1]):
                    continue
                yi, yj = ys[i], ys[i + 1]
                if yi == 0:
                    return float(xs[i]), float(xs[i])
                if yi * yj < 0:
                    # antes de aceptar el intervalo, comprobar puntos intermedios
                    mid_xs = np.linspace(xs[i], xs[i+1], 9)
                    safe = True
                    # rechazar si intervalo contiene una raíz del denominador
                    for dr in denom_roots:
                        if dr >= xs[i] and dr <= xs[i+1]:
                            safe = False
                            break
                    if not safe:
                        continue
                    for mx in mid_xs:
                        try:
                            my = float(fnum(mx))
                        except Exception:
                            safe = False
                            break
                        if not np.isfinite(my):
                            safe = False
                            break
                    if safe:
                        return float(xs[i]), float(xs[i + 1])

        return None


# Pequeño ejemplo de uso (ejecutar desde otro módulo/CLI)
if __name__ == '__main__':
    s = FalsePositionSolver(max_iter=50)
    rows, res = s.solve('x**3 - 2*x - 5', 1, 3, 1e-6)
    print(res)
    for r in rows:
        print(r)
