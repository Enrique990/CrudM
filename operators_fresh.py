import tkinter as tk
from tkinter import ttk, messagebox
import matrices


def _format_matrix_for_display(matrix):
    if not matrix or not any(matrix):
        return ""
    str_rows = [[str(cell) for cell in row] for row in matrix]
    col_widths = [max(len(row[c]) for row in str_rows) for c in range(len(str_rows[0]))]
    lines = []
    for row in str_rows:
        padded = [cell.rjust(col_widths[i]) for i, cell in enumerate(row)]
        lines.append("[ " + "  ".join(padded) + " ]")
    return "\n".join(lines)


class MatrixPanel:
    """Panel individual con cuadrícula y operaciones básicas."""

    def __init__(self, parent, title, on_result):
        self.on_result = on_result
        self.title = title
        self.frame = ttk.LabelFrame(parent, text=title, padding=8)
        self.rows_var = tk.IntVar(value=3)
        self.cols_var = tk.IntVar(value=3)
        self.scalar_var = tk.DoubleVar(value=1.0)
        self.power_var = tk.IntVar(value=1)

        header = ttk.Frame(self.frame)
        header.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))
        ttk.Label(header, text="Filas:").pack(side=tk.LEFT, padx=(0, 4))
        tk.Spinbox(header, from_=1, to=10, width=4, textvariable=self.rows_var, command=self._rebuild).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(header, text="Columnas:").pack(side=tk.LEFT, padx=(0, 4))
        tk.Spinbox(header, from_=1, to=10, width=4, textvariable=self.cols_var, command=self._rebuild).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(header, text="+", width=2, command=self._inc_cols).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(header, text="-", width=2, command=self._dec_cols).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(header, text="+ fila", width=6, command=self._inc_rows).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(header, text="- fila", width=6, command=self._dec_rows).pack(side=tk.RIGHT, padx=(6, 0))

        self.grid_frame = ttk.Frame(self.frame)
        self.grid_frame.grid(row=1, column=0, columnspan=4, sticky="w")
        self.entries = []
        self._rebuild()

        ops = ttk.Frame(self.frame)
        ops.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Button(ops, text="Determinante", command=self._det).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(ops, text="Inversa", command=self._inv).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(ops, text="Transpuesta", command=self._transpose).grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        ttk.Button(ops, text="Multiplicar por", command=self._scale).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        tk.Spinbox(ops, from_=-50, to=50, increment=0.5, width=6, textvariable=self.scalar_var).grid(row=1, column=1, sticky="w", padx=2, pady=2)
        ttk.Label(ops, text="Elevada a").grid(row=1, column=2, sticky="ew", padx=2, pady=2)
        tk.Spinbox(ops, from_=-5, to=8, width=4, textvariable=self.power_var, state="readonly").grid(row=1, column=3, sticky="w", padx=2, pady=2)
        ttk.Button(ops, text="Independencia", command=self._independence).grid(row=2, column=0, columnspan=4, sticky="ew", padx=2, pady=(6, 2))

    # --- layout helpers ---
    def _inc_rows(self):
        self.rows_var.set(self.rows_var.get() + 1)
        self._rebuild()

    def _dec_rows(self):
        self.rows_var.set(max(1, self.rows_var.get() - 1))
        self._rebuild()

    def _inc_cols(self):
        self.cols_var.set(self.cols_var.get() + 1)
        self._rebuild()

    def _dec_cols(self):
        self.cols_var.set(max(1, self.cols_var.get() - 1))
        self._rebuild()

    def _rebuild(self):
        rows = max(1, int(self.rows_var.get()))
        cols = max(1, int(self.cols_var.get()))
        prev = [[e.get() for e in row] for row in self.entries]
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.entries = []
        for i in range(rows):
            row_entries = []
            for j in range(cols):
                e = ttk.Entry(self.grid_frame, width=8)
                default = prev[i][j] if i < len(prev) and j < len(prev[i]) else "0"
                e.insert(0, default)
                e.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(e)
            self.entries.append(row_entries)

    # --- data helpers ---
    def get_matrix(self):
        matrix = []
        for row in self.entries:
            vals = []
            for e in row:
                vals.append(float(e.get()))
            matrix.append(vals)
        return matrix

    def get_effective_matrix(self):
        """Aplica factor y potencia configurados antes de devolver la matriz."""
        base = matrices.Matriz(self.get_matrix())
        factor = float(self.scalar_var.get())
        power = int(self.power_var.get())
        mat = base
        if factor != 1:
            mat = mat.multiplicar(factor)
        if power != 1:
            mat = mat.potencia(power)
        return mat.to_list()

    def set_matrix(self, data):
        if not data:
            return
        r, c = len(data), len(data[0])
        self.rows_var.set(r)
        self.cols_var.set(c)
        self._rebuild()
        for i in range(min(r, len(self.entries))):
            for j in range(min(c, len(self.entries[i]))):
                try:
                    self.entries[i][j].delete(0, tk.END)
                    self.entries[i][j].insert(0, str(data[i][j]))
                except Exception:
                    pass

    # --- operaciones individuales con pasos ---
    def _det(self):
        try:
            mat = self.get_matrix()
            det_res = matrices.determinante_por_gauss_con_pasos(mat, mostrar_pasos=True)
            res = det_res.get("determinante")
            pasos = [str(p) for p in det_res.get("pasos", [])]
            self.on_result(f"Determinante ({len(mat)}x{len(mat[0])}): {res}", None, pasos or ["Procedimiento de Gauss no devuelto."])
        except Exception as e:
            messagebox.showerror("Determinante", str(e))

    def _inv(self):
        try:
            mat = matrices.Matriz(self.get_matrix())
            inv_res = mat.inversa(mostrar_pasos=True)
            pasos = inv_res.get("pasos", [])
            matriz_inv = inv_res.get("inversa")
            if matriz_inv is None:
                self.on_result(inv_res.get("mensaje", "No hay inversa."), None, pasos or ["No hay pasos disponibles."])
                return
            matriz_lista = matriz_inv if isinstance(matriz_inv, list) else (matriz_inv.to_list() if hasattr(matriz_inv, "to_list") else None)
            self.on_result(f"Inversa de {mat.n}x{mat.m}", matriz_lista, pasos or ["Gauss-Jordan sobre [A|I]."])
        except Exception as e:
            messagebox.showerror("Inversa", str(e))

    def _transpose(self):
        try:
            base = self.get_matrix()
            mat = matrices.Matriz(base).trasponer()
            pasos = [f"t[{j+1},{i+1}] = a[{i+1},{j+1}] = {base[i][j]}" for i in range(len(base)) for j in range(len(base[0]))]
            self.on_result("Transpuesta", mat.to_list(), pasos)
        except Exception as e:
            messagebox.showerror("Transpuesta", str(e))

    def _scale(self):
        try:
            factor = float(self.scalar_var.get())
            base = self.get_matrix()
            mat = matrices.Matriz(base).multiplicar(factor).to_list()
            pasos = [f"r[{i+1},{j+1}] = {base[i][j]} * {factor} = {base[i][j]*factor}" for i in range(len(base)) for j in range(len(base[0]))]
            self.on_result(f"Matriz x {factor}", mat, pasos)
        except Exception as e:
            messagebox.showerror("Escalar", str(e))

    def _independence(self):
        try:
            mat = matrices.Matriz(self.get_matrix())
            res = mat.independencia_vectores(mat.to_list())
            msg = res.get("mensaje", "Resultado de independencia")
            detalle = ""
            if "solucion" in res:
                sol = res["solucion"]
                detalle = f"\nRango: {sol.get('rango')} | Independiente: {sol.get('independiente')}"
                if sol.get("libres"):
                    detalle += f" | Columnas libres: {sol.get('libres')}"
            pasos = []
            for p in res.get("pasos", []):
                if isinstance(p, dict) and "descripcion" in p:
                    pasos.append(p["descripcion"])
                    if "matriz" in p:
                        pasos.append(_format_matrix_for_display(p["matriz"]))
                else:
                    pasos.append(str(p))
            self.on_result(f"{msg}{detalle}", None, pasos or ["Sin pasos detallados."])
        except Exception as e:
            messagebox.showerror("Independencia", str(e))


