"""run_biseccion_cli.py

Pequeño programa de consola para probar la clase MetodoBiseccion.

Uso básico (desde PowerShell en la carpeta del proyecto):
    python run_biseccion_cli.py --expr "x**3-2*x-5" --a 1 --b 3 --tol 1e-6

Opciones relevantes:
    --expr        : expresión en x (puede usar '=' o '^')
    --a --b       : extremos del intervalo (si no se pasan y se usa --auto-interval la clase intentará encontrar uno)
    --tol         : tolerancia (ej: 1e-6 o 10^-6 o x10^ - ver parse_tolerance)
    --auto-interval: intenta detectar automáticamente un subintervalo con cambio de signo
    --csv FILE    : si se pasa escribe la tabla de iteraciones en FILE (CSV)

Requisito: `metodo_biseccion.py` con la clase MetodoBiseccion en el mismo directorio/paquete.
"""

import argparse
import sys
import math

try:
    from metodo_biseccion import MetodoBiseccion
except Exception as e:
    print("ERROR: no se pudo importar 'metodo_biseccion.MetodoBiseccion'. Asegúrate de que el archivo 'metodo_biseccion.py' exista y defina la clase MetodoBiseccion.")
    print("Detalle:", e)
    sys.exit(2)

try:
    import pandas as pd
except Exception:
    pd = None


