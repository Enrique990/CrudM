import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from tkinter import ttk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from metodo_falsa_posicion import FalsePositionSolver


class FalsaPosicionGUI:
    def __init__(self, master):
        self.master = master
        master.title('Falsa Posición - Interfaz')
        master.geometry('900x650')

        self.solver = FalsePositionSolver(max_iter=100)

        frm_top = ttkb.Frame(master)
        frm_top.pack(fill='x', padx=10, pady=8)

        ttkb.Label(frm_top, text='f(x):').grid(row=0, column=0, sticky='w')
        self.entry_expr = ttkb.Entry(frm_top, width=50)
        self.entry_expr.grid(row=0, column=1, columnspan=4, padx=6)
        self.entry_expr.insert(0, 'x**3 - 2*x - 5')

        ttkb.Label(frm_top, text='a:').grid(row=1, column=0, sticky='w')
        self.entry_a = ttkb.Entry(frm_top, width=12)
        self.entry_a.grid(row=1, column=1, sticky='w')
        self.entry_a.insert(0, '1')

        ttkb.Label(frm_top, text='b:').grid(row=1, column=2, sticky='w')
        self.entry_b = ttkb.Entry(frm_top, width=12)
        self.entry_b.grid(row=1, column=3, sticky='w')
        self.entry_b.insert(0, '3')

        ttkb.Label(frm_top, text='Tolerancia:').grid(row=2, column=0, sticky='w')
        self.entry_tol = ttkb.Entry(frm_top, width=12)
        self.entry_tol.grid(row=2, column=1, sticky='w')
        self.entry_tol.insert(0, '1e-6')

        ttkb.Label(frm_top, text='Max iter:').grid(row=2, column=2, sticky='w')
        self.entry_max = ttkb.Entry(frm_top, width=12)
        self.entry_max.grid(row=2, column=3, sticky='w')
        self.entry_max.insert(0, '100')

        ttkb.Button(frm_top, text='Calcular', command=self.on_calculate, bootstyle='success').grid(row=0, column=5, padx=6)
        ttkb.Button(frm_top, text='Graficar', command=self.on_plot, bootstyle='info').grid(row=1, column=5, padx=6)
        ttkb.Button(frm_top, text='Exportar CSV', command=self.on_export_csv, bootstyle='secondary').grid(row=2, column=5, padx=6)
        # Botón para sugerir intervalo automáticamente
        ttkb.Button(frm_top, text='Sugerir intervalo', command=self.on_suggest_interval, bootstyle='info').grid(row=0, column=6, padx=6)

        # Treeview y scroll
        frm_mid = ttkb.Frame(master)
        frm_mid.pack(fill='both', expand=False, padx=10, pady=6)

        cols = ['Iteración', 'a', 'b', 'c', 'f(a)', 'f(b)', 'f(c)', 'error']
        self.tree = ttk.Treeview(frm_mid, columns=cols, show='headings', height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor='center')
        vsb = ttk.Scrollbar(frm_mid, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Plot area
        frm_plot = ttkb.Frame(master)
        frm_plot.pack(fill='both', expand=True, padx=10, pady=6)
        self.fig = Figure(figsize=(6, 3.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frm_plot)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Estado
        self.last_rows = []
        self.last_result = None

    def parse_inputs(self):
        expr = self.entry_expr.get().strip()
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            tol = self.solver.parse_tolerance(self.entry_tol.get())
            max_iter = int(self.entry_max.get())
        except Exception as e:
            raise ValueError(f'Entradas inválidas: {e}')
        return expr, a, b, tol, max_iter

    def on_calculate(self):
        try:
            expr, a, b, tol, max_iter = self.parse_inputs()
            self.solver.max_iter = max_iter
            rows, result = self.solver.solve(expr, a, b, tol)
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return

        # poblar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            vals = (r['Iteración'], r['a'], r['b'], r['c'], r['f(a)'], r['f(b)'], r['f(c)'], r['error'])
            self.tree.insert('', 'end', values=tuple(f"{v:.6g}" if isinstance(v, (int, float)) else str(v) for v in vals))

        self.last_rows = rows
        self.last_result = result
        messagebox.showinfo('Resultado', f"Raíz ≈ {result['root']:.12g}\nError = {result['error']:.12g}\nIteraciones = {result['iterations']}")
        # dibujar
        try:
            self.plot_function(expr, a, b, result['root'])
        except Exception:
            pass

    def on_plot(self):
        expr = self.entry_expr.get().strip()
        try:
            sym, f = self.solver.parse_expression(expr)
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            self.plot_function(expr, a, b, None)
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def on_suggest_interval(self):
        expr = self.entry_expr.get().strip()
        if not expr:
            messagebox.showerror('Error', 'Ingrese una expresión antes de sugerir intervalo')
            return
        try:
            interval = self.solver.find_sign_change_interval(expr)
        except Exception as e:
            messagebox.showerror('Error', f'Error durante la búsqueda de intervalo: {e}')
            return
        if not interval:
            messagebox.showinfo('Sin intervalo', 'No se encontró un intervalo con cambio de signo en los rangos probados.')
            return
        a_s, b_s = interval
        # Mostrar un diálogo con opciones: usar y ejecutar, usar (solo rellenar), cancelar
        dlg = tk.Toplevel(self.master)
        dlg.title('Intervalo detectado')
        dlg.transient(self.master)
        dlg.grab_set()

        msg = ttkb.Label(dlg, text=f'Se detectó un posible intervalo con cambio de signo:\n[{a_s:.6g}, {b_s:.6g}]')
        msg.pack(padx=12, pady=(12, 6))

        btn_frame = ttkb.Frame(dlg)
        btn_frame.pack(padx=12, pady=(0, 12))

        def use_and_fill():
            self.entry_a.delete(0, 'end')
            self.entry_b.delete(0, 'end')
            self.entry_a.insert(0, f"{a_s:.6g}")
            self.entry_b.insert(0, f"{b_s:.6g}")
            dlg.destroy()

        def use_and_run():
            use_and_fill()
            # Llamar al cálculo inmediatamente
            try:
                self.on_calculate()
            except Exception:
                # on_calculate ya muestra errores vía messagebox
                pass

        def cancel():
            dlg.destroy()

        ttkb.Button(btn_frame, text='Usar y ejecutar', command=use_and_run, bootstyle='success').pack(side='left', padx=6)
        ttkb.Button(btn_frame, text='Usar (llenar)', command=use_and_fill, bootstyle='secondary').pack(side='left', padx=6)
        ttkb.Button(btn_frame, text='Cancelar', command=cancel, bootstyle='danger').pack(side='left', padx=6)

        # Esperar a que el diálogo se cierre antes de volver al flujo
        self.master.wait_window(dlg)

    def plot_function(self, expr_or_callable, a, b, root=None):
        # obtener callable
        if isinstance(expr_or_callable, str):
            _, f = self.solver.parse_expression(expr_or_callable)
        else:
            f = expr_or_callable
        xs = np.linspace(a, b, 400)
        ys = np.array([np.nan if not np.isfinite(f(x)) else f(x) for x in xs], dtype=float)
        self.ax.clear()
        self.ax.plot(xs, ys, label='f(x)')
        self.ax.axhline(0, color='gray', linewidth=0.8)
        if root is not None:
            try:
                yroot = float(f(root))
                self.ax.plot(root, yroot, 'ro', label=f'raíz ≈ {root:.6g}')
                self.ax.axvline(root, color='red', linestyle='--', linewidth=0.8)
            except Exception:
                self.ax.axvline(root, color='red', linestyle='--', linewidth=0.8)
        self.ax.set_xlim(a, b)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.legend()
        self.ax.grid(True, linestyle=':', linewidth=0.6)
        self.canvas.draw()

    def on_export_csv(self):
        if not self.last_rows:
            messagebox.showinfo('Info', 'No hay datos para exportar')
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path:
            return
        df = pd.DataFrame(self.last_rows)
        df.to_csv(path, index=False)
        messagebox.showinfo('Éxito', f'Tabla exportada a {path}')


if __name__ == '__main__':
    root = ttkb.Window(themename='cosmo')
    app = FalsaPosicionGUI(root)
    root.mainloop()
