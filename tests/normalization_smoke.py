"""
Normalization smoke tests for expression parsing across solvers.
Run:
    python -m tests.normalization_smoke
"""
from __future__ import annotations

import sys
import traceback

# Targets
from metodo_biseccion import _to_callable, MetodoBiseccion
from metodo_newton_raph import NewtonRaphsonSolver
from metodo_secante import SecantSolver


def _check_no_func_star_paren(text: str) -> None:
    import re
    pat = re.compile(r"\b(sin|cos|tan|exp|log|ln|sqrt|abs|asin|acos|atan|cot|sec|csc)\s*\*\s*\(", re.IGNORECASE)
    assert not pat.search(text), f"Found forbidden pattern 'func*((' in: {text}"


def run() -> None:
    errors = []

    cases = [
        r"\cos(x)-x",
        r"\ln(x)-1",
        r"\sqrt{x}-2",
        r"e^(x)-2",
        r" sin ( x ) + 2 ",
        r"cos (x) - x",
        r"2x+3",
        r"3(x+1)",
    ]

    # Bisección: callable via _to_callable, and parse_expression for numpy callable
    try:
        mb = MetodoBiseccion(max_iter=50)
        for expr in cases:
            f = _to_callable(expr)
            _ = f(0.5)  # use positive point to avoid ln domain issues
            sym, fnum = mb.parse_expression(expr)
            _ = float(fnum(0.1))
    except Exception as e:
        errors.append(f"Bisección parsing/eval failed: {e}")

    # Newton: normalization and parse_expression
    try:
        nsolver = NewtonRaphsonSolver(max_iter=50)
        for expr in cases:
            norm = nsolver._normalize_expr(expr)
            _check_no_func_star_paren(norm)
            sym, fnum, dnum = nsolver.parse_expression(expr)
            _ = float(fnum(0.2))
    except Exception as e:
        errors.append(f"Newton parsing/eval failed: {e}")

    # Secante: normalization and parse_expression
    try:
        ssolver = SecantSolver(max_iter=50)
        for expr in cases:
            norm = ssolver._normalize_expr(expr)
            _check_no_func_star_paren(norm)
            sym, fnum = ssolver.parse_expression(expr)
            _ = float(fnum(0.3))
    except Exception as e:
        errors.append(f"Secante parsing/eval failed: {e}")

    if errors:
        for e in errors:
            print("FAIL:", e)
        raise SystemExit(1)
    else:
        print("OK: normalization and parsing smoke tests passed (", len(cases), "cases )")


if __name__ == "__main__":
    try:
        run()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(1)