def main():
    p = argparse.ArgumentParser(description='CLI para probar MetodoBiseccion')
    # Hacer --expr opcional con un valor por defecto para que el script pueda correr sin parámetros
    p.add_argument(
        '--expr', '-f',
        required=False,
        default='x**3-2*x-5',
        help='Expresión en x (ej: "x**3-2*x-5" o "cos(x)=x"). Por defecto: x**3-2*x-5'
    )
    p.add_argument('--a', type=float, help='Extremo izquierdo a')
    p.add_argument('--b', type=float, help='Extremo derecho b')
    p.add_argument('--tol', default='1e-6', help='Tolerancia (ej: 1e-6, 10^-6, x10^ - formato flexible)')
    p.add_argument('--max-iter', type=int, default=100, help='Máximo de iteraciones (por defecto 100)')
    p.add_argument('--auto-interval', action='store_true', help='Intentar detectar un intervalo con cambio de signo automáticamente')
    p.add_argument('--samples', type=int, default=400, help='Muestras para buscar cambio de signo (si --auto-interval)')
    p.add_argument('--csv', help='Escribir tabla de iteraciones a CSV')
    p.add_argument('--gui', action='store_true', help='Abrir una mini-GUI Tkinter')
    p.add_argument('--auto-test', action='store_true', help='Modo no interactivo para probar la GUI y salir (útil para demos)')
    args = p.parse_args()

    mb = MetodoBiseccion(max_iter=args.max_iter)

    expr = args.expr

    # parse tol
    try:
        tol = MetodoBiseccion.parse_tolerance(args.tol)
    except Exception as e:
        print(f"Error al parsear la tolerancia: {e}")
        sys.exit(3)

    a = args.a
    b = args.b

    # Si no se proporcionan a/b, intentamos detectar un intervalo automáticamente
    # ya sea porque el usuario lo pidió con --auto-interval o porque faltan a/b.
    if (a is None or b is None):
        if not args.auto_interval:
            print("No se proporcionaron --a y --b; intentando auto-interval por defecto…")
        else:
            print("Intentando detectar un intervalo con cambio de signo…")
        # prefer the more robust bracketing routine which samples interior points and
        # tolerates domain errors (use compatibility wrapper which calls top-level)
        try:
            res = mb.find_bracketing_interval(expr, x0=0.0, step=1.0, max_steps=10)
        except Exception:
            res = None
        # res may be dict (from top-level) or tuple (from older implementations)
        interval = None
        if isinstance(res, dict):
            interval = res.get('interval')
        elif isinstance(res, tuple) and len(res) >= 2:
            interval = (res[0], res[1])
        if interval:
            a, b = interval
            print(f"Intervalo detectado: a={a}, b={b}")
        else:
            # Si falla el auto-interval y estamos usando la expresión por defecto, usa un intervalo conocido
            if expr == 'x**3-2*x-5':
                a, b = 1.0, 3.0
                print("No se detectó intervalo automáticamente; usando intervalo por defecto a=1, b=3 para la expresión por defecto.")
            else:
                print("No se encontró un intervalo con cambio de signo en los rangos probados.")
                sys.exit(4)

    if a is None or b is None:
        print("Debes proporcionar --a y --b o permitir la detección automática de intervalo.")
        sys.exit(5)

    # GUI mode: launch a minimal Tkinter interface or run an auto-test (non-interactive)
    if args.gui:
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
        except Exception as e:
            print(f"No se pudo cargar tkinter: {e}")
            sys.exit(7)

        state = {'last_result': None, 'decimal_mode': False}

        def _to_float_from_str(s):
            from fractions import Fraction as _F
            if s is None:
                return None
            if isinstance(s, (int, float)):
                return float(s)
            s = str(s)
            if s.startswith('ERR:'):
                return None
            try:
                if '/' in s:
                    return float(_F(s))
                return float(s)
            except Exception:
                return None

        def _fmt_dec(x):
            try:
                return f"{float(x):.5f}"
            except Exception:
                return ''

        def compute_and_show(expr_val, a_val, b_val, tol_val, csv_file=None):
            try:
                result = mb.biseccion_dict(expr_val, a_val, b_val, tol_val, max_iter=args.max_iter, mostrar_pasos=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error durante bisección: {e}")
                return
            sol = result.get('solucion')
            mensaje = result.get('mensaje')
            if sol:
                label_root_var.set(f"Raíz: {sol.get('root')} (iter={sol.get('iteraciones')})")
            else:
                label_root_var.set("Sin solución")
            label_msg_var.set(str(mensaje))

            # save last result for decimal toggle
            state['last_result'] = result
            state['decimal_mode'] = False

            for i in tree.get_children():
                tree.delete(i)
            for paso in result.get('pasos', []):
                tree.insert('', 'end', values=(paso.get('iter'), paso.get('a'), paso.get('b'), paso.get('c'), paso.get('fa'), paso.get('fb'), paso.get('fc'), paso.get('error') if 'error' in paso else paso.get('prod')))

            if csv_file:
                try:
                    if pd is not None:
                        pd.DataFrame(result.get('pasos', [])).to_csv(csv_file, index=False)
                    else:
                        raise RuntimeError('pandas no está disponible')
                except Exception as e:
                    messagebox.showwarning("CSV", f"No se pudo escribir CSV: {e}")

        # auto-test: run computation and print results, then exit
        if args.auto_test:
            try:
                res = mb.biseccion_dict(expr, a, b, tol, max_iter=args.max_iter, mostrar_pasos=True)
                print('\n[GUI AUTO-TEST] Resultado:')
                print(f"  Raíz: {res.get('solucion', {}).get('root')}")
                print(f"  Mensaje: {res.get('mensaje')}")
                print(f"  Pasos: {len(res.get('pasos', []))}")
                if pd is not None:
                    try:
                        df = pd.DataFrame(res.get('pasos', []))
                        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                            print(df)
                    except Exception:
                        pass
                sys.exit(0)
            except Exception as e:
                print(f"Error en GUI auto-test: {e}")
                sys.exit(8)

        # build GUI
        root = tk.Tk()
        root.title('Bisección (mini GUI)')
        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky='nsew')

        ttk.Label(frm, text='Expresión:').grid(row=0, column=0, sticky='w')
        entry_expr = ttk.Entry(frm, width=30)
        entry_expr.insert(0, expr)
        entry_expr.grid(row=0, column=1, sticky='w')

        ttk.Label(frm, text='a:').grid(row=1, column=0, sticky='w')
        entry_a = ttk.Entry(frm, width=10)
        entry_a.insert(0, str(a))
        entry_a.grid(row=1, column=1, sticky='w')

        ttk.Label(frm, text='b:').grid(row=1, column=2, sticky='w')
        entry_b = ttk.Entry(frm, width=10)
        entry_b.insert(0, str(b))
        entry_b.grid(row=1, column=3, sticky='w')

        ttk.Label(frm, text='tol:').grid(row=2, column=0, sticky='w')
        entry_tol = ttk.Entry(frm, width=10)
        entry_tol.insert(0, str(args.tol))
        entry_tol.grid(row=2, column=1, sticky='w')

        def parse_number_str(s: str) -> float:
            s = s.strip()
            # try plain float
            try:
                return float(s)
            except Exception:
                pass
            # try evaluating simple expressions using pi/e
            try:
                val = eval(s, {"__builtins__": {}}, {'pi': math.pi, 'e': math.e})
                return float(val)
            except Exception as e:
                raise ValueError(f"No se pudo interpretar el número: '{s}' ({e})")

        def on_run_button():
            try:
                a_val = parse_number_str(entry_a.get())
                b_val = parse_number_str(entry_b.get())
            except Exception as e:
                messagebox.showerror("Entrada inválida", f"Error con los extremos: {e}")
                return
            try:
                tol_val = MetodoBiseccion.parse_tolerance(entry_tol.get())
            except Exception as e:
                messagebox.showerror("Entrada inválida", f"Tolerancia inválida: {e}")
                return
            compute_and_show(entry_expr.get(), a_val, b_val, tol_val, args.csv)

        btn_run = ttk.Button(frm, text='Ejecutar', command=on_run_button)
        btn_run.grid(row=2, column=3, sticky='e')

        def on_auto_interval():
            expr_val = entry_expr.get()
            try:
                res = mb.find_bracketing_interval(expr_val)
            except Exception as e:
                messagebox.showerror('Error', f'Error buscando intervalo: {e}')
                return
            # res might be dict (from top-level) or tuple (from compat). Normalize.
            interval = None
            pasos = None
            mensaje = None
            if isinstance(res, dict):
                interval = res.get('interval')
                pasos = res.get('pasos')
                mensaje = res.get('mensaje')
            elif isinstance(res, tuple) and len(res) >= 2:
                interval = (res[0], res[1])
            elif isinstance(res, tuple) and len(res) == 1:
                interval = res[0]

            if interval is None:
                messagebox.showinfo('Intervalo', mensaje or 'No se encontró intervalo con cambio de signo.')
                return

            # interval may be Fractions; convert to float string for entries
            try:
                a_found = float(interval[0])
                b_found = float(interval[1])
            except Exception:
                a_found = None
                b_found = None

            if a_found is not None and b_found is not None:
                use = messagebox.askyesno('Intervalo encontrado', f"Se encontró intervalo: a={a_found}, b={b_found}\n¿Usar este intervalo?")
                if use:
                    entry_a.delete(0, 'end')
                    entry_a.insert(0, str(a_found))
                    entry_b.delete(0, 'end')
                    entry_b.insert(0, str(b_found))
            else:
                messagebox.showinfo('Intervalo', f'Intervalo encontrado: {interval}\n(No se pudo convertir a float)')

        btn_interval = ttk.Button(frm, text='Auto-interval', command=on_auto_interval)
        btn_interval.grid(row=2, column=2, sticky='w')

        def _render_result_decimal(as_decimal: bool):
            # repopulate the tree and label based on state['last_result'] and as_decimal flag
            res = state.get('last_result')
            if not res:
                return
            sol = res.get('solucion')
            if sol:
                root_s = sol.get('root')
                if as_decimal:
                    dec = _to_float_from_str(root_s)
                    root_label = f"Raíz: {root_s} ({_fmt_dec(dec)}) (iter={sol.get('iteraciones')})"
                else:
                    root_label = f"Raíz: {root_s} (iter={sol.get('iteraciones')})"
                label_root_var.set(root_label)
            # repopulate table
            for i in tree.get_children():
                tree.delete(i)
            for paso in res.get('pasos', []):
                a_v = paso.get('a')
                b_v = paso.get('b')
                c_v = paso.get('c')
                fa_v = paso.get('fa')
                fb_v = paso.get('fb')
                fc_v = paso.get('fc')
                err_v = paso.get('error') if 'error' in paso else paso.get('prod')
                if as_decimal:
                    a_v = _fmt_dec(_to_float_from_str(a_v)) if a_v is not None else ''
                    b_v = _fmt_dec(_to_float_from_str(b_v)) if b_v is not None else ''
                    c_v = _fmt_dec(_to_float_from_str(c_v)) if c_v is not None else ''
                    fa_v = _fmt_dec(_to_float_from_str(fa_v)) if fa_v is not None else ''
                    fb_v = _fmt_dec(_to_float_from_str(fb_v)) if fb_v is not None else ''
                    fc_v = _fmt_dec(_to_float_from_str(fc_v)) if fc_v is not None else ''
                    err_v = _fmt_dec(_to_float_from_str(err_v)) if err_v is not None else ''
                tree.insert('', 'end', values=(paso.get('iter'), a_v, b_v, c_v, fa_v, fb_v, fc_v, err_v))

        def on_toggle_decimal():
            if state.get('last_result') is None:
                messagebox.showinfo('Info', 'No hay resultados para convertir. Ejecuta la bisección primero.')
                return
            state['decimal_mode'] = not state['decimal_mode']
            _render_result_decimal(state['decimal_mode'])
            btn_decimal.config(text='Mostrar fracciones' if state['decimal_mode'] else 'Mostrar decimales')

        btn_decimal = ttk.Button(frm, text='Mostrar decimales', command=on_toggle_decimal)
        btn_decimal.grid(row=2, column=4, sticky='w')

        label_root_var = tk.StringVar(value='Raíz: --')
        label_msg_var = tk.StringVar(value='')
        ttk.Label(frm, textvariable=label_root_var).grid(row=3, column=0, columnspan=4, sticky='w')
        ttk.Label(frm, textvariable=label_msg_var).grid(row=4, column=0, columnspan=4, sticky='w')

        cols = ('iter', 'a', 'b', 'c', 'fa', 'fb', 'fc', 'error')
        tree = ttk.Treeview(frm, columns=cols, show='headings', height=10)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=80)
        tree.grid(row=5, column=0, columnspan=4, sticky='nsew')

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.mainloop()
        return

    try:
        rows, raiz, error = mb.biseccion(expr, a, b, tol)
    except Exception as e:
        print(f"Error durante bisección: {e}")
        sys.exit(6)

    print('\nResultado:')
    print(f"  Raíz aproximada: {raiz}")
    print(f"  Error final (|f(c)|): {error}")
    print(f"  Iteraciones: {len(rows)}\n")

    # mostrar tabla
    if pd is not None:
        df = pd.DataFrame(rows)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)
    else:
        # impresión sencilla si no hay pandas
        print('Iter\ta\tb\tc\tf(a)\tf(b)\tf(c)\tf(a)*f(c)')
        for r in rows:
            print(f"{r['Iteración']}\t{r['a']:.6g}\t{r['b']:.6g}\t{r['c']:.6g}\t{r['f(a)']:.6g}\t{r['f(b)']:.6g}\t{r['f(c)']:.6g}\t{r['f(a)*f(c)']:.6g}")

    if args.csv:
        try:
            if pd is not None:
                df.to_csv(args.csv, index=False)
            else:
                # escribir CSV manualmente
                import csv
                with open(args.csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for r in rows:
                        writer.writerow(r)
            print(f"Tabla guardada en {args.csv}")
        except Exception as e:
            print(f"No se pudo escribir CSV: {e}")


if __name__ == '__main__':
    main()
