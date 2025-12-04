import tkinter as tk
from tkinter import ttk, messagebox
import matrices
import persistencia


def _default_palette():
    """Paleta por defecto (alineada con la calculadora principal)."""
    return {
        "background": "#0b1220",
        "panel": "#0f172a",
        "card": "#111d2f",
        "card_alt": "#0d1626",
        "accent": "#e9c46a",
        "accent_soft": "#8bd3dd",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "input": "#0d1828",
        "outline": "#1f2a3c",
    }


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
    """Panel individual con cuadrÃ­cula y operaciones bÃ¡sicas."""

    def __init__(self, parent, title, on_result, styles=None, palette=None, fonts=None):
        self.on_result = on_result
        self.title = title
        self.styles = styles or {}
        self.palette = palette or _default_palette()
        self.fonts = fonts or {}
        self.frame = ttk.LabelFrame(parent, text=title, padding=8, style=self.styles.get("labelframe", ""))
        self.rows_var = tk.IntVar(value=3)
        self.cols_var = tk.IntVar(value=3)
        self.scalar_var = tk.DoubleVar(value=1.0)
        self.power_var = tk.IntVar(value=1)  # fija (sin UI) para evitar ruido

        header = ttk.Frame(self.frame, style=self.styles.get("card", ""))
        header.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))
        ttk.Label(header, text="Filas:", style=self.styles.get("label", "")).pack(side=tk.LEFT, padx=(0, 4))
        tk.Spinbox(
            header,
            from_=1,
            to=10,
            width=4,
            textvariable=self.rows_var,
            command=self._rebuild,
            bg=self.palette["input"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            disabledbackground=self.palette["panel"],
            highlightbackground=self.palette["outline"],
        ).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(header, text="Columnas:", style=self.styles.get("label", "")).pack(side=tk.LEFT, padx=(0, 4))
        tk.Spinbox(
            header,
            from_=1,
            to=10,
            width=4,
            textvariable=self.cols_var,
            command=self._rebuild,
            bg=self.palette["input"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            disabledbackground=self.palette["panel"],
            highlightbackground=self.palette["outline"],
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.grid_frame = ttk.Frame(self.frame, style=self.styles.get("card", ""))
        self.grid_frame.grid(row=1, column=0, columnspan=4, sticky="w")
        self.entries = []
        self._rebuild()

        ops = ttk.Frame(self.frame, style=self.styles.get("card", ""))
        ops.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Button(ops, text="Determinante", command=self._det, style=self.styles.get("button", "")).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(ops, text="Inversa", command=self._inv, style=self.styles.get("button", "")).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(ops, text="Transpuesta", command=self._transpose, style=self.styles.get("button", "")).grid(row=0, column=2, sticky="ew", padx=2, pady=2)
        ttk.Button(ops, text="Multiplicar por", command=self._scale, style=self.styles.get("button", "")).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        tk.Spinbox(
            ops,
            from_=-50,
            to=50,
            increment=0.5,
            width=6,
            textvariable=self.scalar_var,
            bg=self.palette["input"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            disabledbackground=self.palette["panel"],
            highlightbackground=self.palette["outline"],
        ).grid(row=1, column=1, sticky="w", padx=2, pady=2)
        ttk.Button(ops, text="Independencia", command=self._independence, style=self.styles.get("button", "")).grid(row=2, column=0, columnspan=3, sticky="ew", padx=2, pady=(6, 2))

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
                e = ttk.Entry(self.grid_frame, width=8, style=self.styles.get("entry", ""))
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

    def __init__(self, master, palette=None, fonts=None, styles=None, as_toplevel=True):
        self.master = master
        self.palette = palette or _default_palette()
        self.fonts = fonts or {
            "body": ("Segoe UI", 11),
            "label": ("Segoe UI Semibold", 11),
            "title": ("Segoe UI Semibold", 16),
            "mono": ("Consolas", 12),
        }
        self.styles = styles or self._build_styles()
        self.as_toplevel = as_toplevel

        if as_toplevel:
            self.container = tk.Toplevel(master)
            self.container.title("Operador de matrices (dual)")
            self.container.geometry("1200x720")
            parent_for_root = self.container
        else:
            self.container = ttk.Frame(master, style=self.styles.get("surface", ""))
            parent_for_root = self.container

        # Contenedor con scroll para evitar cortes en pantallas pequeÃ±as
        scroll_wrap = ttk.Frame(parent_for_root, style=self.styles.get("surface", ""))
        scroll_wrap.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(scroll_wrap, bg=self.palette["panel"], highlightthickness=0, bd=0)
        vscroll = ttk.Scrollbar(scroll_wrap, orient=tk.VERTICAL, command=self.canvas.yview, style=self.styles.get("scrollbar", ""))
        self.canvas.configure(yscrollcommand=vscroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        root = ttk.Frame(self.canvas, padding=8, style=self.styles.get("surface", ""))
        self.canvas_window = self.canvas.create_window((0, 0), window=root, anchor="nw")
        root.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        self._bind_global_scroll()
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        root.rowconfigure(0, weight=1)
        content = ttk.Frame(root, style=self.styles.get("surface", ""))
        content.grid(row=0, column=0, columnspan=2, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left_column = ttk.Frame(content, style=self.styles.get("surface", ""))
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left_column.columnconfigure(0, weight=1)
        left_column.rowconfigure(0, weight=0)
        left_column.rowconfigure(1, weight=1)

        # Cabecera, controles y bandeja a la izquierda
        top_card = ttk.Frame(left_column, style=self.styles.get("card", ""), padding=10)
        top_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_card.columnconfigure(0, weight=1)
        top_card.columnconfigure(1, weight=1)

        header = ttk.Frame(top_card, style=self.styles.get("card", ""))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(header, text="Operador avanzado", style=self.styles.get("title", "")).pack(anchor="w")
        ttk.Label(header, text="Opera matrices, guarda resultados y observa el procedimiento paso a paso.", style=self.styles.get("muted", "")).pack(anchor="w", pady=(2, 0))

        controls = ttk.Frame(top_card, style=self.styles.get("card", ""))
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        primary_row = ttk.Frame(controls, style=self.styles.get("card", ""))
        primary_row.grid(row=0, column=0, sticky="w")
        ttk.Button(primary_row, text="Nueva matriz", command=self._add_panel, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(primary_row, text="Operar:", style=self.styles.get("label", "")).pack(side=tk.LEFT, padx=(0, 6))
        self.sel_left = tk.StringVar()
        self.sel_right = tk.StringVar()
        self.combo_left = ttk.Combobox(primary_row, width=12, textvariable=self.sel_left, state="readonly", style=self.styles.get("combo", ""))
        self.combo_right = ttk.Combobox(primary_row, width=12, textvariable=self.sel_right, state="readonly", style=self.styles.get("combo", ""))
        self.combo_left.pack(side=tk.LEFT, padx=(0, 6))
        self.combo_right.pack(side=tk.LEFT, padx=(0, 10))

        ops_row = ttk.Frame(controls, style=self.styles.get("card", ""))
        ops_row.grid(row=0, column=1, sticky="e")
        ttk.Button(ops_row, text="A x B", width=7, command=self._mul_ab, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=3)
        ttk.Button(ops_row, text="A+B", width=7, command=self._add_ab, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=3)
        ttk.Button(ops_row, text="A-B", width=7, command=self._sub_ab, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=3)
        ttk.Button(ops_row, text="B-A", width=7, command=self._sub_ba, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=3)
        self.save_btn = ttk.Button(ops_row, text="Guardar resultado", command=self._save_result_as_panel, state="disabled", style=self.styles.get("button", ""))
        self.save_btn.pack(side=tk.LEFT, padx=(10, 0))

        listbox_card = ttk.Frame(top_card, style=self.styles.get("card", ""), padding=8)
        listbox_card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        listbox_card.columnconfigure(0, weight=1)
        top_bandeja = ttk.Frame(listbox_card, style=self.styles.get("card", ""))
        top_bandeja.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(top_bandeja, text="Bandeja de matrices (para sumar/restar/multiplicar en secuencia)", style=self.styles.get("label", "")).pack(side=tk.LEFT)
        actions = ttk.Frame(top_bandeja, style=self.styles.get("card", ""))
        actions.pack(side=tk.RIGHT)
        ttk.Button(actions, text="Sumar seleccion", command=self._sum_selected, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(actions, text="Restar secuencia", command=self._sub_selected, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Multiplicar secuencia", command=self._mul_selected, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Eliminar seleccion", command=self._delete_selected_panels, style=self.styles.get("button", "")).pack(side=tk.LEFT, padx=(8,0))

        self.selection_list = tk.Listbox(
            listbox_card,
            selectmode=tk.EXTENDED,
            height=4,
            exportselection=False,
            bg=self.palette["card"],
            fg=self.palette["text"],
            selectbackground=self.palette["accent"],
            selectforeground=self.palette["background"],
            highlightthickness=0,
            borderwidth=0,
            relief="flat",
        )
        self.selection_list.grid(row=1, column=0, sticky="ew")

        panels_wrapper = ttk.Frame(left_column, style=self.styles.get("surface", ""))
        panels_wrapper.grid(row=1, column=0, sticky="nsew")
        panels_wrapper.rowconfigure(0, weight=1)
        panels_wrapper.columnconfigure(0, weight=1)
        panels_canvas = tk.Canvas(panels_wrapper, bg=self.palette["panel"], highlightthickness=0, bd=0)
        panels_scroll = ttk.Scrollbar(panels_wrapper, orient=tk.VERTICAL, command=panels_canvas.yview, style=self.styles.get("scrollbar", ""))
        panels_canvas.configure(yscrollcommand=panels_scroll.set)
        panels_canvas.grid(row=0, column=0, sticky="nsew")
        panels_scroll.grid(row=0, column=1, sticky="ns")
        self.panels_container = ttk.Frame(panels_canvas, style=self.styles.get("surface", ""))
        self.panels_window = panels_canvas.create_window((0, 0), window=self.panels_container, anchor="nw")
        self.panels_container.bind("<Configure>", lambda e: panels_canvas.configure(scrollregion=panels_canvas.bbox("all")))
        panels_canvas.bind("<Configure>", lambda e: panels_canvas.itemconfigure(self.panels_window, width=e.width))
        self.panels_container.columnconfigure(0, weight=1)
        self._container_left = self.panels_container  # pila vertical
        self._container_right = self.panels_container

        self.panels = []
        self.last_result_matrix = None
        self._add_panel()
        self._add_panel()

        right_column = ttk.Frame(content, style=self.styles.get("surface", ""))
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.columnconfigure(0, weight=1)
        # Dar m��s espacio vertical a los pasos que al resultado
        right_column.rowconfigure(0, weight=1, minsize=40)
        right_column.rowconfigure(1, weight=5)

        right_res = ttk.LabelFrame(right_column, text="Resultado", padding=10, style=self.styles.get("labelframe", ""))
        right_res.grid(row=0, column=0, sticky="nsew")
        right_res.columnconfigure(0, weight=1)
        right_res.rowconfigure(1, weight=1)
        ttk.Label(right_res, text="Matriz resultante", style=self.styles.get("label", "")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.result_text = tk.Text(
            right_res,
            wrap="word",
            bg=self.palette["card_alt"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            bd=0,
            highlightthickness=0,
            font=self.fonts.get("mono", ("Consolas", 12)),
        )
        self.result_text.grid(row=1, column=0, sticky="nsew")
        ttk.Scrollbar(right_res, command=self.result_text.yview, style=self.styles.get("scrollbar", "")).grid(row=1, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=self.result_text.yview)

        right_steps = ttk.LabelFrame(right_column, text="Pasos", padding=10, style=self.styles.get("labelframe", ""))
        right_steps.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        right_steps.columnconfigure(0, weight=1)
        right_steps.rowconfigure(1, weight=1)
        ttk.Label(right_steps, text="Procedimiento detallado", style=self.styles.get("label", "")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.steps_text = tk.Text(
            right_steps,
            wrap="word",
            bg=self.palette["card_alt"],
            fg=self.palette["text"],
            insertbackground=self.palette["text"],
            bd=0,
            highlightthickness=0,
            font=self.fonts.get("mono", ("Consolas", 12)),
        )
        self.steps_text.grid(row=1, column=0, sticky="nsew")
        ttk.Scrollbar(right_steps, command=self.steps_text.yview, style=self.styles.get("scrollbar", "")).grid(row=1, column=1, sticky="ns")
        self.steps_text.configure(yscrollcommand=self.steps_text.yview)

    def _build_styles(self):
        """Define estilos locales coherentes con la app principal."""
        style = ttk.Style(self.master)
        p = self.palette
        styles = {
            "surface": "Ops.Surface.TFrame",
            "card": "Ops.Card.TFrame",
            "labelframe": "Ops.Card.TLabelframe",
            "label": "Ops.TLabel",
            "muted": "Ops.Muted.TLabel",
            "title": "Ops.Title.TLabel",
            "cardtitle": "Ops.CardTitle.TLabel",
            "button": "Ops.Button.TButton",
            "combo": "Ops.TCombobox",
            "entry": "Ops.Entry.TEntry",
            "scrollbar": "Ops.Vertical.TScrollbar",
        }
        style.configure(styles["surface"], background=p["panel"])
        style.configure(styles["card"], background=p["card"])
        style.configure(styles["labelframe"], background=p["card"], foreground=p["accent"], borderwidth=0, relief="flat", padding=4)
        style.configure(styles["labelframe"] + ".Label", background=p["card"], foreground=p["accent"], font=self.fonts.get("label"))
        style.configure(styles["label"], background=p["panel"], foreground=p["text"], font=self.fonts.get("body"))
        style.configure(styles["muted"], background=p["panel"], foreground=p["muted"], font=self.fonts.get("body"))
        style.configure(styles["title"], background=p["panel"], foreground=p["accent"], font=self.fonts.get("title"))
        style.configure(styles["cardtitle"], background=p["card"], foreground=p["accent"], font=self.fonts.get("title"))
        style.configure(styles["button"], background=p["card"], foreground=p["text"], font=self.fonts.get("label"), borderwidth=0, padding=(10, 6))
        style.map(styles["button"], background=[("active", p["accent"])], foreground=[("active", p["background"])])
        style.configure(styles["combo"], fieldbackground=p["input"], background=p["input"], foreground=p["text"])
        style.configure(styles["entry"], fieldbackground=p["input"], background=p["input"], foreground=p["text"])
        # Scrollbar discreta (casi invisible) para integrarse al panel
        style.configure(styles["scrollbar"], troughcolor=p["panel"], background=p["panel"], bordercolor=p["panel"], arrowcolor=p["panel"])
        style.map(styles["scrollbar"], background=[("active", p["panel"])], arrowcolor=[("active", p["panel"])])
        return styles

    def _add_panel(self):
        name = chr(ord("A") + len(self.panels))
        parent = self._container_left if len(self.panels) % 2 == 0 else self._container_right
        panel = MatrixPanel(parent, f"Matriz {name}", self._show_result, styles=self.styles, palette=self.palette, fonts=self.fonts)
        panel.frame.pack(anchor="n", fill=tk.X, pady=4)
        self.panels.append(panel)
        self._refresh_selectors()
        return panel

    def _bind_global_scroll(self):
        """Permite hacer scroll con rueda desde cualquier zona."""
        def _on_mousewheel(event):
            num = getattr(event, "num", None)
            if num in (4, 5):  # Linux buttons
                delta = -1 if num == 4 else 1
            else:
                try:
                    delta = -1 if event.delta > 0 else 1
                except Exception:
                    delta = 0
            if delta:
                self.canvas.yview_scroll(delta, "units")
            return "break"

        top = self.master.winfo_toplevel()
        top.bind_all("<MouseWheel>", _on_mousewheel, add="+")
        top.bind_all("<Button-4>", _on_mousewheel, add="+")
        top.bind_all("<Button-5>", _on_mousewheel, add="+")
        # Asegurar que el canvas tenga el foco al entrar en cualquier zona
        for widget in (self.canvas, self.container, top):
            try:
                widget.bind("<Enter>", lambda e: self.canvas.focus_set(), add="+")
            except Exception:
                pass

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
            res, pasos = self._dot_with_steps(A, B, f"{names[0]} x {names[1]}")
            self._show_result("A x B", res, pasos)
        except Exception as e:
            messagebox.showerror("Producto", str(e))

    def _mul_ba(self):
        try:
            B, A, names = self._get_selected_two(return_names=True)
            res, pasos = self._dot_with_steps(B, A, f"{names[0]} x {names[1]}")
            self._show_result("B x A", res, pasos)
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
            res, pasos = self._sum_matrices(mats, names, "Suma de selecciÃ³n")
            self._show_result("Suma de selecciÃ³n", res, pasos)
        except Exception as e:
            messagebox.showerror("Suma", str(e))

    def _sub_selected(self):
        try:
            idxs = self._selected_indices()
            if len(idxs) < 2:
                raise ValueError("Selecciona 2 o mÃ¡s matrices para restar secuencialmente.")
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
                raise ValueError("Selecciona 2 o mÃ¡s matrices para multiplicar.")
            mats = [self.panels[i].get_effective_matrix() for i in idxs]
            names = [self.selection_list.get(i) for i in idxs]
            pasos_all = []
            res = mats[0]
            for idx in range(1, len(mats)):
                res, pasos = self._dot_with_steps(res, mats[idx], f"{names[idx-1]} x {names[idx]}")
                pasos_all.extend(pasos)
            pasos_all.append("Producto secuencial completo.")
            self._show_result("Producto secuencial", res, pasos_all)
        except Exception as e:
            messagebox.showerror("Producto", str(e))

    def _delete_selected_panels(self):
        """Elimina las matrices seleccionadas de la bandeja y renumera las restantes."""
        try:
            idxs = sorted(self._selected_indices(), reverse=True)
        except Exception as e:
            messagebox.showwarning("Eliminar", str(e))
            return
        for idx in idxs:
            try:
                panel = self.panels.pop(idx)
                panel.frame.destroy()
            except Exception:
                pass
        self._renumber_panels()
        self._refresh_selectors()

    def _renumber_panels(self):
        """Actualiza los nombres visibles tras eliminar/agregar."""
        for idx, panel in enumerate(self.panels):
            new_name = f"Matriz {chr(ord('A') + idx)}"
            try:
                panel.title = new_name
                panel.frame.configure(text=new_name)
            except Exception:
                pass

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
                rendered = []
                for item in steps:
                    if isinstance(item, dict):
                        if "descripcion" in item:
                            rendered.append(str(item["descripcion"]))
                        if "matriz" in item:
                            rendered.append(_format_matrix_for_display(item["matriz"]))
                        if not item:
                            rendered.append("{}")
                    else:
                        rendered.append(str(item))
                self.steps_text.insert(tk.END, "\n".join(rendered))
            else:
                self.steps_text.insert(tk.END, str(steps))
        else:
            self.steps_text.insert(tk.END, "Procedimiento no disponible para esta operaciÃ³n.")

    # ---- helpers ----
    def _dot_with_steps(self, A, B, etiqueta):
        if not A or not B:
            raise ValueError("Matrices vacÃ­as.")
        if len(A[0]) != len(B):
            raise ValueError(f"Dimensiones incompatibles: {len(A)}x{len(A[0])} con {len(B)}x{len(B[0])}")
        n, k, p = len(A), len(B), len(B[0])
        out = [[0.0 for _ in range(p)] for _ in range(n)]
        pasos = [f"{etiqueta}: {n}x{k} x {k}x{p}"]
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
                raise ValueError("Todas las matrices deben tener el mismo tamaÃ±o para sumar/restar.")
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
        panel = self._add_panel()
        panel.set_matrix(self.last_result_matrix)
        self._persist_result_matrix(self.last_result_matrix)

    def _persist_result_matrix(self, matrix_data):
        """Guarda la matriz resultante en almacenamiento para reutilizarla en otras pestañas."""
        try:
            if not matrix_data:
                return
            todas = persistencia.cargar_todas_matrices()
            idx = 1
            name = f"OP{idx}"
            while name in todas:
                idx += 1
                name = f"OP{idx}"
            filas = len(matrix_data)
            cols = len(matrix_data[0]) if matrix_data and matrix_data[0] is not None else 0
            payload = {"nombre": name, "filas": filas, "columnas": cols, "datos": matrix_data}
            persistencia.guardar_matriz(name, payload)
        except Exception as e:
            messagebox.showwarning("Guardar matriz", f"No se pudo guardar la matriz en archivo: {e}")


def launch_new_operator_window(root):
    """Abrir el operador en una ventana aparte (modo anterior)."""
    return DualOperatorsWindow(root, as_toplevel=True)


def create_embedded_operator(parent, palette=None, fonts=None):
    """Crear el operador embebido en un contenedor existente."""
    return DualOperatorsWindow(parent, palette=palette, fonts=fonts, as_toplevel=False)