class DualOperatorsWindow:
    """Ventana principal con dos paneles visibles y soporte para N matrices."""

    def __init__(self, master):
        self.master = master
        self.top = tk.Toplevel(master)
        self.top.title("Operador de matrices (dual)")
        self.top.geometry("1200x720")

        root = ttk.Frame(self.top, padding=10)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=0)
        root.columnconfigure(2, weight=1)

        # Toolbar
        toolbar = ttk.Frame(root)
        toolbar.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ttk.Button(toolbar, text="Agregar matriz", command=self._add_panel).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(toolbar, text="Operar:").pack(side=tk.LEFT, padx=(0, 4))
        self.sel_left = tk.StringVar()
        self.sel_right = tk.StringVar()
        self.combo_left = ttk.Combobox(toolbar, width=12, textvariable=self.sel_left, state="readonly")
        self.combo_right = ttk.Combobox(toolbar, width=12, textvariable=self.sel_right, state="readonly")
        self.combo_left.pack(side=tk.LEFT, padx=(0, 6))
        self.combo_right.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="×", width=4, command=self._mul_ab).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="+", width=4, command=self._add_ab).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="A-B", width=5, command=self._sub_ab).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="B-A", width=5, command=self._sub_ba).pack(side=tk.LEFT, padx=2)
        self.save_btn = ttk.Button(toolbar, text="Guardar resultado como matriz", command=self._save_result_as_panel, state="disabled")
        self.save_btn.pack(side=tk.LEFT, padx=(12, 0))

        # Lista de matrices para operaciones con más de 2
        listbox_frame = ttk.Frame(root)
        listbox_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ttk.Label(listbox_frame, text="Selecciona matrices (orden para × y -):").pack(anchor="w")
        self.selection_list = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED, height=4, exportselection=False)
        self.selection_list.pack(fill=tk.X, pady=4)
        multibar = ttk.Frame(listbox_frame)
        multibar.pack(anchor="w", pady=2)
        ttk.Button(multibar, text="Σ Seleccion", command=self._sum_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(multibar, text="Restar secuencia", command=self._sub_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(multibar, text="Multiplicar secuencia", command=self._mul_selected).pack(side=tk.LEFT, padx=2)

        left = ttk.Frame(root)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        right = ttk.Frame(root)
        right.grid(row=1, column=2, sticky="nsew", padx=(16, 0))

        self.panels = []
        self._container_left = left
        self._container_right = right
        self.last_result_matrix = None
        self._add_panel()
        self._add_panel()

        result_area = ttk.Frame(root)
        result_area.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(16, 0))
        result_area.columnconfigure(0, weight=1)
        result_area.columnconfigure(1, weight=1)
        result_area.rowconfigure(0, weight=1)

        result_box = ttk.LabelFrame(result_area, text="Resultado", padding=8)
        result_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        result_box.columnconfigure(0, weight=1)
        result_box.rowconfigure(0, weight=1)
        self.result_text = tk.Text(result_box, height=10, wrap="word")
        self.result_text.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(result_box, command=self.result_text.yview).grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=self.result_text.yview)

        steps_box = ttk.LabelFrame(result_area, text="Pasos", padding=8)
        steps_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        steps_box.columnconfigure(0, weight=1)
        steps_box.rowconfigure(0, weight=1)
        self.steps_text = tk.Text(steps_box, height=10, wrap="word")
        self.steps_text.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(steps_box, command=self.steps_text.yview).grid(row=0, column=1, sticky="ns")
        self.steps_text.configure(yscrollcommand=self.steps_text.yview)

        root.rowconfigure(2, weight=1)

    def _add_panel(self):
        name = chr(ord("A") + len(self.panels))
        parent = self._container_left if len(self.panels) % 2 == 0 else self._container_right
        panel = MatrixPanel(parent, f"Matriz {name}", self._show_result)
        panel.frame.pack(anchor="n", fill=tk.X, pady=4)
        self.panels.append(panel)
        self._refresh_selectors()

    def _refresh_selectors(self):
        names = [f"Matriz {chr(ord('A') + idx)}" for idx in range(len(self.panels))]
        self.combo_left["values"] = names
        self.combo_right["values"] = names
        if not self.sel_left.get() and names:
            self.sel_left.set(names[0])
        if len(names) > 1 and not self.sel_right.get():
            self.sel_right.set(names[1])
        self.selection_list.delete(0, tk.END)
        for name in names:
            self.selection_list.insert(tk.END, name)

    # ---- binary operations ----
    def _add_ab(self):
        try:
            A, B, names = self._get_selected_two(return_names=True)
            res, pasos = self._sum_matrices([A, B], names, "A + B")
            self._show_result("A + B", res, pasos)
        except Exception as e:
            messagebox.showerror("Suma", str(e))

    def _sub_ab(self):
        try:
            A, B, names = self._get_selected_two(return_names=True)
            res, pasos = self._sum_matrices([A, matrices.Matriz(B).multiplicar(-1).to_list()], [names[0], f"-{names[1]}"], "A - B")
            self._show_result("A - B", res, pasos)
        except Exception as e:
            messagebox.showerror("Resta", str(e))

    def _sub_ba(self):
        try:
            B, A, names = self._get_selected_two(return_names=True)
            res, pasos = self._sum_matrices([B, matrices.Matriz(A).multiplicar(-1).to_list()], [names[0], f"-{names[1]}"], "B - A")
            self._show_result("B - A", res, pasos)
        except Exception as e:
            messagebox.showerror("Resta", str(e))

    def _mul_ab(self):
        try:
            A, B, names = self._get_selected_two(return_names=True)
            res, pasos = self._dot_with_steps(A, B, f"{names[0]} × {names[1]}")
            self._show_result("A × B", res, pasos)
        except Exception as e:
            messagebox.showerror("Producto", str(e))

    def _mul_ba(self):
        try:
            B, A, names = self._get_selected_two(return_names=True)
            res, pasos = self._dot_with_steps(B, A, f"{names[0]} × {names[1]}")
            self._show_result("B × A", res, pasos)
        except Exception as e:
            messagebox.showerror("Producto", str(e))

    def _get_selected_two(self, return_names=False):
        names = [f"Matriz {chr(ord('A') + idx)}" for idx in range(len(self.panels))]
        if not names:
            raise ValueError("Agrega matrices primero.")
        try:
            i = names.index(self.sel_left.get())
            j = names.index(self.sel_right.get())
        except ValueError:
            raise ValueError("Selecciona dos matrices.")
        if i == j:
            raise ValueError("Elige dos matrices distintas para operar.")
        mats = (self.panels[i].get_effective_matrix(), self.panels[j].get_effective_matrix())
        return (*mats, [names[i], names[j]]) if return_names else mats

    def _selected_indices(self):
        sel = list(self.selection_list.curselection())
        if not sel:
            raise ValueError("Selecciona al menos una matriz en la lista.")
        return sel

    def _sum_selected(self):
        try:
            idxs = self._selected_indices()
            mats = [self.panels[i].get_effective_matrix() for i in idxs]
            names = [self.selection_list.get(i) for i in idxs]
            res, pasos = self._sum_matrices(mats, names, "Suma de selección")
            self._show_result("Suma de selección", res, pasos)
        except Exception as e:
            messagebox.showerror("Suma", str(e))

    def _sub_selected(self):
        try:
            idxs = self._selected_indices()
            if len(idxs) < 2:
                raise ValueError("Selecciona 2 o más matrices para restar secuencialmente.")
            mats = [self.panels[i].get_effective_matrix() for i in idxs]
            names = [self.selection_list.get(i) for i in idxs]
            pasos = [f"Inicio con {names[0]}"]
            res = matrices.Matriz(mats[0])
            for name, m in zip(names[1:], mats[1:]):
                pasos.append(f"Resta {name}")
                res = res.restar(matrices.Matriz(m))
            pasos.append("Resultado final listo.")
            self._show_result("Resta secuencial", res.to_list(), pasos)
        except Exception as e:
            messagebox.showerror("Resta", str(e))

    def _mul_selected(self):
        try:
            idxs = self._selected_indices()
            if len(idxs) < 2:
                raise ValueError("Selecciona 2 o más matrices para multiplicar.")
            mats = [self.panels[i].get_effective_matrix() for i in idxs]
            names = [self.selection_list.get(i) for i in idxs]
            pasos_all = []
            res = mats[0]
            for idx in range(1, len(mats)):
                res, pasos = self._dot_with_steps(res, mats[idx], f"{names[idx-1]} × {names[idx]}")
                pasos_all.extend(pasos)
            pasos_all.append("Producto secuencial completo.")
            self._show_result("Producto secuencial", res, pasos_all)
        except Exception as e:
            messagebox.showerror("Producto", str(e))

    # ---- salida ----
    def _show_result(self, text, matrix=None, steps=None):
        if matrix is not None:
            self.last_result_matrix = matrix
            self.save_btn.config(state="normal")
            render = f"{text}:\n{_format_matrix_for_display(matrix)}"
        else:
            self.last_result_matrix = None
            self.save_btn.config(state="disabled")
            render = text
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, render)
        self.steps_text.delete("1.0", tk.END)
        if steps:
            if isinstance(steps, list):
                self.steps_text.insert(tk.END, "\n".join(steps))
            else:
                self.steps_text.insert(tk.END, str(steps))
        else:
            self.steps_text.insert(tk.END, "Procedimiento no disponible para esta operación.")

    # ---- helpers ----
    def _dot_with_steps(self, A, B, etiqueta):
        if not A or not B:
            raise ValueError("Matrices vacías.")
        if len(A[0]) != len(B):
            raise ValueError(f"Dimensiones incompatibles: {len(A)}x{len(A[0])} con {len(B)}x{len(B[0])}")
        n, k, p = len(A), len(B), len(B[0])
        out = [[0.0 for _ in range(p)] for _ in range(n)]
        pasos = [f"{etiqueta}: {n}x{k} · {k}x{p}"]
        for i in range(n):
            for j in range(p):
                terms = [f"{A[i][t]}*{B[t][j]}" for t in range(k)]
                val = sum(A[i][t] * B[t][j] for t in range(k))
                out[i][j] = val
                pasos.append(f"r[{i+1},{j+1}] = " + " + ".join(terms) + f" = {val}")
        return out, pasos

    def _sum_matrices(self, mats, names, title):
        if not mats:
            raise ValueError("No hay matrices seleccionadas.")
        r, c = len(mats[0]), len(mats[0][0])
        for m in mats:
            if len(m) != r or len(m[0]) != c:
                raise ValueError("Todas las matrices deben tener el mismo tamaño para sumar/restar.")
        pasos = [f"{title} ({r}x{c})"]
        for name, m in zip(names, mats):
            pasos.append(f"{name}:")
            pasos.append(_format_matrix_for_display(m))
        res = [[0.0 for _ in range(c)] for _ in range(r)]
        for i in range(r):
            for j in range(c):
                terms = []
                for idx, m in enumerate(mats):
                    label = names[idx] if idx < len(names) else f"M{idx+1}"
                    terms.append(f"{label}[{i+1},{j+1}]={m[i][j]}")
                    res[i][j] += m[i][j]
                pasos.append(f"r[{i+1},{j+1}] = " + " + ".join(terms) + f" = {res[i][j]}")
        return res, pasos

    def _save_result_as_panel(self):
        if not self.last_result_matrix:
            messagebox.showwarning("Resultado", "No hay matriz resultante para guardar.")
            return
        self._add_panel()
        self.panels[-1].set_matrix(self.last_result_matrix)


def launch_new_operator_window(root):
    return DualOperatorsWindow(root)
