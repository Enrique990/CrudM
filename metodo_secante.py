"""metodo_secante.py
Implementa la lógica del Método de la Secante sin modificar la interfaz.

API principal (similar a Newton y Falsa Posición):

	from metodo_secante import SecantSolver
	solver = SecantSolver(max_iter=100)
	rows, result = solver.solve(expr_or_callable, x0, x1, tol)

Salida:
	- rows: lista de dicts por iteración (sin columna 'error'). Incluye claves:
		'Iteración', 'x_prev', 'x', 'f(x_prev)', 'f(x)', 'x_next', 'delta_x'
	  Nota: reportamos |f(...)| para consistencia con el contrato reciente (|f(c)|).
	- result: dict con claves:
		'root' (float), 'abs_error' (|f(root)|), 'f_root' (|f(root)|),
		'iteraciones' (int), 'iterations' (int), 'mensaje' (str)

No se realizan cambios de UI; esta lógica es consumible por la misma interfaz
que usa Bisección / Falsa Posición / Newton.no se deve de ralizar ma cambios pq esto ya funciona bien con el main.py
"""

from typing import Callable, List, Dict, Tuple
import sympy as sp
import numpy as np


class SecantSolver:
	def __init__(self, max_iter: int = 100):
		self.max_iter = int(max_iter)

	# --------------------
	# Utilidades / parsing
	# --------------------
	@staticmethod
	def _normalize_expr(expr_str: str) -> str:
		# Unificar '=' como resta, y '^' como potencia de Python
		if '=' in expr_str:
			left, right = expr_str.split('=', 1)
			expr_str = f"({left}) - ({right})"
		txt = expr_str.replace('^', '**')
		# Normalizar llaves y notación común con e^
		txt = txt.replace('{', '(').replace('}', ')')
		import re
		txt = re.sub(r"\be\^\s*\(", "exp(", txt)
		txt = re.sub(r"\be\^", "e**", txt)
		# Aliases frecuentes en español
		txt = re.sub(r"\bsen\s*\(", 'sin(', txt, flags=re.IGNORECASE)
		txt = re.sub(r"\bln\s*\(", 'log(', txt, flags=re.IGNORECASE)
		return txt

	@staticmethod
	def parse_expression(expr_str: str) -> Tuple[sp.Expr, Callable]:
		"""Devuelve (sympy_expr, f_callable) o lanza ValueError si la expresión es inválida."""
		txt = SecantSolver._normalize_expr(expr_str)
		x = sp.Symbol('x')
		locals_map = {'e': sp.E, 'pi': sp.pi}
		try:
			sym_f = sp.sympify(txt, locals=locals_map, convert_xor=True)
		except Exception as e:
			raise ValueError(f"Expresión inválida: {e}")
		try:
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
	# Método: Secante
	# --------------------
	def solve(self, expr_or_callable, x0: float, x1: float, tol: float, return_dataframe: bool = False):
		"""Ejecuta el método de la Secante.

		- expr_or_callable: cadena (se parsea) o callable f(x)
		- x0, x1: puntos iniciales
		- tol: tolerancia (float)
		- return_dataframe: si True devuelve un DataFrame como primer valor (si pandas está disponible)
		"""
		# Preparar f
		if isinstance(expr_or_callable, str):
			_, f = self.parse_expression(expr_or_callable)
		elif callable(expr_or_callable):
			f = expr_or_callable
		else:
			raise ValueError('expr_or_callable debe ser una cadena o una función callable')

		try:
			x_prev = float(x0)
			x_curr = float(x1)
			f_prev = float(f(x_prev))
			f_curr = float(f(x_curr))
		except Exception as e:
			raise ValueError(f"Error al evaluar f en los puntos iniciales: {e}")

		rows: List[Dict] = []
		iters = 0
		mensaje = ""

		# Si alguno ya cumple por residual, registrar una sola fila mínima
		if abs(f_prev) <= tol and abs(f_curr) <= tol:
			# Preferir x_curr como raíz candidata
			rows.append({'Iteración': 1, 'x_prev': x_prev, 'x': x_curr, 'f(x_prev)': abs(f_prev), 'f(x)': abs(f_curr), 'x_next': x_curr, 'delta_x': 0.0})
			result = {
				'root': float(x_curr),
				'abs_error': float(abs(f_curr)),
				'f_root': float(abs(f_curr)),
				'iteraciones': 1,
				'iterations': 1,
				'mensaje': 'Convergencia alcanzada por criterio |f(x)|'
			}
			return rows, result

		for i in range(1, self.max_iter + 1):
			iters = i
			denom = (f_curr - f_prev)
			if denom == 0.0:
				mensaje = 'Denominador cero en fórmula de secante'
				# Registrar estado y salir
				rows.append({'Iteración': i, 'x_prev': x_prev, 'x': x_curr, 'f(x_prev)': abs(f_prev), 'f(x)': abs(f_curr), 'x_next': x_curr, 'delta_x': 0.0})
				break

			x_next = x_curr - f_curr * (x_curr - x_prev) / denom
			delta_x = abs(x_next - x_curr)

			# Evaluar residual en x_curr (antes de actualizar) para guardar en fila
			rows.append({
				'Iteración': i,
				'x_prev': float(x_prev),
				'x': float(x_curr),
				'f(x_prev)': float(abs(f_prev)),
				'f(x)': float(abs(f_curr)),
				'x_next': float(x_next),
				'delta_x': float(delta_x)
			})

			# Actualizar
			x_prev, x_curr = x_curr, float(x_next)
			f_prev, f_curr = f_curr, float(f(x_curr))

			# Criterio de parada por residual |f(x)| en el nuevo punto
			if abs(f_curr) <= tol:
				# Sobrescribir la última fila para que refleje el punto convergido
				if rows:
					rows[-1] = {
						'Iteración': i,
						'x_prev': float(x_prev),  # el previo al convergido
						'x': float(x_curr),       # punto convergido
						'f(x_prev)': float(abs(f_prev)),
						'f(x)': float(abs(f_curr)),
						'x_next': float(x_curr),
						'delta_x': 0.0
					}
				mensaje = 'Convergencia alcanzada por criterio |f(x)|'
				break

		result = {
			'root': float(x_curr),
			'abs_error': float(abs(f_curr)),
			'f_root': float(abs(f_curr)),
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


__all__ = ['SecantSolver']

