import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
import math
import io
import base64
import re
from crud import (
    crear_matriz,
    actualizar_matriz,
    crear_conjunto_vectores,
    actualizar_conjunto_vectores,
    crear_conjunto_matrices,
    actualizar_conjunto_matrices,
)
import persistencia
import matrices
from metodo_biseccion import MetodoBiseccion

class MatrixCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Matrices")
        self.palette = {
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
        self.fonts = {
            "body": ("Segoe UI", 11),
            "label": ("Segoe UI Semibold", 11),
            "title": ("Segoe UI Semibold", 19),
            "hero": ("Segoe UI Semibold", 21),
            "mono": ("Consolas", 12),
        }
        self.root.configure(bg=self.palette["background"])
        # Ejecutar en pantalla completa (estilo Windows maximizado). Para modo kiosco se puede usar attributes('-fullscreen', True)
        try:
            self.root.state('zoomed')
        except Exception:
            # Fallback si no está disponible 'zoomed'
            self.root.attributes('-fullscreen', True)

        style = ttk.Style()
        style.theme_use('clam')
        # Estilo para el Notebook y sus pestañas
        accent = self.palette["accent"]
        muted = self.palette["muted"]
        text = self.palette["text"]
        card = self.palette["card"]
        panel = self.palette["panel"]
        bg = self.palette["background"]
        style.configure('TNotebook', background=bg, borderwidth=0)
        style.configure('TNotebook.Tab', background=panel, foreground=muted, padding=[16, 10], font=self.fonts["label"])
        style.map('TNotebook.Tab', background=[('selected', card), ('active', self.palette["card_alt"])], foreground=[('selected', text)])

        btn_opts = dict(background=card, foreground=text, font=self.fonts["label"], borderwidth=0, focusthickness=0, relief="flat")
        style.configure('Dark.TFrame', background=panel)
        style.configure('Surface.TFrame', background=bg)
        style.configure('Card.TFrame', background=card, relief='flat', borderwidth=0)
        style.configure('Dark.TLabel', background=panel, foreground=text, font=self.fonts["body"])
        style.configure('Muted.TLabel', background=panel, foreground=muted, font=self.fonts["body"])
        style.configure('Title.TLabel', background=panel, foreground=accent, font=self.fonts["title"])
        style.configure('Hero.TLabel', background=panel, foreground=text, font=self.fonts["hero"])
        style.configure('CardHero.TLabel', background=card, foreground=text, font=self.fonts["hero"])
        style.configure('CardTitle.TLabel', background=card, foreground=accent, font=self.fonts["title"])
        style.configure('CardMuted.TLabel', background=card, foreground=muted, font=self.fonts["body"])
        style.configure('Result.TLabel', background=panel, foreground=text, font=('Consolas', 13))
        style.configure('Dark.TButton', **btn_opts, padding=(14, 8))
        style.map('Dark.TButton', background=[('active', accent), ('pressed', accent)], foreground=[('active', bg), ('pressed', bg)])
        style.configure('Ghost.TButton', background=panel, foreground=text, font=self.fonts["body"], borderwidth=0, padding=(8, 6))
        style.map('Ghost.TButton', background=[('active', card)], foreground=[('active', text)])
        # Botones tipo pestaña para el teclado matemático
        style.configure('TabInactive.TButton', background=panel, foreground=text, font=self.fonts["body"], borderwidth=0, padding=(10, 6))
        style.map('TabInactive.TButton', background=[('active', card)], foreground=[('active', text)])
        style.configure('TabActive.TButton', background=accent, foreground=bg, font=self.fonts["body"], borderwidth=0, padding=(10, 6))
        style.map('TabActive.TButton', background=[('active', accent)], foreground=[('active', bg)])
        style.configure('Entry.TEntry', fieldbackground=self.palette["input"], foreground=text, font=self.fonts["body"])
        style.configure('MathEntry.TEntry', fieldbackground=self.palette["input"], foreground=text, font=('Consolas', 16))
        style.configure('TCombobox', fieldbackground=self.palette["input"], background=self.palette["input"], foreground=text)
        # Treeview elegante para tabla de pasos numéricos
        style.configure('Elegant.Treeview', background=card, fieldbackground=card, foreground=text, borderwidth=0, rowheight=26)
        style.configure('Elegant.Treeview.Heading', background=card, foreground=accent, font=self.fonts["label"])
        style.map('Elegant.Treeview', background=[('selected', self.palette["card_alt"])], foreground=[('selected', accent)])
        # Estilo invisible para scrollbars (mismo color que fondo, sin contraste)
        try:
            style.configure('Invisible.Vertical.TScrollbar', background=panel, troughcolor=panel, bordercolor=panel, arrowcolor=panel)
            style.map('Invisible.Vertical.TScrollbar', background=[('active', panel), ('!active', panel)], arrowcolor=[('active', panel)])
            # Layout vacío para ocultar por completo la apariencia
            style.layout('Invisible.Vertical.TScrollbar', [])
        except Exception:
            pass
        # Estilo visible y coherente para scrollbars de la app
        try:
            style.configure('App.Vertical.TScrollbar', troughcolor=self.palette['outline'], background=self.palette['accent_soft'])
        except Exception:
            pass
        # Estilo visible específico para la barra de Resultado en Calculadora
        try:
            style.configure('CalcVisible.Vertical.TScrollbar', troughcolor=self.palette['outline'], background=self.palette['accent_soft'])
        except Exception:
            pass

        # --- Creación del Notebook para manejar las pestañas ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- Pestaña 1: Operador avanzado (reemplaza operador clásico) ---
        self.operators_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.operators_tab, text='Operador avanzado')
        self.create_fresh_operator_widgets(self.operators_tab)

        # --- Pestaña 2: Solucionador Sistema de ecuaciones ---
        self.calculator_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.calculator_tab, text='Solucionador Sistema de ecuaciones')
        self.create_calculator_widgets(self.calculator_tab)

        # --- Pestaña 3: Independencia de Vectores (última) ---
        self.independence_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.independence_tab, text='Independencia de Vectores')
        self.create_independence_widgets(self.independence_tab)

        # --- Nueva Pestaña: Métodos numéricos ---
        self.numeric_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.numeric_tab, text='Métodos numéricos')
        self.create_numeric_widgets(self.numeric_tab)

        # Estado para la pestaña de métodos numéricos
        self.mb_num = MetodoBiseccion(max_iter=100)
        # Intentar cargar el solver de Falsa Posición (requiere sympy y numpy)
        self.mb_fp = None
        # Intentar cargar el solver de Newton-Raphson
        self.mb_newton = None
        # Intentar cargar el solver de Secante
        self.mb_secante = None
        try:
            from metodo_falsa_posicion import FalsePositionSolver as _FPS
            self.mb_fp = _FPS(max_iter=100)
        except Exception:
            self.mb_fp = None
        try:
            from metodo_newton_raph import NewtonRaphsonSolver as _NRS
            self.mb_newton = _NRS(max_iter=100)
        except Exception:
            self.mb_newton = None
        try:
            from metodo_secante import SecantSolver as _SS
            self.mb_secante = _SS(max_iter=100)
        except Exception:
            self.mb_secante = None
        self.num_state = {'last_result': None, 'decimal_mode': False}

        self.selected_matrix = None
        self.selected_method = None

        self.update_matrix_list()
        self.update_vector_set_list()
        self.update_matrix_set_list()
        # Fijar el tamaño inicial de ambos listboxes una sola vez (sin sincronizaciones posteriores)
        self._apply_initial_listbox_size()
        # Mostrar portada inicial
        self.create_start_screen()

    def create_start_screen(self):
        """Portada inicial CalcuGebra con hero y equipo."""
        try:
            self.notebook.pack_forget()
        except Exception:
            pass

        self.start_frame = tk.Frame(self.root, bg=self.palette["background"])
        self.start_frame.pack(fill="both", expand=True)

        # Canvas con scroll invisible para toda la portada
        self.start_canvas = tk.Canvas(self.start_frame, bg=self.palette["background"], highlightthickness=0, bd=0)
        start_scroll = ttk.Scrollbar(self.start_frame, orient=tk.VERTICAL, command=self.start_canvas.yview, style='App.Vertical.TScrollbar')
        try:
            start_scroll.configure(width=8)
        except Exception:
            pass
        self.start_canvas.configure(yscrollcommand=start_scroll.set)
        self.start_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        start_scroll.pack(side=tk.RIGHT, fill="y")

        start_inner = tk.Frame(self.start_canvas, bg=self.palette["background"])
        inner_window = self.start_canvas.create_window((0, 0), window=start_inner, anchor="nw")
        start_inner.bind("<Configure>", lambda e: self.start_canvas.configure(scrollregion=self.start_canvas.bbox("all")))
        self.start_canvas.bind("<Configure>", lambda e: self.start_canvas.itemconfig(inner_window, width=e.width))
        def _on_start_wheel(ev):
            self.start_canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
        # Scroll con rueda en cualquier zona de la portada (Windows/mac) y botones 4/5 (Linux)
        def _bind_global():
            try:
                self.root.bind_all("<MouseWheel>", _on_start_wheel)
                self.root.bind_all("<Button-4>", lambda e: self.start_canvas.yview_scroll(-1, "units"))
                self.root.bind_all("<Button-5>", lambda e: self.start_canvas.yview_scroll(1, "units"))
            except Exception:
                pass
        _bind_global()

        hero_height = 320
        self.hero_canvas = tk.Canvas(
            start_inner,
            bg=self.palette["background"],
            height=hero_height,
            highlightthickness=0,
            bd=0,
        )
        self.hero_canvas.pack(fill="x", expand=False)
        self.hero_canvas.bind("<Configure>", lambda e: self._paint_start_hero(e.width, hero_height))

        content = tk.Frame(start_inner, bg=self.palette["background"])
        content.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        card = tk.Frame(content, bg=self.palette["panel"], padx=32, pady=28, bd=0, highlightthickness=0)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="CalcuGebra", font=self.fonts["hero"], fg=self.palette["text"], bg=self.palette["panel"]).pack(anchor="w")
        tk.Label(
            card,
            text="Calculadora creativa de algebra lineal: matrices, resolucion de sistemas de ecuaciones lineales y metodos numericos que muestran cada paso.",
            font=self.fonts["label"],
            fg=self.palette["accent"],
            bg=self.palette["panel"],
            wraplength=880,
            justify="left",
        ).pack(anchor="w", pady=(8, 16))

        origin_text = (
            "Nacio en la clase de Algebra Lineal como laboratorio vivo: construir, probar y visualizar algoritmos reales "
            "para que cualquier persona pueda entenderlos y aplicarlos sin perder precision academica."
        )
        tk.Label(
            card,
            text=origin_text,
            font=self.fonts["body"],
            fg=self.palette["text"],
            bg=self.palette["panel"],
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        thanks_block = tk.Frame(card, bg=self.palette["panel"])
        thanks_block.pack(anchor="w", fill="x", pady=(0, 14))
        tk.Label(
            thanks_block,
            text="Profesor Carlos Iván Argüello",
            font=self.fonts["hero"],
            fg=self.palette["accent"],
            bg=self.palette["panel"],
        ).pack(anchor="w")
        tk.Label(
            thanks_block,
            text="Agradecimiento especial por su guía y apoyo constante.",
            font=self.fonts["body"],
            fg=self.palette["accent_soft"],
            bg=self.palette["panel"],
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        highlights = tk.Frame(card, bg=self.palette["panel"])
        highlights.pack(fill="x", pady=(0, 12))
        for title, desc in [
            ("Resolucion guiada", "Sistemas de ecuaciones lineales con pasos visibles y resultados claros."),
            ("Operadores de matrices", "Suma, producto, inversas y mas en un panel ordenado."),
            ("Metodos numericos", "Biseccion y compania con trazabilidad de iteraciones."),
        ]:
            block = tk.Frame(highlights, bg=self.palette["card"], padx=14, pady=12)
            block.pack(side="left", expand=True, fill="both", padx=6)
            tk.Label(block, text=title, font=self.fonts["label"], fg=self.palette["accent_soft"], bg=self.palette["card"]).pack(anchor="w")
            tk.Label(block, text=desc, font=self.fonts["body"], fg=self.palette["text"], bg=self.palette["card"], wraplength=240, justify="left").pack(anchor="w", pady=(4, 0))

        tk.Label(card, text="Equipo creador", font=self.fonts["label"], fg=self.palette["accent_soft"], bg=self.palette["panel"]).pack(anchor="w", pady=(10, 4))
        names_frame = tk.Frame(card, bg=self.palette["panel"])
        names_frame.pack(anchor="w", fill="x", pady=(0, 10))
        for name in [
            "ALICIA MASSIEL ESTRADA ACEVEDO",
            "STEPHANY DAIANA FLORES BALTODANO",
            "ENRIQUE JOSE TALENO NUNEZ",
        ]:
            row = tk.Frame(names_frame, bg=self.palette["panel"])
            row.pack(anchor="w", pady=2, fill="x")
            badge = tk.Canvas(row, width=10, height=10, bg=self.palette["panel"], highlightthickness=0)
            badge.create_oval(1, 1, 9, 9, fill=self.palette["accent"], outline=self.palette["accent"])
            badge.pack(side="left", padx=(0, 8))
            tk.Label(row, text=name, font=self.fonts["body"], fg=self.palette["text"], bg=self.palette["panel"]).pack(side="left")

        tk.Label(
            card,
            text="Objetivo: dominar algoritmos de algebra lineal mientras se comparte una herramienta accesible y vistosa para resolverlos rapido.",
            font=self.fonts["body"],
            fg=self.palette["muted"],
            bg=self.palette["panel"],
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 18))

        ttk.Button(card, text="Entrar a CalcuGebra", style='Dark.TButton', command=self._show_main_app).pack(anchor="w", pady=(6, 0))

    def _paint_start_hero(self, width, height):
        """Dibuja hero con plano cartesiano y parabola."""
        canvas = self.hero_canvas
        canvas.delete("all")
        stripes = ["#132035", "#0f172a", "#0b1220"]
        stripe_h = max(1, height // len(stripes))
        for i, color in enumerate(stripes):
            canvas.create_rectangle(0, i * stripe_h, width, (i + 1) * stripe_h, fill=color, outline="")

        canvas.create_oval(width * 0.05, height * 0.25, width * 0.55, height * 1.05, fill=self.palette["card_alt"], outline=self.palette["card_alt"])
        canvas.create_polygon(
            width * 0.12, height * 0.7,
            width * 0.55, height * 0.32,
            width * 0.96, height * 0.9,
            width * 0.14, height * 0.98,
            fill=self.palette["card"],
            outline="",
            smooth=True,
        )

        plane_x = width * 0.62
        plane_y = height * 0.2
        plane_w = width * 0.3
        plane_h = height * 0.55
        grid_color = self.palette["accent_soft"]
        canvas.create_rectangle(plane_x, plane_y, plane_x + plane_w, plane_y + plane_h, outline=self.palette["outline"], width=2, fill=self.palette["panel"])
        for i in range(1, 5):
            gx = plane_x + (plane_w / 5) * i
            canvas.create_line(gx, plane_y, gx, plane_y + plane_h, fill=grid_color, dash=(2, 4))
        for i in range(1, 5):
            gy = plane_y + (plane_h / 5) * i
            canvas.create_line(plane_x, gy, plane_x + plane_w, gy, fill=grid_color, dash=(2, 4))
        canvas.create_line(plane_x, plane_y + plane_h / 2, plane_x + plane_w, plane_y + plane_h / 2, fill=self.palette["accent"], width=2)
        canvas.create_line(plane_x + plane_w / 2, plane_y, plane_x + plane_w / 2, plane_y + plane_h, fill=self.palette["accent"], width=2)
        points = []
        for t in range(-40, 41, 3):
            nx = t / 40
            px = plane_x + (nx + 1) * (plane_w / 2)
            py = plane_y + plane_h - ((nx ** 2) * plane_h * 0.7 + plane_h * 0.08)
            points.append(px)
            points.append(py)
        canvas.create_line(points, fill=self.palette["accent_soft"], width=3, smooth=True)

        spark_color = self.palette["accent_soft"]
        for dx, dy, r in [(0.74, 0.16, 8), (0.68, 0.34, 6), (0.84, 0.46, 7), (0.9, 0.26, 5)]:
            cx = width * dx
            cy = height * dy
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=spark_color, outline=spark_color)
            canvas.create_line(cx - r * 1.4, cy, cx + r * 1.4, cy, fill=spark_color, width=2)
            canvas.create_line(cx, cy - r * 1.4, cx, cy + r * 1.4, fill=spark_color, width=2)

        canvas.create_text(width * 0.08, height * 0.25, text="CalcuGebra", anchor="w", font=self.fonts["hero"], fill=self.palette["text"])
        canvas.create_text(
            width * 0.08,
            height * 0.42,
            text="Algebra lineal con actitud: matrices, resolucion de sistemas lineales y metodos numericos listos para explorar.",
            anchor="w",
            font=self.fonts["label"],
            fill=self.palette["accent"],
            width=width * 0.6,
        )
        canvas.create_text(
            width * 0.08,
            height * 0.58,
            text="Hecho en clase como proyecto vivo para aprender haciendo y compartirlo con mas personas.",
            anchor="w",
            font=self.fonts["body"],
            fill=self.palette["text"],
            width=width * 0.55,
        )

    def _show_main_app(self):
        """Cerrar portada y mostrar tabs."""
        try:
            if hasattr(self, 'start_frame') and self.start_frame.winfo_exists():
                self.start_frame.destroy()
        except Exception:
            pass
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except Exception:
            pass
        if not self.notebook.winfo_ismapped():
            self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def create_calculator_widgets(self, parent_frame):
        """Crea todos los widgets para la pestaña del solucionador de sistemas."""
        # Frame principal con scroll + panel de Procedimiento a la derecha
        main_frame = ttk.Frame(parent_frame, style='Surface.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Contenedor para el área scrolleable (izquierda)
        content_stack = ttk.Frame(main_frame, style='Surface.TFrame')
        content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(content_stack, bg=self.palette["panel"], highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(content_stack, orient=tk.VERTICAL, command=self.canvas.yview, style='Invisible.Vertical.TScrollbar')
        try:
            self.scrollbar.configure(width=0)
        except Exception:
            pass
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        # Hacer que el contenido ocupe el ancho del canvas para poder centrar internamente
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollable_frame.bind("<Enter>", self._bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel)

        # Panel de Procedimiento a la derecha (fijo, ocupa todo el alto y hasta el borde derecho)
        self.calc_proc_panel = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        self.calc_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12, 0), pady=4)
        # Estructura interna del panel de procedimiento (label + text con scrollbar)
        ttk.Label(self.calc_proc_panel, text="Procedimiento", style='CardTitle.TLabel').pack(anchor='nw', pady=(6, 6))
        calc_steps_container = ttk.Frame(self.calc_proc_panel, style='Card.TFrame')
        calc_steps_container.pack(fill=tk.BOTH, expand=True)
        calc_steps_container.rowconfigure(0, weight=1)
        calc_steps_container.columnconfigure(0, weight=1)
        self.steps_text = tk.Text(calc_steps_container, font=('Consolas', 12), bg=self.palette['card_alt'], fg=self.palette['text'], insertbackground=self.palette['text'], bd=0, highlightthickness=0, width=50, wrap='word')
        self.steps_text.grid(row=0, column=0, sticky='nsew')
        calc_steps_scrollbar = ttk.Scrollbar(calc_steps_container, orient=tk.VERTICAL, command=self.steps_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            calc_steps_scrollbar.configure(width=0)
        except Exception:
            pass
        calc_steps_scrollbar.grid(row=0, column=1, sticky='ns')
        self.steps_text.configure(yscrollcommand=calc_steps_scrollbar.set)

        # Envoltura que ocupa todo el ancho y centra el contenido en columna media
        self.center_wrapper = ttk.Frame(self.scrollable_frame, style='Surface.TFrame')
        self.center_wrapper.pack(fill='x', expand=True)
        # Distribución: columna 0 = panel izquierdo (no expandir), columna 1 = contenido (expandir), columna 2 = separador derecho (no expandir)
        self.center_wrapper.grid_columnconfigure(0, weight=0)
        self.center_wrapper.grid_columnconfigure(1, weight=1)
        self.center_wrapper.grid_columnconfigure(2, weight=0)

        # Frame contenedor centrado
        self.content_container = ttk.Frame(self.center_wrapper, style='Surface.TFrame')
        # Mover el contenido hacia la izquierda con margen de separación respecto al panel lateral
        self.content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')  # <-- Ajusta el margen izquierdo/derecho del contenido (Calculadora)

        # --- Panel lateral izquierdo para la lista de Matrices almacenadas ---
        # Ajuste vertical del layout para que los elementos laterales se estiren en Y
        self.center_wrapper.grid_rowconfigure(0, weight=1)
        # Panel izquierdo anclado a la esquina superior izquierda de la pestaña de Calculadora
        self.calc_left_panel = ttk.Frame(self.center_wrapper, style='Card.TFrame', padding=(10, 10))
        # Coordenadas panel izquierdo (Calculadora): row=0, column=0; ajustar sticky/padx/pady si deseas moverlo
        self.calc_left_panel.grid(row=0, column=0, sticky='nsw', padx=(0,10), pady=(0,0))  # <-- Coordenadas/Tamaño panel lateral (Calculadora)
        # Configuración para permitir que la lista se estire verticalmente dentro del panel
        self.calc_left_panel.grid_columnconfigure(0, weight=1)
        self.calc_left_panel.grid_rowconfigure(1, weight=1)  # <-- La fila 1 contendrá la lista; weight=1 permite estiramiento en Y

        self.create_widgets() # Llama al método original para poblar el contenedor

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _bound_to_mousewheel_vectors(self, event):
        self.vector_canvas.bind_all("<MouseWheel>", self._on_mousewheel_vectors)

    def _unbound_to_mousewheel_vectors(self, event):
        self.vector_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel_vectors(self, event):
        self.vector_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Soporte de scroll con la rueda para la pestaña Operadores
    def _bound_to_mousewheel_ops(self, event):
        self.ops_canvas.bind_all("<MouseWheel>", self._on_mousewheel_ops)

    def _unbound_to_mousewheel_ops(self, event):
        self.ops_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel_ops(self, event):
        self.ops_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Soporte de scroll con la rueda para la pestaña Métodos numéricos (zona izquierda scrolleable)
    def _bound_to_mousewheel_num(self, event):
        try:
            self.num_canvas.bind_all("<MouseWheel>", self._on_mousewheel_num)
        except Exception:
            pass

    def _unbound_to_mousewheel_num(self, event):
        try:
            self.num_canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass

    def _on_mousewheel_num(self, event):
        try:
            self.num_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception:
            pass

    # Scroll con la rueda sobre el Treeview de procedimiento (panel derecho)
    def _on_mousewheel_num_tree(self, event):
        try:
            self.num_tree.yview_scroll(int(-1*(event.delta/120)), 'units')
        except Exception:
            pass

    def _apply_initial_listbox_size(self):
        """Establece una vez un tamaño fijo para ambos listboxes (matrices y conjuntos de vectores)
        para que luzcan iguales pero sin quedar vinculados entre sí."""
        def apply_once(attempt=0):
            try:
                # Verificar que existan los frames necesarios
                if not hasattr(self, 'matrix_list_frame') or not hasattr(self, 'vector_list_frame'):
                    if attempt < 10:
                        self.root.after(150, lambda: apply_once(attempt+1))
                    return

                self.root.update_idletasks()

                # Tomar el tamaño actual visible del frame de matrices como referencia visual
                w = self.matrix_list_frame.winfo_width()
                h = self.matrix_list_frame.winfo_height()

                # Si aún no hay tamaño calculado, reintentar unas veces
                if (w <= 0 or h <= 0) and attempt < 10:
                    self.root.after(150, lambda: apply_once(attempt+1))
                    return

                # Fijar tamaños en ambos frames sin dejar eventos enlazados (no habrá sincronización dinámica)
                if w > 0 and h > 0:
                    # Evitar que la grilla reescale los frames
                    try:
                        self.matrix_list_frame.grid_propagate(False)
                    except Exception:
                        pass
                    try:
                        self.vector_list_frame.grid_propagate(False)
                    except Exception:
                        pass

                    # Aplicar el mismo tamaño inicial a ambos, de forma independiente
                    try:
                        self.matrix_list_frame.configure(width=w)
                    except Exception:
                        pass
                    try:
                        self.vector_list_frame.configure(width=w)
                    except Exception:
                        pass
            except Exception:
                # Silenciar para no afectar la app
                pass

        # Ejecutar con un pequeño retraso para asegurar que el layout esté calculado
        self.root.after(200, apply_once)


    def _add_tab_header(self, container, title, subtitle, columns):
        """Cabecera reutilizable para las pestañas con título y descripción corta."""
        header_card = ttk.Frame(container, style='Card.TFrame', padding=(18, 16))
        header_card.grid(row=0, column=0, columnspan=columns, sticky="ew", pady=(0, 12))
        header_card.grid_columnconfigure(0, weight=1)
        ttk.Label(header_card, text=title, style='CardHero.TLabel').grid(row=0, column=0, sticky="w")
        ttk.Label(header_card, text=subtitle, style='CardMuted.TLabel').grid(row=1, column=0, sticky="w", pady=(6, 0))
        return header_card

    def create_widgets(self):
        # El contenido de este metodo ahora se dibuja dentro de self.content_container
        main_frame = self.content_container
        main_frame.grid_columnconfigure(0, weight=1)

        text_color = self.palette["text"]

        self._add_tab_header(
            main_frame,
            "Solucionador Sistema de ecuaciones",
            "Gestiona, resuelve y guarda sistemas con panel lateral de procedimiento y lectura cómoda.",
            columns=4,
        )

        form_card = ttk.Frame(main_frame, style='Card.TFrame', padding=(16, 14))
        form_card.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        for c in range(4):
            form_card.grid_columnconfigure(c, weight=1)

        ttk.Label(form_card, text="Nombre de la matriz:", style='Dark.TLabel').grid(row=0, column=0, sticky="w", pady=4)
        self.name_entry = ttk.Entry(form_card, width=18, style='Entry.TEntry')
        self.name_entry.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(form_card, text="Metodo:", style='Dark.TLabel').grid(row=0, column=2, sticky="e", padx=(0, 5))
        self.method_var = tk.StringVar(value=" ")
        self.method_combobox = ttk.Combobox(
            form_card,
            textvariable=self.method_var,
            values=[
                "Gauss-Jordan",
                "Gauss",
                "Cramer",
            ],
            state="readonly",
            width=16,
        )
        self.method_combobox.grid(row=0, column=3, sticky="w")
        self.method_combobox.bind('<<ComboboxSelected>>', self._on_method_select)

        ttk.Label(form_card, text="Filas:", style='Dark.TLabel').grid(row=1, column=0, sticky="w", pady=4)
        self.rows_var = tk.StringVar(value="0")
        self.rows_spinbox = tk.Spinbox(form_card, from_=1, to=20, width=6, textvariable=self.rows_var, bg=self.palette["input"], fg=text_color, font=self.fonts["body"])
        self.rows_spinbox.grid(row=1, column=1, sticky="w", padx=(0, 20))
        ttk.Label(form_card, text="Columnas:", style='Dark.TLabel').grid(row=1, column=2, sticky="e", padx=(0, 5))
        self.cols_var = tk.StringVar(value="0")
        self.cols_spinbox = tk.Spinbox(form_card, from_=1, to=20, width=6, textvariable=self.cols_var, bg=self.palette["input"], fg=text_color, font=self.fonts["body"])
        self.cols_spinbox.grid(row=1, column=3, sticky="w")

        ttk.Button(form_card, text="Crear matriz", command=self.create_matrix, style='Dark.TButton').grid(row=2, column=0, columnspan=4, pady=(10, 10), sticky="ew")

        action_frame = ttk.Frame(form_card, style='Card.TFrame')
        action_frame.grid(row=3, column=0, columnspan=4)
        action_buttons = ttk.Frame(action_frame, style='Card.TFrame')
        action_buttons.pack(anchor='center')
        ttk.Button(action_buttons, text="Ver", command=self.view_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Modificar", command=self.modify_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Eliminar", command=self.delete_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Resolver", command=lambda: self.solve_matrix(), style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Limpiar", command=self.clear_calculator_tab, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        ttk.Label(self.calc_left_panel, text="Matrices almacenadas:", style='Dark.TLabel').grid(row=0, column=0, sticky="nw", pady=(12, 5), padx=(20, 0))
        matrix_list_frame = ttk.Frame(self.calc_left_panel, style='Card.TFrame')
        matrix_list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10), padx=(20, 0))
        matrix_list_frame.grid_columnconfigure(0, weight=1)
        matrix_list_frame.grid_rowconfigure(0, weight=1)
        self.matrix_list_frame = matrix_list_frame
        matrix_list_frame.grid_propagate(False)
        matrix_list_frame.configure(width=260, height=690)

        self.matrix_listbox = tk.Listbox(matrix_list_frame, height=6, font=('Segoe UI', 11), bg=self.palette["input"], fg=text_color, selectbackground=self.palette["accent"], selectforeground=self.palette["background"], borderwidth=0, highlightthickness=0, exportselection=0)
        self.matrix_listbox.grid(row=0, column=0, sticky="nsew")
        matrix_scrollbar = ttk.Scrollbar(matrix_list_frame, orient=tk.VERTICAL, command=self.matrix_listbox.yview, style='Invisible.Vertical.TScrollbar')
        try:
            matrix_scrollbar.configure(width=0)
        except Exception:
            pass
        matrix_scrollbar.grid(row=0, column=1, sticky="ns")
        self.matrix_listbox.configure(yscrollcommand=matrix_scrollbar.set)
        self.matrix_listbox.bind('<<ListboxSelect>>', self._on_matrix_select)

        matrix_card = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        matrix_card.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        ttk.Label(matrix_card, text="Datos de la matriz", style='CardTitle.TLabel').grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))
        self.matrix_frame = ttk.Frame(matrix_card, style='Dark.TFrame')
        self.matrix_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 4))

        equations_card = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        equations_card.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        equations_card.grid_columnconfigure(0, weight=1)
        equations_card.grid_columnconfigure(1, weight=0)
        ttk.Label(equations_card, text="Resolver desde ecuaciones (texto o LaTeX)", style='CardTitle.TLabel').grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.equations_text = tk.Text(equations_card, height=6, font=('Consolas', 12), bg=self.palette["card_alt"], fg=self.palette["text"], insertbackground=self.palette["text"], bd=0, highlightthickness=0, wrap='word')
        self.equations_text.grid(row=1, column=0, rowspan=3, sticky="nsew", padx=(0, 10))
        eq_scroll_calc = ttk.Scrollbar(equations_card, orient=tk.VERTICAL, command=self.equations_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            eq_scroll_calc.configure(width=1)
        except Exception:
            pass
        eq_scroll_calc.grid(row=1, column=2, rowspan=3, sticky='ns')
        self.equations_text.configure(yscrollcommand=eq_scroll_calc.set)
        ttk.Label(equations_card, text="Escribe ecuaciones con '=' y separa con nueva l?nea o \\ en LaTeX.", style='CardMuted.TLabel').grid(row=1, column=1, sticky='nw', pady=(0,4))
        ttk.Label(equations_card, text="Ejemplo LaTeX: 2x + 3y &= 5 \\ x - y &= 1", style='CardMuted.TLabel').grid(row=2, column=1, sticky='nw')
        ttk.Button(equations_card, text="Generar matriz y resolver", style='Dark.TButton', command=self.solve_equations_from_calculator).grid(row=3, column=1, sticky='nw', pady=(6,0))
        # Botonera específica para resolver directamente con Gauss-Jordan, Gauss o Cramer desde ecuaciones
        eq_methods_frame = ttk.Frame(equations_card, style='Card.TFrame')
        eq_methods_frame.grid(row=4, column=0, columnspan=2, sticky='w', pady=(8, 0))
        ttk.Label(eq_methods_frame, text="Resolver con:", style='Dark.TLabel').pack(anchor='w', pady=(0,4))
        eq_btns = ttk.Frame(eq_methods_frame, style='Card.TFrame')
        eq_btns.pack(anchor='w')
        ttk.Button(eq_btns, text="Gauss-Jordan", style='Dark.TButton', command=lambda: self.solve_equations_from_calculator("Gauss-Jordan")).pack(side=tk.LEFT, padx=4)
        ttk.Button(eq_btns, text="Gauss", style='Dark.TButton', command=lambda: self.solve_equations_from_calculator("Gauss")).pack(side=tk.LEFT, padx=4)
        ttk.Button(eq_btns, text="Cramer", style='Dark.TButton', command=lambda: self.solve_equations_from_calculator("Cramer")).pack(side=tk.LEFT, padx=4)

        result_container = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        result_container.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=(0, 6))
        result_container.grid_rowconfigure(1, weight=1)
        result_container.grid_columnconfigure(0, weight=1)

        ttk.Label(result_container, text="Resultado", style='CardTitle.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))

        solution_frame = ttk.Frame(result_container, style='Card.TFrame')
        solution_frame.grid(row=1, column=0, sticky="nsew")
        solution_frame.grid_rowconfigure(0, weight=1)
        solution_frame.grid_columnconfigure(0, weight=1)
        try:
            solution_frame.grid_columnconfigure(1, minsize=0)
        except Exception:
            pass

        self.result_text = tk.Text(solution_frame, height=16, width=79, font=('Segoe UI', 13), bg=self.palette["card_alt"], fg=self.palette["accent_soft"], insertbackground=text_color, bd=0, highlightthickness=0, wrap='word')
        self.result_text.grid(row=0, column=0, sticky="nsew")
        result_scrollbar = ttk.Scrollbar(
            solution_frame,
            orient=tk.VERTICAL,
            command=self.result_text.yview,
            style='Invisible.Vertical.TScrollbar'
        )
        try:
            result_scrollbar.configure(width=0)
        except Exception:
            pass
        result_scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

    # (Seccion de "Pasos" eliminada aqui; ahora vive en self.calc_proc_panel)
    def create_independence_widgets(self, parent_frame):
        """Crea todos los widgets para la pestaña de independencia de vectores
        con la misma estructura de layout/scroll que la pestaña de matrices."""

        # --- Contenedor con scroll (izquierda) + Procedimiento a la derecha ---
        main_frame = ttk.Frame(parent_frame, style='Surface.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        vector_content_stack = ttk.Frame(main_frame, style='Surface.TFrame')
        vector_content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vector_canvas = tk.Canvas(vector_content_stack, bg=self.palette["panel"], highlightthickness=0, bd=0)
        vector_scrollbar = ttk.Scrollbar(vector_content_stack, orient=tk.VERTICAL, command=self.vector_canvas.yview, style='Invisible.Vertical.TScrollbar')
        try:
            vector_scrollbar.configure(width=0)
        except Exception:
            pass
        self.vector_scrollable_frame = ttk.Frame(self.vector_canvas, style='Dark.TFrame')
        self.vector_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.vector_canvas.configure(scrollregion=self.vector_canvas.bbox("all"))
        )
        self.vector_canvas_window = self.vector_canvas.create_window((0, 0), window=self.vector_scrollable_frame, anchor="nw")
        self.vector_canvas.bind("<Configure>", lambda e: self.vector_canvas.itemconfig(self.vector_canvas_window, width=e.width))
        self.vector_canvas.configure(yscrollcommand=vector_scrollbar.set)
        self.vector_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vector_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bindeo de la rueda del ratón
        self.vector_scrollable_frame.bind("<Enter>", self._bound_to_mousewheel_vectors)
        self.vector_scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel_vectors)

        # Panel de Procedimiento a la derecha (fijo)
        self.ind_proc_panel = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        self.ind_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12,0), pady=4)
        ttk.Label(self.ind_proc_panel, text="Procedimiento", style='CardTitle.TLabel').pack(anchor='nw', pady=(6,6))
        ind_steps_container = ttk.Frame(self.ind_proc_panel, style='Card.TFrame')
        ind_steps_container.pack(fill=tk.BOTH, expand=True)
        ind_steps_container.rowconfigure(0, weight=1)
        ind_steps_container.columnconfigure(0, weight=1)
        self.independence_steps_text = tk.Text(ind_steps_container, font=('Consolas', 12), bg=self.palette['card_alt'], fg=self.palette['text'], insertbackground=self.palette['text'], bd=0, highlightthickness=0, width=50, wrap='word')
        self.independence_steps_text.grid(row=0, column=0, sticky='nsew')
        ind_steps_scrollbar = ttk.Scrollbar(ind_steps_container, orient=tk.VERTICAL, command=self.independence_steps_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            ind_steps_scrollbar.configure(width=0)
        except Exception:
            pass
        ind_steps_scrollbar.grid(row=0, column=1, sticky='ns')
        self.independence_steps_text.configure(yscrollcommand=ind_steps_scrollbar.set)

    # --- Contenedor de contenido centrado ---
        self.vector_center_wrapper = ttk.Frame(self.vector_scrollable_frame, style='Surface.TFrame')
        self.vector_center_wrapper.pack(fill='x', expand=True)
        # Distribución: 0 = panel izquierdo (no expandir), 1 = contenido (expandir), 2 = separador derecho (no expandir)
        self.vector_center_wrapper.grid_columnconfigure(0, weight=0)
        self.vector_center_wrapper.grid_columnconfigure(1, weight=1)
        self.vector_center_wrapper.grid_columnconfigure(2, weight=0)

        self.vector_content_container = ttk.Frame(self.vector_center_wrapper, style='Surface.TFrame')
        # Mover contenido a la izquierda con margen respecto al panel lateral
        self.vector_content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')  # <-- Ajusta margen contenido (Vectores)

        # --- Panel lateral izquierdo para Conjuntos de Vectores ---
        # Permite estiramiento vertical del panel lateral
        self.vector_center_wrapper.grid_rowconfigure(0, weight=1)
        self.vec_left_panel = ttk.Frame(self.vector_center_wrapper, style='Card.TFrame', padding=(10, 10))
        # Coordenadas panel izquierdo (Vectores): esquina superior izquierda
        self.vec_left_panel.grid(row=0, column=0, sticky='nsw', padx=(0,10), pady=(0,0))  # <-- Coordenadas/Tamaño panel lateral (Vectores)
        self.vec_left_panel.grid_columnconfigure(0, weight=1)
        self.vec_left_panel.grid_rowconfigure(1, weight=1)  # <-- La fila 1 contendrá la lista; se estira en Y

        container = self.vector_content_container
        # Configurar columnas para que escalen horizontalmente
        for c in range(4):
            container.grid_columnconfigure(c, weight=1)

        # Cabecera destacada
        self._add_tab_header(
            container,
            "Independencia de Vectores",
            "Construye conjuntos, verifica independencia y revisa pasos en paralelo.",
            columns=4,
        )

        vec_form_card = ttk.Frame(container, style='Card.TFrame', padding=(16, 14))
        vec_form_card.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(0, 12))
        for c in range(4):
            vec_form_card.grid_columnconfigure(c, weight=1)

        # --- Controles superiores ---
        ttk.Label(vec_form_card, text="Nombre:", style='Dark.TLabel').grid(row=0, column=0, sticky='w')
        self.vector_name_entry = ttk.Entry(vec_form_card, width=18, style='Entry.TEntry')
        self.vector_name_entry.grid(row=0, column=1, sticky='w', padx=(0, 20))

        ttk.Label(vec_form_card, text="Nº Vectores:", style='Dark.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.num_vectors_var = tk.StringVar(value="0")
        num_vectors_spinbox = tk.Spinbox(vec_form_card, from_=1, to=20, width=6, textvariable=self.num_vectors_var, bg=self.palette["input"], fg=self.palette["text"])
        num_vectors_spinbox.grid(row=1, column=1, sticky='w', padx=(0,20))

        ttk.Label(vec_form_card, text="Dimensión:", style='Dark.TLabel').grid(row=1, column=2, sticky='e', padx=(0,5))
        self.dim_vectors_var = tk.StringVar(value="0")
        dim_vectors_spinbox = tk.Spinbox(vec_form_card, from_=1, to=20, width=6, textvariable=self.dim_vectors_var, bg=self.palette["input"], fg=self.palette["text"])
        dim_vectors_spinbox.grid(row=1, column=3, sticky='w')

        ttk.Button(vec_form_card, text="Crear Conjunto de Vectores", style='Dark.TButton', command=self.create_vector_set_ui).grid(row=2, column=0, columnspan=4, pady=(10, 20), sticky='ew')

        # --- Lista de Conjuntos y Acciones (distribución similar a matrices) ---
        # --- Lista de Conjuntos de Vectores en panel lateral izquierdo (Vectores) ---
        ttk.Label(self.vec_left_panel, text="Conjuntos de Vectores Almacenados:", style='Dark.TLabel')\
            .grid(row=0, column=0, sticky='nw', pady=(12,5), padx=(20,0))  # <-- Coordenadas etiqueta (Vectores)
        # Contenedor con scrollbar para la lista de conjuntos de vectores
        vector_list_frame = ttk.Frame(self.vec_left_panel, style='Card.TFrame')
        vector_list_frame.grid_propagate(False)
        vector_list_frame.configure(width=260, height=690)
        vector_list_frame.grid(row=1, column=0, sticky='nsew', pady=(0,10), padx=(20,0))  # <-- Coordenadas/Tamaño lista (Vectores)
        vector_list_frame.grid_columnconfigure(0, weight=1)
        vector_list_frame.grid_rowconfigure(0, weight=1)
        # Guardar referencia para sincronizar tamaño con el listbox de matrices
        self.vector_list_frame = vector_list_frame

        self.vector_set_listbox = tk.Listbox(vector_list_frame, height=6, font=('Segoe UI', 11), bg=self.palette['input'], fg=self.palette['text'], selectbackground=self.palette['accent'], selectforeground=self.palette['background'], borderwidth=0, highlightthickness=0, exportselection=0)
        self.vector_set_listbox.grid(row=0, column=0, sticky='nsew')
        vector_scrollbar = ttk.Scrollbar(vector_list_frame, orient=tk.VERTICAL, command=self.vector_set_listbox.yview, style='Invisible.Vertical.TScrollbar')
        try:
            vector_scrollbar.configure(width=0)
        except Exception:
            pass
        vector_scrollbar.grid(row=0, column=1, sticky='ns')  # <-- Side bar (scroll) asociado a la lista (Vectores)
        self.vector_set_listbox.configure(yscrollcommand=vector_scrollbar.set)
        self.vector_set_listbox.bind('<<ListboxSelect>>', self._on_vector_set_select)

        # Botonera centrada (alinea con "Crear Conjunto de Vectores")
        vector_action_frame = ttk.Frame(vec_form_card, style='Card.TFrame')
        vector_action_frame.grid(row=3, column=0, columnspan=4, pady=(0, 4))
        vector_action_buttons = ttk.Frame(vector_action_frame, style='Surface.TFrame')
        vector_action_buttons.pack(anchor='center')
        ttk.Button(vector_action_buttons, text="Ver", command=self.view_vector_set, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(vector_action_buttons, text="Modificar", command=self.modify_vector_set_ui, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(vector_action_buttons, text="Eliminar", command=self.delete_vector_set, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        # Ubicar Verificar Independencia junto a Eliminar
        ttk.Button(vector_action_buttons, text="Verificar Independencia", command=self.run_independence_check, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(vector_action_buttons, text="Limpiar", command=self.clear_independence_tab, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        # --- Área de datos de vectores ---
        ttk.Label(container, text="Datos del conjunto:", style='CardTitle.TLabel').grid(row=2, column=0, columnspan=4, sticky='w', pady=(10,5))
        self.vector_entries_frame = ttk.Frame(container, style='Card.TFrame', padding=(12, 10))
        self.vector_entries_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(0,10))

        # --- Área de resultados con scroll (igual estilo que matrices) ---
        results_container = ttk.Frame(container, style='Card.TFrame', padding=(14, 12))
        results_container.grid(row=4, column=0, columnspan=4, sticky='nsew', pady=(10,0))
        results_container.grid_rowconfigure(1, weight=1)
        results_container.grid_rowconfigure(3, weight=1)
        results_container.grid_columnconfigure(0, weight=1)

        ttk.Label(results_container, text="Resultado", style='CardTitle.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        solution_frame_vec = ttk.Frame(results_container)
        solution_frame_vec.grid(row=1, column=0, sticky='nsew')
        solution_frame_vec.grid_rowconfigure(0, weight=1)
        solution_frame_vec.grid_columnconfigure(0, weight=1)

        self.independence_result_text = tk.Text(solution_frame_vec, height=16, width=79, font=('Segoe UI', 13), bg=self.palette['card_alt'], fg=self.palette['accent_soft'], insertbackground=self.palette['text'], bd=0, highlightthickness=0, wrap='word')
        self.independence_result_text.grid(row=0, column=0, sticky='nsew')
        result_scrollbar_vec = ttk.Scrollbar(solution_frame_vec, orient=tk.VERTICAL, command=self.independence_result_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            result_scrollbar_vec.configure(width=0)
        except Exception:
            pass
        result_scrollbar_vec.grid(row=0, column=1, sticky='ns')
        self.independence_result_text.configure(yscrollcommand=result_scrollbar_vec.set)

    # (Procedimiento movido al panel derecho)

    def create_fresh_operator_widgets(self, parent_frame):
        """Embebe el operador dual en una pestaña dedicada con el estilo de la app."""
        container = ttk.Frame(parent_frame, style='Surface.TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        try:
            import operators_fresh

            self.embedded_operator = operators_fresh.create_embedded_operator(
                container, palette=self.palette, fonts=self.fonts
            )
            if hasattr(self.embedded_operator, "container"):
                self.embedded_operator.container.pack(fill=tk.BOTH, expand=True)
        except Exception as exc:
            fallback = ttk.Frame(container, style='Card.TFrame', padding=14)
            fallback.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            ttk.Label(fallback, text="No se pudo cargar el operador de matrices.", style='CardTitle.TLabel').pack(anchor="w")
            ttk.Label(fallback, text=str(exc), style='CardMuted.TLabel', wraplength=800, justify='left').pack(anchor="w", pady=(8, 0))

    def create_numeric_widgets(self, parent_frame):
        """Crea la pestaña 'Métodos numéricos' con el mismo layout base."""
        # Contenedor con scroll (izquierda) + Procedimiento a la derecha
        main_frame = ttk.Frame(parent_frame, style='Surface.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        num_content_stack = ttk.Frame(main_frame, style='Surface.TFrame')
        num_content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.num_canvas = tk.Canvas(num_content_stack, bg=self.palette["panel"], highlightthickness=0, bd=0)
        num_scrollbar = ttk.Scrollbar(num_content_stack, orient=tk.VERTICAL, command=self.num_canvas.yview, style='CalcVisible.Vertical.TScrollbar')
        try:
            num_scrollbar.configure(width=10)
        except Exception:
            pass
        self.num_scrollable_frame = ttk.Frame(self.num_canvas, style='Dark.TFrame')
        self.num_scrollable_frame.bind(
            "<Configure>", lambda e: self.num_canvas.configure(scrollregion=self.num_canvas.bbox("all"))
        )
        # Habilitar scroll con la rueda del ratón para toda la zona scrolleable
        self.num_scrollable_frame.bind("<Enter>", self._bound_to_mousewheel_num)
        self.num_scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel_num)
        self.num_canvas_window = self.num_canvas.create_window((0, 0), window=self.num_scrollable_frame, anchor="nw")
        self.num_canvas.bind("<Configure>", lambda e: self.num_canvas.itemconfig(self.num_canvas_window, width=e.width))
        self.num_canvas.configure(yscrollcommand=num_scrollbar.set)
        self.num_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        num_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Panel de Procedimiento a la derecha (con tabla)
        self.num_proc_panel = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        self.num_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12,0), pady=4)
        # Hacer el panel de procedimiento un poco más estrecho
        try:
            self.num_proc_panel.configure(width=560)
            self.num_proc_panel.pack_propagate(False)
        except Exception:
            pass
        ttk.Label(self.num_proc_panel, text="Procedimiento", style='CardTitle.TLabel').pack(anchor='nw', pady=(6,6))
        num_steps_container = ttk.Frame(self.num_proc_panel, style='Card.TFrame')
        num_steps_container.pack(fill=tk.BOTH, expand=True)
        num_steps_container.rowconfigure(0, weight=1)
        num_steps_container.columnconfigure(0, weight=1)
        cols = ('iter','a','b','c','fa','fb','fc')
        self.num_tree = ttk.Treeview(num_steps_container, columns=cols, show='headings', height=20, style='Elegant.Treeview')
        for c in cols:
            self.num_tree.heading(c, text=c)
            width = 60 if c == 'iter' else 70
            self.num_tree.column(c, width=width, anchor='center')
        self.num_tree.grid(row=0, column=0, sticky='nsew')
        num_steps_scrollbar = ttk.Scrollbar(num_steps_container, orient=tk.VERTICAL, command=self.num_tree.yview, style='Invisible.Vertical.TScrollbar')
        try:
            num_steps_scrollbar.configure(width=0)
        except Exception:
            pass
        num_steps_scrollbar.grid(row=0, column=1, sticky='ns')
        self.num_tree.configure(yscrollcommand=num_steps_scrollbar.set)
        # Habilitar scroll con rueda sobre el Treeview
        self.num_tree.bind("<Enter>", lambda e: self.num_tree.bind_all("<MouseWheel>", self._on_mousewheel_num_tree))
        self.num_tree.bind("<Leave>", lambda e: self.num_tree.unbind_all("<MouseWheel>"))

        # Wrapper centrado similar a otras pestañas
        self.num_center_wrapper = ttk.Frame(self.num_scrollable_frame, style='Surface.TFrame')
        self.num_center_wrapper.pack(fill='x', expand=True)
        self.num_center_wrapper.grid_columnconfigure(0, weight=0)
        self.num_center_wrapper.grid_columnconfigure(1, weight=1)
        self.num_center_wrapper.grid_columnconfigure(2, weight=0)

        self.num_content_container = ttk.Frame(self.num_center_wrapper, style='Surface.TFrame')
        self.num_content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')

        # Panel izquierdo para CRUD de ecuaciones (como otras pestañas)
        self.num_left_panel = ttk.Frame(self.num_center_wrapper, style='Card.TFrame', padding=(10, 10))
        self.num_left_panel.grid(row=0, column=0, sticky='nsw', padx=(0,10), pady=(0,0))
        self.num_left_panel.grid_propagate(False)
        self.num_left_panel.configure(width=260, height=520)
        ttk.Label(self.num_left_panel, text="Ecuaciones almacenadas:", style='Dark.TLabel').grid(row=0, column=0, sticky='nw', pady=(12,5), padx=(20,0))
        eq_list_frame = ttk.Frame(self.num_left_panel, style='Card.TFrame')
        eq_list_frame.grid(row=1, column=0, sticky='nsew', pady=(0,10), padx=(20,0))
        eq_list_frame.grid_propagate(False)
        eq_list_frame.configure(width=260, height=505)
        eq_list_frame.grid_columnconfigure(0, weight=1)
        # No reservar espacio; barra invisible con ancho 0
        try:
            eq_list_frame.grid_columnconfigure(1, minsize=0)
        except Exception:
            pass
        eq_list_frame.grid_rowconfigure(0, weight=1)
        self.eq_list_frame = eq_list_frame
        self.eq_listbox = tk.Listbox(
            eq_list_frame,
            height=6,
            font=('Segoe UI', 11),
            bg=self.palette['input'],
            fg=self.palette['text'],
            selectbackground=self.palette['accent'],
            selectforeground=self.palette['background'],
            borderwidth=0,
            highlightthickness=0,
            exportselection=0
        )
        self.eq_listbox.grid(row=0, column=0, sticky='nsew')
        # Scrollbar vertical invisible para la lista de ecuaciones
        eq_vscroll = ttk.Scrollbar(eq_list_frame, orient=tk.VERTICAL, command=self.eq_listbox.yview, style='Invisible.Vertical.TScrollbar')
        try:
            eq_vscroll.configure(width=0)
        except Exception:
            pass
        eq_vscroll.grid(row=0, column=1, sticky='ns')
        self.eq_listbox.configure(yscrollcommand=eq_vscroll.set)
        self.eq_listbox.bind('<<ListboxSelect>>', self._on_equation_select)

        container = self.num_content_container
        for c in range(4):
            container.grid_columnconfigure(c, weight=1)

        # Cabecera destacada
        self._add_tab_header(
            container,
            "Métodos numéricos",
            "Ejecuta Bisección, Falsa Posición, Newton y Secante con panel de pasos y vista previa LaTeX.",
            columns=4,
        )

        num_form_card = ttk.Frame(container, style='Card.TFrame', padding=(16, 14))
        num_form_card.grid(row=1, column=0, columnspan=4, sticky='ew', pady=(0, 12))
        for c in range(4):
            num_form_card.grid_columnconfigure(c, weight=1)

    # Fila 1: Nombre + Método (alineado como en otras pestañas)
        ttk.Label(num_form_card, text="Nombre de la ecuación:", style='Dark.TLabel').grid(row=0, column=0, sticky='w')
        self.num_name_entry = ttk.Entry(num_form_card, width=18, style='Entry.TEntry')
        self.num_name_entry.grid(row=0, column=1, sticky='w', padx=(0,20))
        ttk.Label(num_form_card, text="Método:", style='Dark.TLabel').grid(row=0, column=2, sticky='e', padx=(0,5))
        self.num_method_var = tk.StringVar(value="Bisección")
        self.num_method_combobox = ttk.Combobox(
            num_form_card,
            textvariable=self.num_method_var,
            values=["Bisección", "Falsa Posición", "Newton-Raphson", "Secante"],
            state="readonly",
            width=16,
        )
        self.num_method_combobox.grid(row=0, column=3, sticky='w')

    # Fila 2: Expresión
        expr_card = ttk.Frame(container, style='Card.TFrame', padding=(12, 10))
        expr_card.grid(row=2, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        expr_card.grid_columnconfigure(0, weight=1)
        expr_card.grid_columnconfigure(1, weight=1)

        ttk.Label(expr_card, text="Expresión f(x):", style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0,4))
        self.num_expr_entry = ttk.Entry(expr_card, width=52, style='MathEntry.TEntry')
        # Destacar el cursor de inserción para saber dónde se escribe
        try:
            self.num_expr_entry.configure(
                insertbackground=self.palette["accent"],
                insertwidth=2,
            )
        except Exception:
            pass
        self.num_expr_entry.grid(row=1, column=0, sticky='we', padx=(0,12), pady=(0,4))
        self.num_expr_entry.bind("<KeyRelease>", lambda e: self._update_latex_preview())

        # Vista previa grande renderizada (LaTeX) en un cuadro dedicado y claro
        preview_box = tk.Frame(expr_card, bg="#ffffff", highlightbackground=self.palette['outline'], highlightthickness=1, bd=0)
        preview_box.configure(height=110)
        try:
            preview_box.grid_propagate(False)
        except Exception:
            pass
        preview_box.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(6,0))
        preview_box.grid_columnconfigure(0, weight=1)
        preview_box.grid_rowconfigure(0, weight=1)
        self.num_expr_preview = tk.Label(
            preview_box,
            text="Vista previa LaTeX",
            anchor='w',
            justify='left',
            bg="#ffffff",
            fg="#0b0b0b",
            font=('Segoe UI', 16),
            padx=6,
            pady=4,
        )
        self.num_expr_preview.grid(row=0, column=0, sticky='nsew')
        self._latex_preview_image = None

    # Fila 3: Teclado matem?tico/LaTeX con pesta?as
        math_tabs = [
            ("123", [
                [("x","x",None), ("y","y",None), ("π","\\pi",None), ("e","e",None), ("7","7",None), ("8","8",None), ("9","9",None), ("·","\\cdot",None), ("÷","/ ",None)],
                [("x²","x^2",None), ("y²","y^2",None), ("√","\\sqrt{ }",6), ("|x|","\\left|  \\right|",8), ("4","4",None), ("5","5",None), ("6","6",None), ("+","+",None), ("-","-",None)],
                [("<","<",None), (">",">",None), ("⌊x⌋","\\lfloor  \\rfloor",9), ("⌈x⌉","\\lceil  \\rceil",9), ("1","1",None), ("2","2",None), ("3","3",None), ("=","=",None), (",",", ",None)],
                [("ans","ans",None), ("(", "(", None), (")", ")", None), ("[", "[", None), ("]", "]", None), ("0","0",None), (".",".",None), ("<","<",None), (">",">",None)],
            ]),
            ("f(x)", [
                [("sen","\\sin()",5), ("cos","\\cos()",5), ("tg","\\tan()",5), ("sen^-1","\\sin^{-1}()",9), ("cos^-1","\\cos^{-1}()",9), ("tg^-1","\\tan^{-1}()",9), ("ln","\\ln()",4), ("log10","\\log_{10}()",10), ("log","\\log()",5)],
                [("e^","e^{ }",3), ("10^","10^{ }",4), ("√x","\\sqrt{ }",6), ("∛x","\\sqrt[3]{ }",10), ("^","^{}",2), ("_","_{ }",3), ("d/dx","\\frac{d}{dx}",10), ("∂","\\partial",None), ("∫","\\int ",None)],
                [("∑","\\sum",None), ("∏","\\prod",None), ("lim","\\lim_{x\\to }",12), ("→","\\to",None), ("∞","\\infty",None), ("≈","\\approx",None), ("≠","\\neq",None), ("≤","\\le",None), ("≥","\\ge",None)],
                [("{","{",None), ("}","}",None), ("<", "<", None), (">", ">", None), ("(","(",None), (")",")",None), ("[","[",None), ("]","]",None), ("\\","\\\\ ",None)],
            ]),
            ("ABC", [
                [("a","a",None), ("b","b",None), ("c","c",None), ("A","A",None), ("B","B",None), ("C","C",None), ("x","x",None), ("y","y",None), ("z","z",None)],
                [("α","\\alpha",None), ("β","\\beta",None), ("γ","\\gamma",None), ("θ","\\theta",None), ("λ","\\lambda",None), ("μ","\\mu",None), ("π","\\pi",None), ("φ","\\phi",None), ("ω","\\omega",None)],
                [("vec","\\vec{}",5), ("T","^{T}",2), ("det","\\det()",6), ("⊤","\\top",None), ("⊥","\\perp",None), ("∈","\\in",None), ("∉","\\notin",None), ("∪","\\cup",None), ("∩","\\cap",None)],
                [("∀","\\forall",None), ("∃","\\exists",None), ("¬","\\neg",None), ("⇒","\\Rightarrow",None), ("⇔","\\Leftrightarrow",None), ("∴","\\therefore",None), ("∵","\\because",None), ("⊂","\\subset",None), ("⊆","\\subseteq",None)],
            ]),
            ("#&?", [
                [("%","%",None), ("!","!",None), ("$","$",None), ("°","^{\\circ}",3), ("|","|",None), (";",";",None), (":",":",None), ("^","^",None), ("_","_",None)],
                [("<=","\\le",None), (">=","\\ge",None), ("≠","\\neq",None), ("±","\\pm",None), ("·","\\cdot",None), ("∓","\\mp",None), ("∫","\\int ",None), ("∮","\\oint",None), ("∑","\\sum",None)],
                [("→","\\to",None), ("↦","\\mapsto",None), ("⇑","\\Uparrow",None), ("⇓","\\Downarrow",None), ("⇔","\\Leftrightarrow",None), ("∇","\\nabla",None), ("⊗","\\otimes",None), ("⊕","\\oplus",None), ("∂","\\partial",None)],
                [("√","\\sqrt{ }",6), ("frac","\\frac{ }{ }",6), ("|x|","\\left|  \\right|",8), ("⌊⌋","\\lfloor  \\rfloor",9), ("⌈⌉","\\lceil  \\rceil",9), ("{ }","\\{\\}",2), ("[ ]","[]",1), ("( )","()",1), ("\\n","\\\\ ",None)],
            ])
        ]
        kb_frame = ttk.Frame(container, style='Card.TFrame', padding=(8,6))
        kb_frame.grid(row=4, column=0, columnspan=4, sticky='w', pady=(0,6))
        kb_tabbar = ttk.Frame(kb_frame, style='Surface.TFrame')
        kb_tabbar.pack(anchor='w', pady=(0,6))
        self._math_kb_frames = {}
        self._math_kb_buttons = {}
        def _show_math_tab(tab_name):
            for name, frame in self._math_kb_frames.items():
                frame.pack_forget()
            frame = self._math_kb_frames.get(tab_name)
            if frame:
                frame.pack(fill='x', expand=True)
            for name, btn in self._math_kb_buttons.items():
                btn.configure(style='TabActive.TButton' if name == tab_name else 'TabInactive.TButton')
        for tab_name, rows in math_tabs:
            btn = ttk.Button(kb_tabbar, text=tab_name, style='TabInactive.TButton', command=lambda n=tab_name: _show_math_tab(n))
            btn.pack(side=tk.LEFT, padx=(0,6))
            self._math_kb_buttons[tab_name] = btn
            tab_frame = ttk.Frame(kb_frame, style='Card.TFrame')
            for r, row in enumerate(rows):
                for c, (label, token, offset) in enumerate(row):
                    b = ttk.Button(tab_frame, text=label, style='Dark.TButton',
                                   command=lambda t=token, o=offset: self._insert_math_token(t, o))
                    b.grid(row=r, column=c, padx=2, pady=2, sticky='w')
            self._math_kb_frames[tab_name] = tab_frame
        _show_math_tab("123")
    # Fila 4: a, b
        ttk.Label(container, text="a:", style='Dark.TLabel').grid(row=5, column=0, sticky='w')
        self.num_a_entry = ttk.Entry(container, width=10, style='Entry.TEntry')
        self.num_a_entry.grid(row=5, column=1, sticky='w')
        ttk.Label(container, text="b:", style='Dark.TLabel').grid(row=5, column=2, sticky='e', padx=(0,5))
        self.num_b_entry = ttk.Entry(container, width=10, style='Entry.TEntry')
        self.num_b_entry.grid(row=5, column=3, sticky='w')

    # Fila 5: tol
        ttk.Label(container, text="tolerancia:", style='Dark.TLabel').grid(row=6, column=0, sticky='w')
        self.num_tol_entry = ttk.Entry(container, width=10, style='Entry.TEntry')
        self.num_tol_entry.grid(row=6, column=1, sticky='w')
        # Botón dedicado para detectar intervalos automáticamente
        self.num_detect_interval_btn = ttk.Button(container, text="Detectar intervalos", command=self._num_auto_interval, style='Dark.TButton')
        self.num_detect_interval_btn.grid(row=6, column=2, columnspan=2, sticky='ew', padx=(6,0))

        # Botonera de acciones CRUD centrada (incluye Auto-intervalo) justo debajo de la expresion
        eq_action_frame = ttk.Frame(container, style='Surface.TFrame')
        eq_action_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(4,4))
        eq_action_buttons = ttk.Frame(eq_action_frame, style='Card.TFrame')
        eq_action_buttons.pack(anchor='center')
        ttk.Button(eq_action_buttons, text="Ver", command=self.view_equation, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(eq_action_buttons, text="Modificar", command=self.modify_equation_ui, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(eq_action_buttons, text="Eliminar", command=self.delete_equation, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(eq_action_buttons, text="Resolver", command=self._num_run, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        self.num_plot_btn = ttk.Button(eq_action_buttons, text="Grafica", command=self._num_plot_function, style='Dark.TButton')
        self.num_plot_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(eq_action_buttons, text="Auto-intervalo", command=self._num_auto_interval, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(eq_action_buttons, text="Limpiar", command=self.clear_numeric_tab, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        # Boton largo centrado tipo "Crear Conjunto de Vectores"
        ttk.Button(container, text="Crear ecuacion", command=self.create_equation, style='Dark.TButton')            .grid(row=7, column=0, columnspan=4, pady=(10, 20), sticky='ew')

        # Fila separada para el botón de Mostrar decimales, centrado
        eq_toggle_frame = ttk.Frame(container, style='Surface.TFrame')
        # Añadimos margen superior para que no quede pegado a la hilera anterior de botones
        eq_toggle_frame.grid(row=8, column=0, columnspan=4, pady=(14,0), sticky='ew')
        eq_toggle_buttons = ttk.Frame(eq_toggle_frame, style='Card.TFrame')
        eq_toggle_buttons.pack(anchor='center')
        # Guardamos referencia para poder colocar el botón de "Actualizar ecuación" a su derecha cuando se modifique
        self.eq_toggle_buttons = eq_toggle_buttons
        self.num_toggle_btn = ttk.Button(eq_toggle_buttons, text="Mostrar decimales", command=self._num_toggle_decimal, style='Dark.TButton')
        self.num_toggle_btn.pack(side=tk.LEFT, padx=5)

        # Sección de Datos de la ecuación justo encima de Resultado
        eqdata_container = ttk.Frame(container, style='Card.TFrame', padding=(12, 10))
        # Margen más pequeño como en Independencia de Vectores
        # Importante: no expandir verticalmente esta sección para evitar huecos vacíos
        eqdata_container.grid(row=9, column=0, columnspan=4, sticky='ew', pady=(4,0))
        # No configurar weight en la fila para que no se estire en Y
        eqdata_container.grid_columnconfigure(0, weight=1)
        ttk.Label(eqdata_container, text="Datos de la ecuación", style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        eqdata_frame = ttk.Frame(eqdata_container)
        # No usar 'nsew' ni weight vertical para evitar que crezca sin contenido
        eqdata_frame.grid(row=1, column=0, sticky='ew')
        eqdata_frame.grid_columnconfigure(0, weight=1)
        # Text sin barra lateral; altura mínima y autoajuste por contenido
        self.num_eq_data_text = tk.Text(eqdata_frame, height=1, width=79, font=('Segoe UI', 13), bg=self.palette['card_alt'], fg=self.palette['text'], insertbackground=self.palette['text'], bd=0, highlightthickness=0, wrap='word')
        self.num_eq_data_text.grid(row=0, column=0, sticky='nsew')
        # Inicializar en altura mínima
        try:
            self._num_eqdata_autosize(min_lines=1, max_lines=8)
        except Exception:
            pass

        # Resultado (igual estilo que otras pestañas)
        result_container = ttk.Frame(container, style='Card.TFrame', padding=(14, 12))
        # Mantener mismo margen vertical superior que en "Datos del conjunto" de la pestaña de Vectores
        result_container.grid(row=10, column=0, columnspan=4, sticky='nsew', pady=(10,0))
        result_container.grid_rowconfigure(1, weight=1)
        result_container.grid_columnconfigure(0, weight=1)
        ttk.Label(result_container, text="Resultado", style='CardTitle.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        # Mismo patrón que en las otras pestañas: frame local + Text + Scrollbar
        solution_frame_num = ttk.Frame(result_container)
        solution_frame_num.grid(row=1, column=0, sticky='nsew')
        solution_frame_num.grid_rowconfigure(0, weight=1)
        solution_frame_num.grid_columnconfigure(0, weight=1)
        self.num_result_text = tk.Text(solution_frame_num, height=11, width=79, font=('Segoe UI', 13), bg=self.palette['card_alt'], fg=self.palette['accent_soft'], insertbackground=self.palette['text'], bd=0, highlightthickness=0, wrap='word')
        self.num_result_text.grid(row=0, column=0, sticky='nsew')
        # Scrollbar vertical para el resultado (estilo invisible como el resto)
        num_result_scroll = ttk.Scrollbar(solution_frame_num, orient=tk.VERTICAL, command=self.num_result_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            num_result_scroll.configure(width=0)
        except Exception:
            pass
        num_result_scroll.grid(row=0, column=1, sticky='ns')
        self.num_result_text.configure(yscrollcommand=num_result_scroll.set)

        # Estado de modificación
        self._num_editing_name = None
        # Cargar lista inicial
        self.update_equation_list()
        # (Se quita la sincronización especial de alturas para usar mismos parámetros que otras pestañas)

    # ---------- Helpers de la pestaña numérica ----------
    def _num_parse_number_str(self, s: str) -> float:
        s = (s or "").strip()
        if not s:
            raise ValueError("valor vacío")
        try:
            return float(s)
        except Exception:
            pass
        try:
            val = eval(s, {"__builtins__": {}}, {'pi': math.pi, 'e': math.e})
            return float(val)
        except Exception as e:
            raise ValueError(f"No se pudo interpretar el número: '{s}' ({e})")

    def _num_normalize_expr(self, expr: str) -> str:
        """Convierte ecuaciones 'algo = algo' a forma restada para los solvers."""
        txt = (expr or "").strip()
        if "=" in txt:
            left, right = txt.split("=", 1)
            txt = f"({left})-({right})"
        return txt

    def _num_to_float_from_str(self, s):
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

    def _num_fmt_dec(self, x):
        try:
            return f"{float(x):.6f}"
        except Exception:
            return ''

    def _num_render_result(self, result: dict, as_decimal: bool):
        # Render de resultado y pasos con toggle decimales/fracciones
        self.num_result_text.delete(1.0, tk.END)
        # repoblar tabla
        for item in self.num_tree.get_children():
            self.num_tree.delete(item)

        # Ajustar encabezados de columnas según el método usado
        try:
            last_method = (self.num_state or {}).get('last_method') if hasattr(self, 'num_state') else None
            if last_method == 'Newton-Raphson':
                # Mostrar derivada en la columna fb
                self.num_tree.heading('fb', text="f'(x)")
            else:
                # Restaurar encabezado estándar
                self.num_tree.heading('fb', text='fb')
            # Mantener los demás encabezados estándar
            self.num_tree.heading('fa', text='fa')
            self.num_tree.heading('fc', text='fc')
        except Exception:
            pass

        sol = (result or {}).get('solucion')
        mensaje = (result or {}).get('mensaje')
        if sol:
            root_s = sol.get('root')
            # preparar error y tolerancia
            err_s = sol.get('abs_error')
            tol_s = sol.get('tol')
            if as_decimal:
                dec = self._num_to_float_from_str(root_s)
                err_fmt = self._num_fmt_dec(self._num_to_float_from_str(err_s)) if err_s is not None else ''
                tol_fmt = self._num_fmt_dec(self._num_to_float_from_str(tol_s)) if tol_s is not None else ''
                root_label = f"Raíz: {root_s} ({self._num_fmt_dec(dec)})\niter={sol.get('iteraciones')}\n"
                if err_s is not None:
                    root_label += f"error={err_fmt}\n"
                if tol_s is not None:
                    root_label += f"tol={tol_fmt}\n"
            else:
                root_label = f"Raíz: {root_s}\niter={sol.get('iteraciones')}\n"
                if err_s is not None:
                    root_label += f"error={err_s}\n"
                if tol_s is not None:
                    root_label += f"tol={tol_s}\n"
            self.num_result_text.insert(tk.END, root_label + "\n")
        if mensaje:
            self.num_result_text.insert(tk.END, str(mensaje) + "\n")

        # Pasos (en panel derecho)
        pasos = (result or {}).get('pasos', [])
        for paso in pasos:
            a_v = paso.get('a'); b_v = paso.get('b'); c_v = paso.get('c')
            fa_v = paso.get('fa'); fb_v = paso.get('fb'); fc_v = paso.get('fc')
            if as_decimal:
                a_v = self._num_fmt_dec(self._num_to_float_from_str(a_v)) if a_v is not None else ''
                b_v = self._num_fmt_dec(self._num_to_float_from_str(b_v)) if b_v is not None else ''
                c_v = self._num_fmt_dec(self._num_to_float_from_str(c_v)) if c_v is not None else ''
                fa_v = self._num_fmt_dec(self._num_to_float_from_str(fa_v)) if fa_v is not None else ''
                fb_v = self._num_fmt_dec(self._num_to_float_from_str(fb_v)) if fb_v is not None else ''
                fc_v = self._num_fmt_dec(self._num_to_float_from_str(fc_v)) if fc_v is not None else ''
            self.num_tree.insert('', 'end', values=(paso.get('iter'), a_v, b_v, c_v, fa_v, fb_v, fc_v))

    def _num_eqdata_autosize(self, min_lines: int = 1, max_lines: int = 8):
        """Ajusta la altura del Text de 'Datos de la ecuación' al contenido.
        - min_lines: altura mínima cuando está vacío o con poco contenido.
        - max_lines: tope para evitar que empuje al resto del layout.
        """
        try:
            if not hasattr(self, 'num_eq_data_text'):
                return
            txt = self.num_eq_data_text
            content = txt.get("1.0", "end-1c")
            lines = (content.count("\n") + 1) if content else 1
            lines = max(min_lines, min(lines, max_lines))
            txt.configure(height=lines)
        except Exception:
            pass

    def _num_sync_result_height(self, attempt: int = 0):
        """Ajusta la altura del frame de resultado de Métodos numéricos
        para que coincida con la altura visible del resultado en la pestaña
        de Independencia de Vectores. Reintenta algunas veces hasta que
        ambos widgets tengan tamaños calculados.
        """
        try:
            if not hasattr(self, 'num_solution_frame') or not hasattr(self, 'independence_result_text'):
                return
            self.root.update_idletasks()
            target_h = self.independence_result_text.winfo_height()
            if target_h <= 1 and attempt < 10:
                # Aún no hay layout definitivo; reintentar
                self.root.after(200, lambda: self._num_sync_result_height(attempt+1))
                return
            if target_h > 1:
                try:
                    self.num_solution_frame.grid_propagate(False)
                except Exception:
                    pass
                try:
                    self.num_solution_frame.configure(height=target_h)
                except Exception:
                    pass
        except Exception:
            # Silenciar para no romper la UI
            pass

    def _num_run(self):
        method = self.num_method_var.get()
        expr = self.num_expr_entry.get().strip()
        tol_input = self.num_tol_entry.get().strip()
        a_txt = self.num_a_entry.get().strip()
        b_txt = self.num_b_entry.get().strip()
        a = b = None

        # Si faltan datos en los campos y hay una ecuación seleccionada, recuperar del almacenamiento
        selected_data = None
        if (not expr or not tol_input or not a_txt or not b_txt) and getattr(self, 'selected_equation', None):
            try:
                from persistencia import cargar_ecuacion
                selected_data = cargar_ecuacion(self.selected_equation)
            except Exception:
                selected_data = None

        # Determinar expresión
        if not expr and selected_data:
            expr = (selected_data or {}).get('expr', '')
        if not expr:
            messagebox.showerror('Error', 'Debes ingresar una expresión o seleccionar una ecuación de la lista.')
            return

        # Determinar tolerancia
        tol = None
        if tol_input:
            try:
                tol = MetodoBiseccion.parse_tolerance(tol_input)
            except Exception as e:
                messagebox.showerror('Entrada inválida', f'Tolerancia inválida: {e}')
                return
        elif selected_data and selected_data.get('tol') is not None:
            tol = selected_data.get('tol')
        else:
            messagebox.showerror('Entrada inválida', 'Debes ingresar una tolerancia o seleccionar una ecuación con tolerancia guardada.')
            return

        # Determinar a y b usando prioridad: campos -> seleccionada -> auto-intervalo
        try:
            if a_txt:
                a = self._num_parse_number_str(a_txt)
            elif selected_data and selected_data.get('a') is not None:
                a = float(selected_data.get('a'))
            if b_txt:
                b = self._num_parse_number_str(b_txt)
            elif selected_data and selected_data.get('b') is not None:
                b = float(selected_data.get('b'))
        except Exception as e:
            messagebox.showerror('Entrada inválida', f'Error con los extremos: {e}')
            return

        if a is None or b is None:
            # intentar auto-intervalo
            try:
                res = self.mb_num.find_bracketing_interval(expr)
            except Exception as e:
                res = {"interval": None, "mensaje": str(e)}
            interval = None
            if isinstance(res, dict):
                interval = res.get('interval')
            elif isinstance(res, tuple) and len(res) >= 2:
                interval = (res[0], res[1])
            if interval is None:
                messagebox.showwarning('Intervalo', (res.get('mensaje') if isinstance(res, dict) else 'No se encontró intervalo válido.'))
                return
            try:
                a = float(interval[0]); b = float(interval[1])
            except Exception:
                messagebox.showwarning('Intervalo', f"Intervalo encontrado: {interval} (no se pudo convertir a float)")
                return

        try:
            if method == 'Bisección':
                res = self.mb_num.biseccion_dict(expr, a, b, tol, max_iter=self.mb_num.max_iter, mostrar_pasos=True)
            elif method == 'Falsa Posición':
                if self.mb_fp is None:
                    messagebox.showinfo('Dependencia faltante', 'El método Falsa Posición requiere sympy y numpy.\nInstálalos e inténtalo de nuevo.')
                    return
                # Adaptar a formato común { 'solucion': {...}, 'pasos': [...] }
                rows, result = self.mb_fp.solve(expr, a, b, tol)
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
                        'error': r.get('error')
                    })
                res = {
                    'solucion': {
                        'root': result.get('root'),
                        'iteraciones': result.get('iterations'),
                        'f_root': result.get('f_root'),
                        'abs_error': result.get('error')
                    },
                    'pasos': pasos,
                    'mensaje': None
                }
            elif method == 'Newton-Raphson':
                if self.mb_newton is None:
                    messagebox.showinfo('Dependencia faltante', 'El método Newton-Raphson requiere sympy y numpy.\nInstálalos e inténtalo de nuevo.')
                    return
                # Usar x0 como el punto medio del intervalo [a,b]
                try:
                    x0 = (float(a) + float(b)) / 2.0
                except Exception:
                    x0 = float(a)
                rows, result = self.mb_newton.solve(expr, x0=x0, tol=tol)
                pasos = []
                for r in rows:
                    # Mapear a las claves genéricas usadas por el visor de pasos
                    pasos.append({
                        'iter': r.get('Iteración'),
                        'a': r.get('x'),
                        'b': r.get('x_next'),
                        'c': r.get('x_next'),
                        'fa': r.get('f(x)'),
                        'fb': r.get("f'(x)"),
                        'fc': r.get('f(x)'),
                        'error': r.get('f(x)')
                    })
                res = {
                    'solucion': {
                        'root': result.get('root'),
                        'iteraciones': result.get('iterations'),
                        'f_root': result.get('f_root'),
                        'abs_error': result.get('abs_error') if result.get('abs_error') is not None else result.get('error')
                    },
                    'pasos': pasos,
                    'mensaje': result.get('mensaje')
                }
            elif method == 'Secante':
                if self.mb_secante is None:
                    messagebox.showinfo('Dependencia faltante', 'El método Secante requiere sympy y numpy.\nInstálalos e inténtalo de nuevo.')
                    return
                # Para Secante necesitamos dos puntos iniciales; usar a,b tal cual
                rows, result = self.mb_secante.solve(expr, x0=float(a), x1=float(b), tol=tol)
                pasos = []
                for r in rows:
                    pasos.append({
                        'iter': r.get('Iteración'),
                        'a': r.get('x_prev'),
                        'b': r.get('x'),
                        'c': r.get('x_next'),
                        'fa': r.get('f(x_prev)'),
                        'fb': r.get('f(x)'),
                        'fc': r.get('f(x)'),
                        'error': r.get('f(x)')
                    })
                res = {
                    'solucion': {
                        'root': result.get('root'),
                        'iteraciones': result.get('iterations'),
                        'f_root': result.get('f_root'),
                        'abs_error': result.get('abs_error') if result.get('abs_error') is not None else result.get('error')
                    },
                    'pasos': pasos,
                    'mensaje': result.get('mensaje')
                }
            else:
                messagebox.showerror('Método no soportado', method)
                return
        except Exception as e:
            messagebox.showerror('Error', f"Error durante {method}: {e}")
            return

        # Inyectar tolerancia en la solución para mostrarla en 'Resultado'
        try:
            if isinstance(res, dict) and isinstance(res.get('solucion'), dict):
                res['solucion']['tol'] = tol
        except Exception:
            pass

        # Guardar resultado y resetear modo (no modificar entradas)
        self.num_state['last_result'] = res
        self.num_state['last_method'] = method
        self.num_state['decimal_mode'] = False
        self.num_toggle_btn.config(text='Mostrar decimales')
        # Render principal en sección Resultado
        self._num_render_result(res, as_decimal=False)
        # Mantener limpia la sección de datos al resolver
        if hasattr(self, 'num_eq_data_text'):
            try:
                self.num_eq_data_text.delete(1.0, tk.END)
                # Volver a altura mínima para que no quede espacio vacío
                self.num_eq_data_text.configure(height=1)
            except Exception:
                pass

    def _num_plot_function(self):
        """Abre una ventana con el gráfico de f(x) para la ecuación actual.
        Usa [a,b] si está disponible; intenta detectar intervalo si no.
        """
        # Resolver expresión: de la entrada o de la ecuación seleccionada
        expr = self.num_expr_entry.get().strip()
        selected_data = None
        if (not expr) and getattr(self, 'selected_equation', None):
            try:
                from persistencia import cargar_ecuacion
                selected_data = cargar_ecuacion(self.selected_equation)
            except Exception:
                selected_data = None
            if selected_data:
                expr = (selected_data or {}).get('expr', '')
        if not expr:
            messagebox.showwarning('Falta expresión', 'Ingresa una expresión f(x) o selecciona una ecuación.')
            return

        # Determinar a y b si existen
        a_txt = self.num_a_entry.get().strip()
        b_txt = self.num_b_entry.get().strip()
        a = b = None
        try:
            if a_txt:
                a = self._num_parse_number_str(a_txt)
            elif selected_data and selected_data.get('a') is not None:
                a = float(selected_data.get('a'))
            if b_txt:
                b = self._num_parse_number_str(b_txt)
            elif selected_data and selected_data.get('b') is not None:
                b = float(selected_data.get('b'))
        except Exception:
            a = b = None

        # Preparar función numérica usando el parser del solver de Falsa Posición
        # Construir función numérica: preferir parser del solver; si no, fallback con math/numexpr
        try:
            from metodo_falsa_posicion import FalsePositionSolver as _FPS
            _, fnum = _FPS.parse_expression(expr)
        except Exception:
            # Fallback: eval con math en entorno controlado
            import math
            allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
            allowed.update({'pi': math.pi, 'e': math.e})
            def fnum(x):
                safe_expr = self._num_normalize_expr(expr).replace('^','**')
                safe_expr = re.sub(r'(?<=[0-9A-Za-z\)\]])\s+(?=[0-9A-Za-z\(\[])', '*', safe_expr)
                return eval(safe_expr, {'__builtins__': {}}, {**allowed, 'x': x})

        # Intervalo: usar [a,b] si válido; si no, intentar detectar uno; si falla, usar [-10,10]
        if a is None or b is None:
            try:
                interval = self.mb_fp.find_sign_change_interval(expr)
            except Exception:
                interval = None
            if interval is not None:
                a, b = interval
        if a is None or b is None or a == b:
            a, b = -10.0, 10.0
        if a > b:
            a, b = b, a

        # Intentar importar matplotlib y embeber en Toplevel
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except Exception:
            messagebox.showinfo('Dependencia faltante', 'Para mostrar la gráfica necesitas instalar matplotlib.\nSugerencia: pip install matplotlib')
            return

        import numpy as np
        xs = np.linspace(a, b, 600)
        ys = []
        for x in xs:
            try:
                y = float(fnum(x))
            except Exception:
                y = np.nan
            ys.append(y)
        ys = np.array(ys, dtype=float)

        win = tk.Toplevel(self.root)
        win.title('Gráfica de f(x)')
        win.configure(bg=self.palette["panel"])
        try:
            win.geometry('820x520')
        except Exception:
            pass

        fig = Figure(figsize=(7.6, 4.6), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(xs, ys, color='#00adb5', linewidth=2)
        ax.axhline(0, color='#888888', linewidth=1)
        ax.axvline(0, color='#888888', linewidth=1)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.set_title('f(x) = ' + expr)

        # Escalado: si el intervalo es muy pequeño, ajustar márgenes y límites de Y a datos
        try:
            import numpy as _np
            xw = float(b - a)
            # Añadir un pequeño margen relativo en X para que no quede demasiado "apretado"
            if _np.isfinite(xw) and xw > 0:
                ax.margins(x=0.04, y=0.12)
                # Mantener límites de X centrados en [a,b] con un pequeño padding proporcional
                pad_x = max(xw * 0.05, 0.0)
                ax.set_xlim(a - pad_x, b + pad_x)

            # Calcular límites Y basados en valores finitos dentro del intervalo actual
            finite = _np.isfinite(ys)
            if _np.any(finite):
                yvals = ys[finite]
                y_min = float(_np.nanmin(yvals))
                y_max = float(_np.nanmax(yvals))
                if _np.isfinite(y_min) and _np.isfinite(y_max):
                    if y_min == y_max:
                        # Si es casi constante, crear una ventana alrededor del valor
                        pad_y = max(1e-6, abs(y_min) * 0.1)
                        ax.set_ylim(y_min - pad_y, y_max + pad_y)
                    else:
                        y_range = y_max - y_min
                        pad_y = max(y_range * 0.12, 1e-12)
                        ax.set_ylim(y_min - pad_y, y_max + pad_y)
        except Exception:
            pass

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=win)
        # --- Interactividad: tooltip con coordenadas y punto seleccionado ---
        try:
            # dibujar líneas de intervalo (si existen)
            if a is not None:
                ax.axvline(a, color='green', linestyle='--', linewidth=1)
            if b is not None:
                ax.axvline(b, color='red', linestyle='--', linewidth=1)

            # anotación flotante (tooltip) y punto seleccionado
            annot = ax.annotate(
                "", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
                bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->")
            )
            annot.set_visible(False)
            sel_point, = ax.plot([], [], marker='o', color='orange', ms=6)

            def nearest_index(x_val):
                import numpy as _np
                if x_val is None:
                    return None
                i = _np.searchsorted(xs, x_val)
                cand = []
                if i > 0:
                    cand.append(i - 1)
                if i < len(xs):
                    cand.append(i)
                if not cand:
                    return None
                best = min(cand, key=lambda j: abs(xs[j] - x_val))
                return best

            x_range = xs.max() - xs.min() if len(xs) else 1.0
            x_threshold = x_range * 0.02  # 2% del rango

            def on_move(event):
                if event.inaxes != ax:
                    if annot.get_visible():
                        annot.set_visible(False)
                        sel_point.set_data([], [])
                        canvas.draw_idle()
                    return
                idx = nearest_index(event.xdata)
                if idx is None:
                    if annot.get_visible():
                        annot.set_visible(False)
                        sel_point.set_data([], [])
                        canvas.draw_idle()
                    return
                dx = abs(xs[idx] - event.xdata) if event.xdata is not None else float('inf')
                if dx <= x_threshold:
                    xpt = xs[idx]
                    ypt = ys[idx]
                    annot.xy = (xpt, ypt)
                    annot.set_text(f"x={xpt:.5f}\ny={ypt:.5f}")
                    annot.get_bbox_patch().set_alpha(0.9)
                    annot.set_visible(True)
                    sel_point.set_data([xpt], [ypt])
                    canvas.draw_idle()
                    return
                # cerca de los extremos a/b
                if a is not None and abs(event.xdata - a) <= x_threshold:
                    annot.xy = (a, 0)
                    annot.set_text(f"a = {a:.5f}")
                    annot.set_visible(True)
                    sel_point.set_data([], [])
                    canvas.draw_idle()
                    return
                if b is not None and abs(event.xdata - b) <= x_threshold:
                    annot.xy = (b, 0)
                    annot.set_text(f"b = {b:.5f}")
                    annot.set_visible(True)
                    sel_point.set_data([], [])
                    canvas.draw_idle()
                    return
                if annot.get_visible():
                    annot.set_visible(False)
                    sel_point.set_data([], [])
                    canvas.draw_idle()

            fig.canvas.mpl_connect("motion_notify_event", on_move)
        except Exception:
            # no romper la función si algo falla en la interactividad
            pass
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------- CRUD Ecuaciones ----------
    def _on_equation_select(self, event):
        sel = self.eq_listbox.curselection()
        if not sel:
            return
        # Solo guardar el nombre seleccionado; no rellenar campos de entrada
        self.selected_equation = self.eq_listbox.get(sel[0])
        # Salir de modo edición si estuviera activo (y quitar botón temporal)
        self._num_editing_name = None
        if hasattr(self, '_num_update_temp_btn') and self._num_update_temp_btn:
            try:
                self._num_update_temp_btn.destroy()
            except Exception:
                pass
            self._num_update_temp_btn = None

    def update_equation_list(self):
        if not hasattr(self, 'eq_listbox'):
            return
        from persistencia import cargar_todas_ecuaciones
        data = cargar_todas_ecuaciones()
        self.eq_listbox.delete(0, tk.END)
        if data:
            for name in data.keys():
                self.eq_listbox.insert(tk.END, name)
        try:
            next_name = self._next_available_letter(data.keys() if data else [])
            self.num_name_entry.delete(0, 'end')
            self.num_name_entry.insert(0, next_name)
        except Exception:
            pass

    def create_equation(self):
        from persistencia import cargar_todas_ecuaciones, guardar_ecuacion
        name = self.num_name_entry.get().strip()
        if not name or not name.isalpha() or not name.isupper() or len(name) != 1:
            messagebox.showerror("Nombre inválido", "El nombre debe ser una única letra mayúscula (A-Z).")
            return
        all_eq = cargar_todas_ecuaciones()
        if name in all_eq:
            messagebox.showerror("Nombre en uso", f"Ya existe una ecuación con el nombre '{name}'.")
            return
        data = self._collect_equation_form()
        if not data:
            return
        if guardar_ecuacion(name, data):
            messagebox.showinfo("Éxito", f"Ecuación '{name}' guardada.")
            self.update_equation_list()

    def _collect_equation_form(self):
        method = self.num_method_var.get()
        expr = self.num_expr_entry.get().strip()
        if not expr:
            messagebox.showerror("Error", "Debes ingresar una expresion o ecuacion en x.")
            return None
        try:
            tol = MetodoBiseccion.parse_tolerance(self.num_tol_entry.get())
        except Exception as e:
            messagebox.showerror("Entrada inválida", f"Tolerancia inválida: {e}")
            return None
        a_txt = self.num_a_entry.get().strip()
        b_txt = self.num_b_entry.get().strip()
        a = self._num_parse_number_str(a_txt) if a_txt else None
        b = self._num_parse_number_str(b_txt) if b_txt else None
        return {
            'metodo': method,
            'expr': expr,
            'a': a,
            'b': b,
            'tol': tol,
        }

    def view_equation(self):
        from persistencia import cargar_ecuacion
        sel = self.eq_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona una ecuación para ver.")
            return
        name = self.eq_listbox.get(sel[0])
        data = cargar_ecuacion(name)
        if not data:
            messagebox.showerror("Error", f"No se pudo cargar la ecuación '{name}'.")
            return
        # Mostrar en sección Datos de la ecuación (no en Resultado)
        if hasattr(self, 'num_eq_data_text'):
            self.num_eq_data_text.delete(1.0, tk.END)
            self.num_eq_data_text.insert(tk.END, f"Ecuación: {name}\n")
            self.num_eq_data_text.insert(tk.END, f"Método: {data.get('metodo')}\n")
            self.num_eq_data_text.insert(tk.END, f"f(x): {data.get('expr')}\n")
            self.num_eq_data_text.insert(tk.END, f"a: {data.get('a')}\n")
            self.num_eq_data_text.insert(tk.END, f"b: {data.get('b')}\n")
            self.num_eq_data_text.insert(tk.END, f"tolerancia: {data.get('tol')}\n")
            # Ajustar altura al contenido mostrado
            try:
                self._num_eqdata_autosize(min_lines=1, max_lines=8)
            except Exception:
                pass
        else:
            # Fallback por si no se creó el widget
            self.num_result_text.delete(1.0, tk.END)
            self.num_result_text.insert(tk.END, f"[Datos ecuación]\nEcuación: {name}\nMétodo: {data.get('metodo')}\n" \
                                         f"f(x): {data.get('expr')}\n" \
                                         f"a: {data.get('a')}\n" \
                                         f"b: {data.get('b')}\n" \
                                         f"tolerancia: {data.get('tol')}\n")

    def modify_equation_ui(self):
        from persistencia import cargar_ecuacion
        sel = self.eq_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona una ecuación para modificar.")
            return
        name = self.eq_listbox.get(sel[0])
        data = cargar_ecuacion(name)
        if not data:
            messagebox.showerror("Error", f"No se pudo cargar la ecuación '{name}'.")
            return
        # Prellenar campos
        self.num_name_entry.delete(0, 'end'); self.num_name_entry.insert(0, name)
        self.num_method_var.set(data.get('metodo','Bisección'))
        self.num_expr_entry.delete(0, 'end'); self.num_expr_entry.insert(0, data.get('expr',''))
        self.num_a_entry.delete(0, 'end'); self.num_b_entry.delete(0, 'end')
        if data.get('a') is not None:
            self.num_a_entry.insert(0, str(data.get('a')))
        if data.get('b') is not None:
            self.num_b_entry.insert(0, str(data.get('b')))
        self.num_tol_entry.delete(0, 'end'); self.num_tol_entry.insert(0, str(data.get('tol','1e-6')))
        self._num_editing_name = name
        # Cambiar botón Crear a Actualizar temporalmente
        # Creamos un botón efímero
        if hasattr(self, '_num_update_temp_btn') and self._num_update_temp_btn:
            try:
                self._num_update_temp_btn.destroy()
            except Exception:
                pass
        # Botón de actualizar aparece a la derecha de "Mostrar decimales" en la misma fila
        parent_for_update = getattr(self, 'eq_toggle_buttons', self.num_content_container)
        self._num_update_temp_btn = ttk.Button(parent_for_update, text='Actualizar ecuación', style='Dark.TButton', command=self.update_equation_data)
        try:
            # Si el padre es el contenedor de toggle, usar pack a la derecha del botón de decimales
            if parent_for_update is self.eq_toggle_buttons:
                self._num_update_temp_btn.pack(side=tk.LEFT, padx=5)
            else:
                # Fallback si no existe el contenedor aún
                self._num_update_temp_btn.grid(row=7, column=0, columnspan=4, pady=(8,0))
        except Exception:
            # En caso de cualquier problema, usar grid en una fila segura
            try:
                self._num_update_temp_btn.grid(row=7, column=0, columnspan=4, pady=(8,0))
            except Exception:
                pass

    def update_equation_data(self):
        from persistencia import actualizar_ecuacion
        if not self._num_editing_name:
            return
        new_name = self.num_name_entry.get().strip()
        if new_name != self._num_editing_name:
            messagebox.showerror('Nombre no editable', 'Para simplificar, el nombre no se puede cambiar al actualizar. (Elimina y vuelve a crear si quieres renombrar).')
            return
        data = self._collect_equation_form()
        if not data:
            return
        if actualizar_ecuacion(self._num_editing_name, data):
            messagebox.showinfo('Éxito', f"Ecuación '{self._num_editing_name}' actualizada.")
            self.update_equation_list()
        if hasattr(self, '_num_update_temp_btn') and self._num_update_temp_btn:
            try:
                self._num_update_temp_btn.destroy()
            except Exception:
                pass
        self._num_editing_name = None

    def delete_equation(self):
        from persistencia import eliminar_ecuacion
        sel = self.eq_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona una ecuación para eliminar.")
            return
        name = self.eq_listbox.get(sel[0])
        if messagebox.askyesno('Confirmar', f"¿Seguro que quieres eliminar la ecuación '{name}'?"):
            if eliminar_ecuacion(name):
                messagebox.showinfo('Éxito', f"Ecuación '{name}' eliminada.")
                self.update_equation_list()

    def _num_auto_interval(self):
        expr = self.num_expr_entry.get().strip()
        try:
            res = self.mb_num.find_bracketing_interval(expr)
        except Exception as e:
            messagebox.showerror('Error', f'Error buscando intervalo: {e}')
            return
        interval = None
        if isinstance(res, dict):
            interval = res.get('interval')
            mensaje = res.get('mensaje')
        elif isinstance(res, tuple) and len(res) >= 2:
            interval = (res[0], res[1])
            mensaje = None
        else:
            mensaje = None
        if interval is None:
            messagebox.showinfo('Intervalo', mensaje or 'No se encontró intervalo con cambio de signo.')
            return
        try:
            a_found = float(interval[0]); b_found = float(interval[1])
        except Exception:
            messagebox.showinfo('Intervalo', f'Intervalo encontrado: {interval}\n(No se pudo convertir a float)')
            return
        use = messagebox.askyesno('Intervalo encontrado', f"Se encontró intervalo: a={a_found}, b={b_found}\n¿Usar este intervalo?")
        if use:
            self.num_a_entry.delete(0, 'end'); self.num_a_entry.insert(0, str(a_found))
            self.num_b_entry.delete(0, 'end'); self.num_b_entry.insert(0, str(b_found))

    def _insert_math_token(self, token, cursor_offset=None):
        """Inserta un token LaTeX/matemático en el campo de expresión y posiciona el cursor si se indica."""
        try:
            entry = self.num_expr_entry
        except Exception:
            return
        pos = entry.index(tk.INSERT)
        entry.insert(pos, token)
        if cursor_offset is not None:
            try:
                entry.icursor(pos + cursor_offset)
            except Exception:
                pass
        try:
            entry.focus_set()
        except Exception:
            pass
        self._update_latex_preview()

    def _format_expr_fractions(self, expr: str) -> str:
        """Convierte divisiones simples en \\frac{num}{den} para que se vean como fraccion en LaTeX."""
        def _read_token_forward(s, start):
            if start >= len(s):
                return None, start
            ch = s[start]
            if ch in '([':
                open_ch = ch
                close_ch = ')' if ch == '(' else ']'
                depth = 1
                j = start + 1
                while j < len(s) and depth > 0:
                    if s[j] == open_ch:
                        depth += 1
                    elif s[j] == close_ch:
                        depth -= 1
                    j += 1
                return s[start:j], j - 1
            j = start
            while j < len(s) and (s[j].isalnum() or s[j] in '._'):
                j += 1
            if j == start:
                return None, start
            return s[start:j], j - 1

        def _read_token_backward(s, start):
            if start < 0:
                return None, start
            ch = s[start]
            if ch in ')]':
                close_ch = ch
                open_ch = '(' if ch == ')' else '['
                depth = 1
                j = start - 1
                while j >= 0 and depth > 0:
                    if s[j] == close_ch:
                        depth += 1
                    elif s[j] == open_ch:
                        depth -= 1
                    j -= 1
                return s[j + 1:start + 1], j + 1
            j = start
            while j >= 0 and (s[j].isalnum() or s[j] in '._'):
                j -= 1
            if j >= 0 and s[j] == '-':
                j -= 1
            if j == start:
                return None, start
            return s[j + 1:start + 1], j + 1

        res = []
        cursor = 0
        i = 0
        while i < len(expr):
            if expr[i] != '/':
                i += 1
                continue
            num_token, num_start = _read_token_backward(expr, i - 1)
            den_token, den_end = _read_token_forward(expr, i + 1)
            if num_token and den_token:
                # Agregar texto pendiente antes del numerador y la fraccion formateada
                res.append(expr[cursor:num_start])
                res.append(f"\\frac{{{num_token}}}{{{den_token}}}")
                cursor = den_end + 1
                i = den_end + 1
            else:
                i += 1
        res.append(expr[cursor:])
        return ''.join(res)

    def _format_expr_exponents(self, expr: str) -> str:
        """Agrupa exponentes para que matplotlib los muestre completos (p.ej. x^-1 -> x^{-1})."""
        res = []
        i = 0
        while i < len(expr):
            ch = expr[i]
            if ch != '^':
                res.append(ch)
                i += 1
                continue

            # Procesar exponente
            res.append('^')
            i += 1
            if i >= len(expr):
                break
            nxt = expr[i]

            # Si ya viene en llaves, dejarlo tal cual
            if nxt == '{':
                res.append('{')
                i += 1
                continue

            # Agrupar paréntesis o corchetes completos
            if nxt in '([':
                open_ch = nxt
                close_ch = ')' if nxt == '(' else ']'
                depth = 1
                j = i + 1
                while j < len(expr) and depth > 0:
                    if expr[j] == open_ch:
                        depth += 1
                    elif expr[j] == close_ch:
                        depth -= 1
                    j += 1
                res.append('{')
                res.append(expr[i:j])
                res.append('}')
                i = j
                continue

            # Capturar tokens simples (numeros, variables, signos)
            start = i
            if nxt == '-':
                i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] in '._'):
                i += 1
            segment = expr[start:i]
            if segment:
                res.append('{')
                res.append(segment)
                res.append('}')
            else:
                res.append(nxt)
                i += 1
        return ''.join(res)

    def _update_latex_preview(self):
        """Renderiza la vista previa en LaTeX usando matplotlib (sin escribir archivos)."""
        expr = ""
        try:
            expr = self.num_expr_entry.get().strip()
        except Exception:
            return
        if not expr:
            self.num_expr_preview.config(text="Vista previa LaTeX", image=None, bg="#ffffff", fg="#0b0b0b", anchor='w', justify='left')
            self._latex_preview_image = None
            return
        # Ajustar fracciones y exponentes para que se muestren completos en LaTeX
        expr_latex = self._format_expr_exponents(self._format_expr_fractions(expr))
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg

            expr_len = len(expr)
            base_fs = 26
            fs = base_fs if expr_len <= 20 else max(14, base_fs - (expr_len - 20) * 0.5)

            fig = Figure(figsize=(6.4, 1.2), dpi=150)
            fig.patch.set_facecolor("#ffffff")
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_facecolor("#ffffff")
            ax.axis('off')
            ax.text(0.02, 0.55, f"${expr_latex}$", fontsize=fs, va='center', ha='left', color="#0b0b0b")

            buf = io.BytesIO()
            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            canvas.print_png(buf)
            buf.seek(0)
            b64 = base64.b64encode(buf.getvalue())
            # tkinter PhotoImage acepta PNG base64
            self._latex_preview_image = tk.PhotoImage(data=b64)
            self.num_expr_preview.config(image=self._latex_preview_image, text="", bg="#ffffff")
            # Si por alguna razón el render no produjo imagen, mostrar texto plano
            try:
                if not self._latex_preview_image or self._latex_preview_image.width() == 0:
                    raise ValueError("Imagen LaTeX vacía")
            except Exception:
                self.num_expr_preview.config(text=expr, image=None, fg="#0b0b0b", bg="#ffffff")
                self._latex_preview_image = None
        except Exception:
            # Fallback: mostrar texto plano si falla el render
            self.num_expr_preview.config(text=expr, image=None, fg="#0b0b0b", bg="#ffffff")
            self._latex_preview_image = None

    def _num_toggle_decimal(self):
        if not self.num_state.get('last_result'):
            messagebox.showinfo('Info', 'No hay resultados para convertir. Ejecuta el método primero.')
            return
        self.num_state['decimal_mode'] = not self.num_state['decimal_mode']
        self._num_render_result(self.num_state['last_result'], as_decimal=self.num_state['decimal_mode'])
        self.num_toggle_btn.config(text='Mostrar fracciones' if self.num_state['decimal_mode'] else 'Mostrar decimales')

    def create_operators_widgets(self, parent_frame):
        """Crea la pestaña para operar conjuntos de matrices (sumar, restar, multiplicar)."""
        # Contenedor con scroll (izquierda) + Procedimiento a la derecha
        main_frame = ttk.Frame(parent_frame, style='Surface.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        ops_content_stack = ttk.Frame(main_frame, style='Surface.TFrame')
        ops_content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.ops_canvas = tk.Canvas(ops_content_stack, bg=self.palette["panel"], highlightthickness=0, bd=0)
        ops_scrollbar = ttk.Scrollbar(ops_content_stack, orient=tk.VERTICAL, command=self.ops_canvas.yview, style='Invisible.Vertical.TScrollbar')
        try:
            ops_scrollbar.configure(width=1)
        except Exception:
            pass
        self.ops_scrollable_frame = ttk.Frame(self.ops_canvas, style='Dark.TFrame')
        self.ops_scrollable_frame.bind(
            "<Configure>", lambda e: self.ops_canvas.configure(scrollregion=self.ops_canvas.bbox("all"))
        )
        self.ops_canvas_window = self.ops_canvas.create_window((0, 0), window=self.ops_scrollable_frame, anchor="nw")
        self.ops_canvas.bind("<Configure>", lambda e: self.ops_canvas.itemconfig(self.ops_canvas_window, width=e.width))
        self.ops_canvas.configure(yscrollcommand=ops_scrollbar.set)
        self.ops_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ops_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bindeo de la rueda del ratón para esta pestaña
        self.ops_scrollable_frame.bind("<Enter>", self._bound_to_mousewheel_ops)
        self.ops_scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel_ops)

        # Panel de Procedimiento a la derecha (fijo)
        self.ops_proc_panel = ttk.Frame(main_frame, style='Card.TFrame', padding=(14, 12))
        self.ops_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12,0), pady=4)
        ttk.Label(self.ops_proc_panel, text="Procedimiento", style='CardTitle.TLabel').pack(anchor='nw', pady=(6,6))
        ops_steps_container = ttk.Frame(self.ops_proc_panel, style='Card.TFrame')
        ops_steps_container.pack(fill=tk.BOTH, expand=True)
        ops_steps_container.rowconfigure(0, weight=1)
        ops_steps_container.columnconfigure(0, weight=1)
        self.ops_steps_text = tk.Text(ops_steps_container, font=('Consolas', 12), bg=self.palette["card_alt"], fg=self.palette["text"], insertbackground=self.palette["text"], bd=0, highlightthickness=0, width=50, wrap='word')
        self.ops_steps_text.grid(row=0, column=0, sticky='nsew')
        steps_scrollbar_ops_right = ttk.Scrollbar(ops_steps_container, orient=tk.VERTICAL, command=self.ops_steps_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            steps_scrollbar_ops_right.configure(width=1)
        except Exception:
            pass
        steps_scrollbar_ops_right.grid(row=0, column=1, sticky='ns')
        self.ops_steps_text.configure(yscrollcommand=steps_scrollbar_ops_right.set)

    # Wrapper centrado
        self.ops_center_wrapper = ttk.Frame(self.ops_scrollable_frame, style='Surface.TFrame')
        self.ops_center_wrapper.pack(fill='x', expand=True)
        # Distribución: 0 = panel izquierdo (no expandir), 1 = contenido (expandir), 2 = separador derecho (no expandir)
        self.ops_center_wrapper.grid_columnconfigure(0, weight=0)
        self.ops_center_wrapper.grid_columnconfigure(1, weight=1)
        self.ops_center_wrapper.grid_columnconfigure(2, weight=0)
        self.ops_content_container = ttk.Frame(self.ops_center_wrapper, style='Surface.TFrame')
        # Mover contenido a la izquierda con margen respecto al panel lateral
        self.ops_content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')  # <-- Ajusta margen contenido (Operadores)

        # --- Panel lateral izquierdo para Conjuntos de Matrices (Operadores) ---
        self.ops_center_wrapper.grid_rowconfigure(0, weight=1)
        self.ops_left_panel = ttk.Frame(self.ops_center_wrapper, style='Card.TFrame', padding=(10, 10))
        # Coordenadas panel izquierdo (Operadores): esquina superior izquierda
        self.ops_left_panel.grid(row=0, column=0, sticky='nsw', padx=(0,10), pady=(0,0))  # <-- Coordenadas/Tamaño panel lateral (Operadores)
        self.ops_left_panel.grid_columnconfigure(0, weight=1)
        self.ops_left_panel.grid_rowconfigure(1, weight=1)  # <-- La fila 1 contendrá la lista; se estira en Y

        container = self.ops_content_container
        # Ocho columnas para alinear Nombre / Nº Matrices / Filas / Columnas / Operación en una sola fila
        for c in range(8):
            container.grid_columnconfigure(c, weight=1)

        # Cabecera destacada
        self._add_tab_header(
            container,
            "Operadores de Matrices",
            "Crea conjuntos, combina matrices y sigue el procedimiento en paralelo.",
            columns=8,
        )

        # Controles superiores
        ops_form_card = ttk.Frame(container, style='Card.TFrame', padding=(16, 14))
        ops_form_card.grid(row=1, column=0, columnspan=8, sticky='ew', pady=(0, 12))
        for c in range(8):
            ops_form_card.grid_columnconfigure(c, weight=1)

        ttk.Label(ops_form_card, text="Nombre del conjunto:", style='Dark.TLabel').grid(row=0, column=0, sticky='w', pady=(0,4))
        self.ops_name_entry = ttk.Entry(ops_form_card, width=18, style='Entry.TEntry')
        self.ops_name_entry.grid(row=0, column=1, sticky='w', padx=(0, 20))

        ttk.Label(ops_form_card, text="Nº Matrices:", style='Dark.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.num_mats_var = tk.StringVar(value="0")
        num_mats_spin = tk.Spinbox(ops_form_card, from_=1, to=10, width=6, textvariable=self.num_mats_var, bg=self.palette["input"], fg=self.palette["text"])
        num_mats_spin.grid(row=1, column=1, sticky='w', padx=(0, 20))

        ttk.Label(ops_form_card, text="Filas:", style='Dark.TLabel').grid(row=1, column=2, sticky='e')
        self.ops_rows_var = tk.StringVar(value="0")
        ops_rows_spin = tk.Spinbox(ops_form_card, from_=1, to=20, width=6, textvariable=self.ops_rows_var, bg=self.palette["input"], fg=self.palette["text"])
        ops_rows_spin.grid(row=1, column=3, sticky='w')

        ttk.Label(ops_form_card, text="Columnas:", style='Dark.TLabel').grid(row=1, column=4, sticky='e')
        self.ops_cols_var = tk.StringVar(value="0")
        ops_cols_spin = tk.Spinbox(ops_form_card, from_=1, to=20, width=6, textvariable=self.ops_cols_var, bg=self.palette["input"], fg=self.palette["text"])
        ops_cols_spin.grid(row=1, column=5, sticky='w')

        # Selector de operación al lado derecho de Filas y Columnas
        ttk.Label(ops_form_card, text="Operacion:", style='Dark.TLabel').grid(row=1, column=6, sticky='e', padx=(10,5))
        self.ops_method_var = tk.StringVar(value=" ")
        self.ops_method_combobox = ttk.Combobox(ops_form_card, textvariable=self.ops_method_var, values=["Suma", "Resta", "Multiplicacion", "Multiplicacion escalar", "Transponer", "Inversa", "Determinante", "Independencia"], state="readonly", width=18)
        self.ops_method_combobox.grid(row=1, column=7, sticky='w')

        ttk.Label(ops_form_card, text="Escalar:", style='Dark.TLabel').grid(row=2, column=0, sticky='w', pady=4)
        self.ops_scalar_var = tk.StringVar(value="1")
        self.ops_scalar_entry = ttk.Entry(ops_form_card, textvariable=self.ops_scalar_var, width=12, style='Entry.TEntry')
        self.ops_scalar_entry.grid(row=2, column=1, sticky='w', padx=(0, 20))

        ttk.Button(ops_form_card, text="Crear Conjunto de Matrices", style='Dark.TButton', command=self.create_matrix_set_ui).grid(row=3, column=0, columnspan=8, pady=(10, 20), sticky='ew')

        # Lista de conjuntos + acciones
        # --- Lista de Conjuntos de Matrices en panel lateral izquierdo (Operadores) ---
        ttk.Label(self.ops_left_panel, text="Conjuntos de Matrices Almacenados:", style='Dark.TLabel')\
            .grid(row=0, column=0, sticky='nw', pady=(12,5), padx=(20,0))  # <-- Coordenadas etiqueta (Operadores)
        ops_list_frame = ttk.Frame(self.ops_left_panel, style='Card.TFrame')
        ops_list_frame.grid_propagate(False)
        ops_list_frame.configure(width=260, height=690)
        ops_list_frame.grid(row=1, column=0, sticky='nsew', pady=(0,10), padx=(20,0))  # <-- Coordenadas/Tamaño lista (Operadores)
        ops_list_frame.grid_columnconfigure(0, weight=1)
        ops_list_frame.grid_rowconfigure(0, weight=1)
        self.matrix_set_listbox = tk.Listbox(ops_list_frame, height=6, font=('Segoe UI', 11), bg=self.palette["input"], fg=self.palette["text"], selectbackground=self.palette["accent"], selectforeground=self.palette["background"], borderwidth=0, highlightthickness=0, exportselection=0)
        self.matrix_set_listbox.grid(row=0, column=0, sticky='nsew')
        ops_scrollbar_list = ttk.Scrollbar(ops_list_frame, orient=tk.VERTICAL, command=self.matrix_set_listbox.yview, style='Invisible.Vertical.TScrollbar')
        try:
            ops_scrollbar_list.configure(width=1)
        except Exception:
            pass
        ops_scrollbar_list.grid(row=0, column=1, sticky='ns')  # <-- Side bar (scroll) asociado a la lista (Operadores)
        self.matrix_set_listbox.configure(yscrollcommand=ops_scrollbar_list.set)
        self.matrix_set_listbox.bind('<<ListboxSelect>>', self._on_matrix_set_select)

        # Botonera centrada (alinea con "Crear Conjunto de Matrices")
        ops_action_frame = ttk.Frame(ops_form_card, style='Card.TFrame')
        ops_action_frame.grid(row=4, column=0, columnspan=8, pady=(0, 4))
        ops_action_buttons = ttk.Frame(ops_action_frame, style='Surface.TFrame')
        ops_action_buttons.pack(anchor='center')
        ttk.Button(ops_action_buttons, text="Ver", style='Dark.TButton', command=self.view_matrix_set).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_action_buttons, text="Modificar", style='Dark.TButton', command=self.modify_matrix_set_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_action_buttons, text="Eliminar", style='Dark.TButton', command=self.delete_matrix_set).pack(side=tk.LEFT, padx=5)
        # Botón Resolver al lado derecho de Eliminar
        ttk.Button(ops_action_buttons, text="Resolver", style='Dark.TButton', command=self.run_matrix_operation).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_action_buttons, text="Limpiar", style='Dark.TButton', command=self.clear_ops_tab).pack(side=tk.LEFT, padx=5)

        # Área de entradas de matrices
        ttk.Label(container, text="Datos del conjunto:", style='CardTitle.TLabel').grid(row=2, column=0, columnspan=8, sticky='w', pady=(10,5))
        self.ops_entries_frame = ttk.Frame(container, style='Card.TFrame', padding=(12, 10))
        self.ops_entries_frame.grid(row=3, column=0, columnspan=8, sticky='ew', pady=(0,10))


        # Resultados
        results_container = ttk.Frame(container, style='Card.TFrame', padding=(14, 12))
        results_container.grid(row=4, column=0, columnspan=8, sticky='nsew', pady=(10,0))
        results_container.grid_rowconfigure(1, weight=1)
        results_container.grid_columnconfigure(0, weight=1)
        ttk.Label(results_container, text="Resultado", style='CardTitle.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        solution_frame_ops = ttk.Frame(results_container)
        solution_frame_ops.grid(row=1, column=0, sticky='nsew')
        solution_frame_ops.grid_rowconfigure(0, weight=1)
        solution_frame_ops.grid_columnconfigure(0, weight=1)
        self.ops_result_text = tk.Text(solution_frame_ops, height=16, width=79, font=('Segoe UI', 13), bg=self.palette["card_alt"], fg=self.palette["accent_soft"], insertbackground=self.palette["text"], bd=0, highlightthickness=0, wrap='word')
        self.ops_result_text.grid(row=0, column=0, sticky='nsew')
        result_scrollbar_ops = ttk.Scrollbar(solution_frame_ops, orient=tk.VERTICAL, command=self.ops_result_text.yview, style='Invisible.Vertical.TScrollbar')
        try:
            result_scrollbar_ops.configure(width=1)
        except Exception:
            pass
        result_scrollbar_ops.grid(row=0, column=1, sticky='ns')
        self.ops_result_text.configure(yscrollcommand=result_scrollbar_ops.set)

    # (Procedimiento movido al panel derecho)

    def _on_matrix_set_select(self, event):
        sel = self.matrix_set_listbox.curselection()
        if sel:
            self.selected_matrix_set = self.matrix_set_listbox.get(sel[0])

    def _next_available_letter(self, existing_names):
        """Devuelve la primera letra A-Z no usada en existing_names. Si todas ocupadas, retorna Z."""
        if not existing_names:
            return "A"
        used = set(str(n).strip().upper() for n in existing_names if isinstance(n, str))
        for code in range(ord('A'), ord('Z') + 1):
            letter = chr(code)
            if letter not in used:
                return letter
        return "Z"

    def update_matrix_set_list(self):
        if not hasattr(self, 'matrix_set_listbox'):
            return
        self.matrix_set_listbox.delete(0, tk.END)
        data = persistencia.cargar_todos_conjuntos_matrices()
        if data:
            for name in data.keys():
                self.matrix_set_listbox.insert(tk.END, name)
        try:
            next_name = self._next_available_letter(data.keys() if data else [])
            self.ops_name_entry.delete(0, tk.END)
            self.ops_name_entry.insert(0, next_name)
        except Exception:
            pass

    def create_matrix_set_ui(self):
        name = self.ops_name_entry.get().strip()
        if not name or not name.isalpha() or not name.isupper() or len(name) != 1:
            messagebox.showerror("Nombre inválido", "El nombre del conjunto debe ser una única letra mayúscula (A-Z).")
            return
        if name in persistencia.cargar_todos_conjuntos_matrices():
            messagebox.showerror("Nombre en uso", f"Ya existe un conjunto de matrices con el nombre '{name}'.")
            return
        try:
            num_m = int(self.num_mats_var.get())
            r = int(self.ops_rows_var.get())
            c = int(self.ops_cols_var.get())
            if num_m <= 0 or r <= 0 or c <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Nº de matrices, filas y columnas deben ser enteros positivos.")
            return
        self.draw_operator_entries(num_m, r, c, name)

    def draw_operator_entries(self, num_matrices, filas, columnas, name, is_modification=False, data=None):
        for w in self.ops_entries_frame.winfo_children():
            w.destroy()
        if is_modification:
            self.original_matrix_set_data_for_modification = {
                'num_matrices': num_matrices,
                'filas': filas,
                'columnas': columnas,
                'datos': [ [row[:] for row in mat] for mat in data ] if data else []
            }
        # Construir rejillas por cada matriz
        self.ops_entries = []
        for idx in range(num_matrices):
            grp = ttk.LabelFrame(self.ops_entries_frame, text=f"M{idx+1}", style='Dark.TFrame')
            grp.grid(row=idx//2, column=idx%2, padx=8, pady=6, sticky='w')
            mat_entries = []
            for i in range(filas):
                row_entries = []
                for j in range(columnas):
                    e = ttk.Entry(grp, width=8, style='Entry.TEntry')
                    default_value = "0"
                    if data and idx < len(data) and i < len(data[idx]) and j < len(data[idx][i]):
                        default_value = str(data[idx][i][j])
                    e.insert(0, default_value)
                    e.grid(row=i, column=j, padx=2, pady=2)
                    row_entries.append(e)
                mat_entries.append(row_entries)
            self.ops_entries.append(mat_entries)

        # Botonera
        btn_frame = ttk.Frame(self.ops_entries_frame, style='Dark.TFrame')
        btn_frame.grid(row=(num_matrices+1)//2 + 1, column=0, columnspan=2, sticky='ew', pady=(10,0))
        text = "Actualizar Conjunto" if is_modification else "Guardar Conjunto"
        cmd = (lambda: self.update_matrix_set_data(self.ops_entries, num_matrices, filas, columnas, name)) if is_modification \
              else (lambda: self.save_matrix_set_data(self.ops_entries, num_matrices, filas, columnas, name))
        ttk.Button(btn_frame, text=text, style='Dark.TButton', command=cmd).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ttk.Button(btn_frame, text="Cancelar", style='Dark.TButton', command=lambda: [w.destroy() for w in self.ops_entries_frame.winfo_children()]).pack(side=tk.LEFT, expand=True, fill='x', padx=2)

    def _extract_matrix_set_values(self, entries):
        mats = []
        for mat in entries:
            mats.append([[float(e.get()) for e in row] for row in mat])
        return mats

    def save_matrix_set_data(self, entries, num_matrices, filas, columnas, name):
        try:
            datos = self._extract_matrix_set_values(entries)
            if crear_conjunto_matrices(name, num_matrices, filas, columnas, datos):
                messagebox.showinfo("Éxito", f"Conjunto de matrices '{name}' guardado.")
                self.update_matrix_set_list()
                self.ops_name_entry.delete(0, tk.END)
                self.num_mats_var.set("0")
                self.ops_rows_var.set("0")
                self.ops_cols_var.set("0")
                for w in self.ops_entries_frame.winfo_children():
                    w.destroy()
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos.")

    def modify_matrix_set_ui(self):
        sel = self.matrix_set_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona un conjunto de matrices para modificar.")
            return
        name = self.matrix_set_listbox.get(sel[0])
        data = persistencia.cargar_conjunto_matrices(name)
        if not data:
            messagebox.showerror("Error", f"No se pudo cargar el conjunto '{name}'.")
            return
        self.draw_operator_entries(data['num_matrices'], data['filas'], data['columnas'], name, is_modification=True, data=data['datos'])

    def update_matrix_set_data(self, entries, num_matrices, filas, columnas, name):
        try:
            datos = self._extract_matrix_set_values(entries)
            orig = self.original_matrix_set_data_for_modification
            if orig['num_matrices'] == num_matrices and orig['filas'] == filas and orig['columnas'] == columnas and orig['datos'] == datos:
                for w in self.ops_entries_frame.winfo_children():
                    w.destroy()
                return
            if actualizar_conjunto_matrices(name, datos, num_matrices, filas, columnas):
                messagebox.showinfo("Éxito", f"Conjunto '{name}' actualizado.")
                self.update_matrix_set_list()
                for w in self.ops_entries_frame.winfo_children():
                    w.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el conjunto '{name}'.")
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de que todos los valores sean números válidos.")

    def delete_matrix_set(self):
        sel = self.matrix_set_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona un conjunto para eliminar.")
            return
        name = self.matrix_set_listbox.get(sel[0])
        if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar el conjunto '{name}'?"):
            if persistencia.eliminar_conjunto_matrices(name):
                messagebox.showinfo("Éxito", f"Conjunto '{name}' eliminado.")
                self.update_matrix_set_list()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el conjunto '{name}'.")

    def view_matrix_set(self):
        sel = self.matrix_set_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selección requerida", "Selecciona un conjunto de matrices para ver.")
            return
        name = self.matrix_set_listbox.get(sel[0])
        data = persistencia.cargar_conjunto_matrices(name)
        if not data:
            messagebox.showerror("Error", f"No se encontró el conjunto '{name}'.")
            return
        # Limpiar y mostrar
        for w in self.ops_entries_frame.winfo_children():
            w.destroy()
        self.ops_result_text.delete(1.0, tk.END)
        self.ops_steps_text.delete(1.0, tk.END)
        info = (f"Conjunto: {data['nombre']}\n"
                f"Nº Matrices: {data['num_matrices']}\n"
                f"Dimensiones: {data['filas']}x{data['columnas']}\n\n")
        # Mostrar cada matriz con formato
        display = info
        for idx, mat in enumerate(data['datos'], start=1):
            display += f"M{idx}:\n" + self._format_matrix_for_display(mat) + "\n"
        lbl = ttk.Label(self.ops_entries_frame, text=display, style='Result.TLabel', justify=tk.LEFT)
        lbl.pack(pady=10, padx=10, anchor='w')


    def run_matrix_operation(self):
        sel = self.matrix_set_listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleccion requerida", "Selecciona un conjunto de matrices.")
            return
        name = self.matrix_set_listbox.get(sel[0])
        data = persistencia.cargar_conjunto_matrices(name)
        if not data:
            messagebox.showerror("Error", f"No se pudo cargar el conjunto '{name}'.")
            return
        mats = [matrices.Matriz(m) for m in data['datos']]
        op = self.ops_method_var.get()
        try:
            self.ops_result_text.delete(1.0, tk.END)
            self.ops_steps_text.delete(1.0, tk.END)

            def fmt_val(v):
                try:
                    f = float(v)
                    s = ("{:.6f}".format(f)).rstrip('0').rstrip('.')
                    return s if s else "0"
                except Exception:
                    return str(v)

            def show_matrix_block(title, mat_list):
                self.ops_steps_text.insert(tk.END, f"{title}\\n")
                self.ops_steps_text.insert(tk.END, self._format_matrix_for_display(mat_list))
                self.ops_steps_text.insert(tk.END, "\\n\\n")

            if op == "Suma":
                self.ops_steps_text.insert(tk.END, "Suma de matrices\n------------------\n\n")
                for idx, m in enumerate(mats, start=1):
                    show_matrix_block(f"M{idx}:", m.to_list())
                res = mats[0]
                paso = 1
                for idx, M in enumerate(mats[1:], start=2):
                    A = res.to_list(); B = M.to_list()
                    R = res.sumar(M).to_list()
                    self.ops_steps_text.insert(tk.END, f"Paso {paso}: R{paso} = {'R'+str(paso-1) if paso>1 else 'M1'} + M{idx}\\n")
                    for i in range(len(A)):
                        for j in range(len(A[0])):
                            self.ops_steps_text.insert(tk.END, f"  r[{i+1},{j+1}] = {fmt_val(A[i][j])} + {fmt_val(B[i][j])} = {fmt_val(R[i][j])}\\n")
                    show_matrix_block("Resultado parcial:", R)
                    res = matrices.Matriz(R)
                    paso += 1
                self.ops_result_text.insert(tk.END, "Resultado de la suma:\\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))

            elif op == "Resta":
                self.ops_steps_text.insert(tk.END, "Resta de matrices\n-----------------\n\n")
                for idx, m in enumerate(mats, start=1):
                    show_matrix_block(f"M{idx}:", m.to_list())
                res = mats[0]; paso = 1
                for idx, M in enumerate(mats[1:], start=2):
                    A = res.to_list(); B = M.to_list()
                    R = res.restar(M).to_list()
                    self.ops_steps_text.insert(tk.END, f"Paso {paso}: R{paso} = {'R'+str(paso-1) if paso>1 else 'M1'} - M{idx}\\n")
                    for i in range(len(A)):
                        for j in range(len(A[0])):
                            self.ops_steps_text.insert(tk.END, f"  r[{i+1},{j+1}] = {fmt_val(A[i][j])} - {fmt_val(B[i][j])} = {fmt_val(R[i][j])}\\n")
                    show_matrix_block("Resultado parcial:", R)
                    res = matrices.Matriz(R)
                    paso += 1
                self.ops_result_text.insert(tk.END, "Resultado de la resta (M1 - M2 - ...):\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))

            elif op == "Multiplicacion":
                self.ops_steps_text.insert(tk.END, "Multiplicación de matrices\n-----------------------\n\n")
                for idx, m in enumerate(mats, start=1):
                    show_matrix_block(f"M{idx}:", m.to_list())
                res = mats[0]; paso = 1
                for idx, M in enumerate(mats[1:], start=2):
                    A = res.to_list(); B = M.to_list()
                    if len(A[0]) != len(B):
                        raise ValueError(f"Dimensiones incompatibles para multiplicacion: {len(A)}x{len(A[0])} * {len(B)}x{len(B[0])}")
                    n, pcols, mcols = len(A), len(B[0]), len(A[0])
                    R = [[0.0 for _ in range(pcols)] for __ in range(n)]
                    self.ops_steps_text.insert(tk.END, f"Paso {paso}: R{paso} = {'R'+str(paso-1) if paso>1 else 'M1'} @ M{idx}\\n")
                    for i in range(n):
                        for j in range(pcols):
                            terms = []
                            s = 0.0
                            for k in range(mcols):
                                terms.append(f"{fmt_val(A[i][k])}*{fmt_val(B[k][j])}")
                                s += float(A[i][k]) * float(B[k][j])
                            R[i][j] = s
                            self.ops_steps_text.insert(tk.END, f"  r[{i+1},{j+1}] = " + " + ".join(terms) + f" = {fmt_val(s)}\\n")
                    show_matrix_block("Resultado parcial:", R)
                    res = matrices.Matriz(R)
                    paso += 1
                self.ops_result_text.insert(tk.END, "Resultado de la multiplicacion (M1 @ M2 @ ...):\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))

            elif op == "Multiplicacion escalar":
                self.ops_steps_text.insert(tk.END, "Multiplicación escalar\n----------------------\n\n")
                try:
                    factor = float(self.ops_scalar_var.get())
                except Exception:
                    messagebox.showerror("Error", "Ingresa un escalar valido.")
                    return
                self.ops_steps_text.insert(tk.END, f"Escalar seleccionado: {fmt_val(factor)}\n\n")
                for idx, m in enumerate(mats, start=1):
                    original = m.to_list()
                    scaled = m.multiplicar(factor).to_list()
                    show_matrix_block(f"M{idx} (original):", original)
                    self.ops_steps_text.insert(tk.END, f"M{idx} * {fmt_val(factor)}\n")
                    self.ops_steps_text.insert(tk.END, self._format_matrix_for_display(scaled))
                    self.ops_steps_text.insert(tk.END, "\n")
                self.ops_result_text.insert(tk.END, f"Resultado de multiplicar {len(mats)} matriz(es) por {fmt_val(factor)}:\n\n")
                for idx, m in enumerate(mats, start=1):
                    scaled = m.multiplicar(factor).to_list()
                    self.ops_result_text.insert(tk.END, f"M{idx} escalar:\n{self._format_matrix_for_display(scaled)}\n\n")

            elif op == "Transponer":
                self.ops_steps_text.insert(tk.END, "Transponer matriz\n-----------------\n\n")
                if len(mats) != 1:
                    messagebox.showwarning("Operación", "Selecciona un conjunto con una sola matriz para transponer.")
                    return
                mat = mats[0]
                res = mat.trasponer()
                self.ops_steps_text.insert(tk.END, "Transposición de la matriz:\n\n")
                self.ops_steps_text.insert(tk.END, self._format_matrix_for_display(mat.to_list()) + "\n\n")
                self.ops_result_text.insert(tk.END, "Matriz transpuesta:\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))

            elif op == "Inversa":
                self.ops_steps_text.insert(tk.END, "Inversa de matriz\n-----------------\n\n")
                if len(mats) != 1:
                    messagebox.showwarning("Operación", "Selecciona un conjunto con una sola matriz para calcular la inversa.")
                    return
                mat = mats[0]
                try:
                    inv_res = mat.inversa(mostrar_pasos=True)
                    self.ops_steps_text.insert(tk.END, "Pasos para la inversa (Gauss-Jordan sobre [A|I]):\n")
                    for paso in inv_res.get("pasos", []):
                        self.ops_steps_text.insert(tk.END, str(paso) + "\n")
                    inv_text = inv_res.get("inversa")
                    if inv_text is None:
                        self.ops_result_text.insert(tk.END, inv_res.get("mensaje", "La matriz es singular."))
                    else:
                        self.ops_result_text.insert(tk.END, inv_res.get("mensaje", "") + "\n\n")
                        self.ops_result_text.insert(tk.END, inv_text)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo calcular la inversa: {e}")
                    return

            elif op == "Determinante":
                self.ops_steps_text.insert(tk.END, "Determinante\n-------------\n\n")
                if len(mats) != 1:
                    messagebox.showwarning("Operación", "Selecciona un conjunto con una sola matriz para el determinante.")
                    return
                mat = mats[0]
                try:
                    det_res = matrices.determinante_por_gauss_con_pasos(mat.to_list(), mostrar_pasos=True)
                    self.ops_steps_text.insert(tk.END, "Pasos para el determinante (Gauss):\n")
                    for paso in det_res.get("pasos", []):
                        self.ops_steps_text.insert(tk.END, str(paso) + "\n\n")
                    det_val = det_res.get("determinante")
                    self.ops_result_text.insert(tk.END, f"Determinante: {det_val}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo calcular el determinante: {e}")
                    return

            elif op == "Independencia":
                self.ops_steps_text.insert(tk.END, "Independencia de vectores\n--------------------------\n\n")
                if len(mats) != 1:
                    messagebox.showwarning("Operación", "Selecciona un conjunto con una sola matriz para verificar independencia.")
                    return
                mat = mats[0]
                try:
                    res_ind = mat.independencia_vectores(mat.to_list())
                    self.ops_result_text.insert(tk.END, res_ind.get("mensaje", "") + "\n")
                    if res_ind.get("pasos"):
                        self.ops_steps_text.insert(tk.END, "Pasos:\n")
                        for idx, paso in enumerate(res_ind["pasos"], start=1):
                            desc = paso.get("descripcion", "")
                            matriz_txt = paso.get("matriz", "")
                            self.ops_steps_text.insert(tk.END, f"Paso {idx}: {desc}\n")
                            if matriz_txt:
                                self.ops_steps_text.insert(tk.END, f"{matriz_txt}\n\n")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo verificar independencia: {e}")
                    return

            else:
                messagebox.showerror("Operacion desconocida", op)
                return
        except Exception as e:
            messagebox.showerror("Error en operacion", str(e))

    def solve_equations_from_ops(self):
        """Genera la matriz desde ecuaciones y la resuelve con el metodo elegido."""
        raw_text = self.ops_equations_text.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Datos requeridos", "Ingresa al menos una ecuacion o un bloque LaTeX.")
            return

        metodo = (self.ops_eq_method_var.get() or "Gauss-Jordan").strip()

        try:
            resultado = matrices.resolver_sistema_desde_ecuaciones(raw_text, metodo=metodo, mostrar_pasos=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo resolver el sistema: {e}")
            return

        matriz_creada = resultado.get("matriz", [])
        variables = resultado.get("variables", [])
        ecuaciones_norm = resultado.get("ecuaciones", [])
        res = resultado.get("resultado", {})

        self.ops_result_text.delete(1.0, tk.END)
        self.ops_steps_text.delete(1.0, tk.END)

        if ecuaciones_norm:
            self.ops_steps_text.insert(tk.END, "Ecuaciones normalizadas:\n")
            for eq in ecuaciones_norm:
                self.ops_steps_text.insert(tk.END, f"  {eq}\n")
            self.ops_steps_text.insert(tk.END, "\n")

        if matriz_creada:
            dims = ""
            if matriz_creada and matriz_creada[0]:
                dims = f" ({len(matriz_creada)}x{len(matriz_creada[0])})"
            self.ops_result_text.insert(tk.END, f"Matriz generada{dims}:\n")
            self.ops_result_text.insert(tk.END, self._format_matrix_for_display(matriz_creada))
            self.ops_result_text.insert(tk.END, "\n\n")

        if variables:
            self.ops_result_text.insert(tk.END, "Variables: " + ", ".join(variables) + "\n\n")

        mensaje = res.get("mensaje")
        if mensaje:
            self.ops_result_text.insert(tk.END, mensaje + "\n\n")

        solucion = res.get("solucion")
        if isinstance(solucion, dict) and solucion:
            for var, val in solucion.items():
                self.ops_result_text.insert(tk.END, f"{var} = {val}\n")
            self.ops_result_text.insert(tk.END, "\n")
        elif isinstance(solucion, str):
            self.ops_result_text.insert(tk.END, solucion + "\n\n")

        pasos = res.get("pasos", [])
        if pasos:
            for idx, paso in enumerate(pasos, start=1):
                descripcion = paso.get("descripcion", "")
                self.ops_steps_text.insert(tk.END, f"Paso {idx}: {descripcion}\n")
                if 'matriz' in paso:
                    self.ops_steps_text.insert(tk.END, self._format_matrix_for_display(paso['matriz']) + "\n")
        elif mensaje:
            self.ops_steps_text.insert(tk.END, mensaje + "\n")

    def draw_vector_entries(self, num_vectores, dimension, name, is_modification=False, data=None):
        """Dibuja la cuadrícula para ingresar los datos de los vectores."""
        for widget in self.vector_entries_frame.winfo_children():
            widget.destroy()

        if is_modification:
             self.original_vector_data_for_modification = {
                'num_vectores': num_vectores,
                'dimension': dimension,
                'datos': [vec[:] for vec in data]
            }

        self.vector_entries = []
        for j in range(num_vectores):
            ttk.Label(self.vector_entries_frame, text=f"V{j+1}", style='Dark.TLabel').grid(row=0, column=j, padx=5, pady=5)
            col_entries = []
            for i in range(dimension):
                entry = ttk.Entry(self.vector_entries_frame, width=8, style='Entry.TEntry')
                default_value = "0"
                if data and j < len(data) and i < len(data[j]):
                    default_value = str(data[j][i])
                entry.insert(0, default_value)
                entry.grid(row=i + 1, column=j, padx=5, pady=2)
                col_entries.append(entry)
            self.vector_entries.append(col_entries)
        
        button_frame = ttk.Frame(self.vector_entries_frame, style='Dark.TFrame')
        button_frame.grid(row=dimension + 2, column=0, columnspan=num_vectores, pady=(15, 0), sticky='ew')

        button_text = "Actualizar Conjunto" if is_modification else "Guardar Conjunto"
        save_command = lambda: self.update_vector_set_data(self.vector_entries, num_vectores, dimension, name) if is_modification else self.save_vector_set_data(self.vector_entries, num_vectores, dimension, name)
        
        ttk.Button(button_frame, text=button_text, style='Dark.TButton', command=save_command).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ttk.Button(button_frame, text="Cancelar", style='Dark.TButton', command=self.clear_vector_entries_frame).pack(side=tk.LEFT, expand=True, fill='x', padx=2)

    def clear_vector_entries_frame(self):
        for widget in self.vector_entries_frame.winfo_children():
            widget.destroy()

    def run_independence_check(self):
        """Recopila los datos de los vectores y ejecuta la comprobación de independencia."""
        selection = self.vector_set_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona un conjunto de vectores de la lista.")
            return

        name = self.vector_set_listbox.get(selection[0])
        vector_set_data = persistencia.cargar_conjunto_vectores(name)

        if not vector_set_data:
            messagebox.showerror("Error", f"No se pudo cargar el conjunto de vectores '{name}'.")
            return
            
        vectores = vector_set_data['datos']
        
        if len(vectores) < 1: # La función lógica ya valida < 2, pero aquí es por si los datos están mal
            messagebox.showwarning("Validación", "Se requieren al menos dos vectores para realizar la comprobación.")
            return

        try:
            # Se necesita una instancia de Matriz para llamar al método.
            dummy_matrix = matrices.Matriz([[1]])
            resultado = dummy_matrix.independencia_vectores(vectores)

            # Limpiar áreas de texto
            self.independence_result_text.delete(1.0, tk.END)
            self.independence_steps_text.delete(1.0, tk.END)

            # Mostrar resultados
            self.independence_result_text.insert(tk.END, resultado.get("mensaje", "No se generó un mensaje."))
            
            solucion = resultado.get("solucion", {})
            if solucion:
                self.independence_result_text.insert(tk.END, f"\nRango: {solucion.get('rango')}")
                if not solucion.get('independiente'):
                    self.independence_result_text.insert(tk.END, f"\nColumnas libres (vectores): {solucion.get('libres')}")

            if "pasos" in resultado:
                for paso in resultado["pasos"]:
                    self.independence_steps_text.insert(tk.END, f"{paso['descripcion']}\n")
                    if 'matriz' in paso:
                        formatted_matrix = self._format_matrix_for_display(paso['matriz'])
                        self.independence_steps_text.insert(tk.END, formatted_matrix + "\n")

        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Error en los datos del vector: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def _format_matrix_for_display(self, matrix_data):
        if not matrix_data or not any(matrix_data):
            return ""
        
        # Convertir todos los elementos a cadenas para calcular anchos
        str_matrix = [[str(cell) for cell in row] for row in matrix_data]
        
        # Encontrar el ancho máximo para cada columna
        col_widths = [0] * len(str_matrix[0])
        for row in str_matrix:
            for i, cell in enumerate(row):
                if len(cell) > col_widths[i]:
                    col_widths[i] = len(cell)
                    
        # Construir la cadena formateada
        formatted_str = ""
        num_rows = len(str_matrix)
        for i, row in enumerate(str_matrix):
            line = ""
            # Usar paréntesis normales y alineación
            if i == 0:
                line += " /"
            elif i == num_rows - 1:
                line += " \\"
            else:
                line += "| "
                
            for j, cell in enumerate(row):
                line += cell.rjust(col_widths[j] + 1)
            
            line += " "
            if i == 0:
                line += "\\ "
            elif i == num_rows - 1:
                line += "/ "
            else:
                line += " |"
            
            formatted_str += line + "\n"
            
        return formatted_str

    def update_matrix_list(self):
        self.matrix_listbox.delete(0, tk.END)
        matrices_data = persistencia.cargar_todas_matrices()
        if matrices_data:
            for name in matrices_data.keys():
                self.matrix_listbox.insert(tk.END, name)
        try:
            next_name = self._next_available_letter(matrices_data.keys() if matrices_data else [])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, next_name)
        except Exception:
            pass
    
    def update_vector_set_list(self):
        self.vector_set_listbox.delete(0, tk.END)
        vector_sets_data = persistencia.cargar_todos_vectores()
        if vector_sets_data:
            for name in vector_sets_data.keys():
                self.vector_set_listbox.insert(tk.END, name)
        try:
            next_name = self._next_available_letter(vector_sets_data.keys() if vector_sets_data else [])
            self.vector_name_entry.delete(0, tk.END)
            self.vector_name_entry.insert(0, next_name)
        except Exception:
            pass

    def view_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
            return
            
        matrix_name = self.matrix_listbox.get(selection[0])
        matrix_data = persistencia.cargar_matriz(matrix_name)
        
        if matrix_data:
            # Limpiar el frame de entrada y las áreas de resultado
            self.clear_matrix_frame()
            self.show_result("") # Limpia las áreas de texto inferiores

            # Formatear los datos de la matriz para mostrarlos
            info_str = (f"Matriz: {matrix_data['nombre']}\n"
                        f"Dimensiones: {matrix_data['filas']}x{matrix_data['columnas']}\n\n")
            matrix_str = self._format_matrix_for_display(matrix_data['datos'])
            
            # Mostrar la información directamente en el frame de datos
            display_label = ttk.Label(self.matrix_frame, text=info_str + matrix_str, style='Result.TLabel', justify=tk.LEFT)
            display_label.pack(pady=10, padx=10, anchor='w')
        else:
            messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")
    
    def view_vector_set(self):
        selection = self.vector_set_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona un conjunto de vectores de la lista.")
            return
            
        name = self.vector_set_listbox.get(selection[0])
        vector_set_data = persistencia.cargar_conjunto_vectores(name)
        
        if vector_set_data:
            # Limpiar el frame de entrada y las áreas de resultado
            self.clear_vector_entries_frame()
            self.independence_result_text.delete(1.0, tk.END)
            self.independence_steps_text.delete(1.0, tk.END)

            # Formatear los datos para mostrarlos
            info_str = (f"\nConjunto: {vector_set_data['nombre']}\n"
                        f"\nNº de Vectores: {vector_set_data['num_vectores']}\n"
                        f"\nDimensión: {vector_set_data['dimension']}\n\n")
            
            # Transponer los datos para mostrarlos como columnas
            datos_transpuestos = list(map(list, zip(*vector_set_data['datos'])))
            vector_str = self._format_matrix_for_display(datos_transpuestos)

            # Mostrar la información directamente en el frame de datos de vectores
            display_label = ttk.Label(self.vector_entries_frame, text=info_str + vector_str, style='Result.TLabel', justify=tk.LEFT)
            display_label.pack(pady=10, padx=10, anchor='w')
        else:
            messagebox.showerror("Error", f"No se encontró el conjunto de vectores '{name}'.")

    def transpose_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz para transponer.")
            return
            
        matrix_name = self.matrix_listbox.get(selection[0])
        matrix_data = persistencia.cargar_matriz(matrix_name)
        
        if matrix_data:
            try:
                matriz_obj = matrices.Matriz(matrix_data['datos'])
                matriz_transpuesta_obj = matriz_obj.trasponer()

                # Limpiar área de entrada y áreas de resultado
                self.clear_matrix_frame()
                try:
                    self.result_text.delete(1.0, tk.END)
                    self.steps_text.delete(1.0, tk.END)
                except Exception:
                    # En caso de que las áreas de resultado no existan por alguna razón
                    pass

                info_str = (f"Transpuesta de la Matriz: {matrix_data['nombre']}\n"
                            f"Nuevas Dimensiones: {matriz_transpuesta_obj.n}x{matriz_transpuesta_obj.m}\n\n")
                matrix_str = self._format_matrix_for_display(matriz_transpuesta_obj.A)

                # Insertar el resultado en la sección "Resultado"
                try:
                    self.result_text.insert(tk.END, info_str)
                    self.result_text.insert(tk.END, matrix_str)
                except Exception as e:
                    # Fallback: si no existe result_text, mostrar en el frame de datos
                    display_label = ttk.Label(self.matrix_frame, text=info_str + matrix_str, style='Result.TLabel', justify=tk.LEFT)
                    display_label.pack(pady=10, padx=10, anchor='w')

            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al transponer la matriz: {e}")
        else:
            messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")

    def calculate_inverse(self):
        """Calcula y muestra la inversa de la matriz seleccionada."""
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona una matriz de la lista.")
            return

        matrix_name = self.matrix_listbox.get(selection[0])
        matrix_data = persistencia.cargar_matriz(matrix_name)

        if not matrix_data:
            messagebox.showerror("Error", f"No se pudo cargar la matriz '{matrix_name}'.")
            return

        try:
            matriz_obj = matrices.Matriz(matrix_data['datos'])
            resultado = matriz_obj.inversa()

            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)

            self.result_text.insert(tk.END, resultado.get("mensaje", "No se generó mensaje.") + "\n")
            if resultado.get("inversa"):
                formatted_inv = self._format_matrix_for_display(resultado["inversa"])
                self.result_text.insert(tk.END, "\nInversa:\n" + formatted_inv)

            if "pasos" in resultado:
                for paso in resultado["pasos"]:
                    self.steps_text.insert(tk.END, f"{paso['descripcion']}\n")
                    if 'matriz' in paso:
                        formatted_matrix = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted_matrix + "\n\n")

        except ValueError as e:
            messagebox.showerror("Error de validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def calculate_determinant(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz para calcular su determinante.")
            return

        matrix_name = self.matrix_listbox.get(selection[0])
        matrix_data = persistencia.cargar_matriz(matrix_name)
        if not matrix_data or not matrix_data.get('datos'):
            messagebox.showerror("Error", f"No se pudo cargar la matriz '{matrix_name}'.")
            return

        datos = matrix_data['datos']
        n = len(datos)
        m = len(datos[0])

        # Si es aumentada n x (n+1), tomar sólo los coeficientes
        if m == n + 1:
            A = [fila[:-1] for fila in datos]
            note = " (se usó sólo la matriz de coeficientes)."
        elif m == n:
            A = datos
            note = ""
        else:
            messagebox.showerror("Dimensiones inválidas", "Para el determinante se requiere una matriz cuadrada n×n o una aumentada n×(n+1).")
            return

        try:
            resultado = matrices.determinante_por_gauss_con_pasos(A, mostrar_pasos=True)

            det = resultado.get("determinante", 0.0)
            det_fmt = f"{int(round(det))}" if abs(det - round(det)) < 1e-10 else f"{det:.4f}"

            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)

            # Encabezado de resultado
            self.result_text.insert(tk.END, f"det(A) = {det_fmt}{note}\n")
            if "mensaje" in resultado:
                self.result_text.insert(tk.END, resultado["mensaje"] + "\n")

            # Mostrar A utilizada
            formatted_A = self._format_matrix_for_display(A)
            self.result_text.insert(tk.END, "\nMatriz A usada:\n" + formatted_A)

            # Mostrar pasos
            if "pasos" in resultado and resultado["pasos"]:
                for idx, paso in enumerate(resultado["pasos"], start=1):
                    self.steps_text.insert(tk.END, f"Paso {idx}: {paso['descripcion']}\n")
                    if 'matriz' in paso:
                        formatted_matrix = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted_matrix + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al calcular el determinante: {e}")

    def delete_matrix(self):
            selection = self.matrix_listbox.curselection()
            if not selection:
                messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
                return

            matrix_name = self.matrix_listbox.get(selection[0])
            if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar la matriz '{matrix_name}'?"):
                if persistencia.eliminar_matriz(matrix_name):
                    messagebox.showinfo("Éxito", f"Matriz '{matrix_name}' eliminada exitosamente.")
                    self.update_matrix_list()
                else:
                    messagebox.showerror("Error", f"No se pudo eliminar la matriz '{matrix_name}'.")

    
    def _on_matrix_select(self, event):
        selection = self.matrix_listbox.curselection()
        if selection:
            self.selected_matrix = self.matrix_listbox.get(selection[0])
            try:
                self.equations_text.delete(1.0, tk.END)
            except Exception:
                pass

    def _on_vector_set_select(self, event):
        selection = self.vector_set_listbox.curselection()
        if selection:
            self.selected_vector_set = self.vector_set_listbox.get(selection[0])

    def _get_method_selection(self):
        allowed = {"Gauss-Jordan", "Gauss", "Cramer"}
        val = (self.method_var.get() or "").strip()
        return val if val in allowed else None

    def _on_method_select(self, event):
        val = (self.method_var.get() or "").strip()
        allowed = {"Gauss-Jordan", "Gauss", "Cramer"}
        if val in allowed:
            self.selected_method = val
        else:
            self.selected_method = None
            self.method_var.set("")

    def solve_matrix(self, metodo_override=None):
        matrix_name = getattr(self, 'selected_matrix', None)
        metodo = metodo_override or self._get_method_selection()

        if not matrix_name:
            selection = self.matrix_listbox.curselection()
            if selection:
                matrix_name = self.matrix_listbox.get(selection[0])
            else:
                messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
                return
        
        if not metodo:
            messagebox.showwarning(
                "Selección requerida",
                "Selecciona un método: Gauss-Jordan, Gauss, Cramer, Transponer, Inversa, Determinante o Independencia.",
            )
            return

        try:
            matriz_data = persistencia.cargar_matriz(matrix_name)
            if matriz_data is None:
                messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")
                return
            datos = matriz_data['datos']
            if not datos or not datos[0]:
                messagebox.showerror("Error", "La matriz está vacía y no se puede procesar.")
                return

            n = len(datos)
            m = len(datos[0])

            # Métodos directos delegados
            if metodo == "Transponer":
                self.transpose_matrix()
                return
            if metodo == "Inversa":
                self.calculate_inverse()
                return
            if metodo == "Determinante":
                self.calculate_determinant()
                return
            if metodo == "Independencia":
                self.check_independence()
                return

            if metodo == "Cramer":
                # Requiere matriz aumentada n×(n+1)
                if m != n + 1:
                    messagebox.showerror("Dimensiones inválidas", "Para Cramer se requiere una matriz aumentada n×(n+1).")
                    return

                A = [fila[:-1] for fila in datos]
                b = [fila[-1] for fila in datos]

                try:
                    resultado = matrices.cramer_con_pasos(A, b, mostrar_pasos=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error al resolver por Cramer: {e}")
                    return

                # Mostrar resultados y pasos
                self.result_text.delete(1.0, tk.END)
                self.steps_text.delete(1.0, tk.END)

                self.result_text.insert(tk.END, "Solución por Cramer:\n")
                for i, x in enumerate(resultado.get("soluciones", []), start=1):
                    x_fmt = f"{int(round(x))}" if abs(x - round(x)) < 1e-10 else f"{x:.6f}"
                    self.result_text.insert(tk.END, f"x{i} = {x_fmt}\n")

                if "mensaje" in resultado:
                    self.result_text.insert(tk.END, "\n" + resultado["mensaje"] + "\n")

                # Mostrar pasos
                self.steps_text.insert(tk.END, "Procedimiento:\n")
                for paso in resultado.get("pasos", []):
                    self.steps_text.insert(tk.END, f"{paso.get('descripcion','')}\n")
                    if 'matriz' in paso:
                        formatted = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted + "\n\n")
                return

            # Gauss / Gauss-Jordan
            matriz_obj = matrices.Matriz(datos)
            if metodo == "Gauss":
                resultado = matriz_obj.gauss()
            elif metodo == "Gauss-Jordan":
                resultado = matriz_obj.gauss_jordan()
            else:
                messagebox.showerror("Error", f"Método de resolución desconocido: {metodo}")
                return
            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)
            # Mostrar el mensaje principal del resultado
            if "mensaje" in resultado:
                self.result_text.insert(tk.END, resultado["mensaje"] + "\n\n")
            # Mostrar la solucion completa
            solucion = resultado.get("solucion")
            if isinstance(solucion, dict):
                self.result_text.insert(tk.END, "Solucion:\n")
                for var, val in solucion.items():
                    if isinstance(val, (int, float)):
                        val_fmt = f"{int(round(val))}" if abs(val - round(val)) < 1e-10 else f"{val:.6f}"
                    else:
                        val_fmt = str(val)
                    self.result_text.insert(tk.END, f"{var} = {val_fmt}\n")
                if solucion:
                    self.result_text.insert(tk.END, "\n")
            elif isinstance(solucion, str):
                self.result_text.insert(tk.END, solucion + "\n\n")
            # Mostrar los pasos si existen
            if "pasos" in resultado and resultado["pasos"]:
                self.steps_text.insert(tk.END, "Procedimiento:\n")
                for idx, paso in enumerate(resultado["pasos"]):
                    self.steps_text.insert(tk.END, f"Paso {idx+1}: {paso['descripcion']}\n")
                    if 'matriz' in paso:
                        formatted_step_matrix = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted_step_matrix + "\n\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la resolución de la matriz: {e}")
    
    def solve_equations_from_calculator(self, metodo_override=None):
        """Convierte ecuaciones (texto o LaTeX) en matriz y resuelve con el metodo seleccionado."""
        raw_text = self.equations_text.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Datos requeridos", "Ingresa al menos una ecuacion o un bloque LaTeX.")
            return

        metodo = metodo_override or self._get_method_selection()
        if not metodo:
            messagebox.showwarning(
                "Seleccion requerida",
                "Selecciona un metodo: Gauss-Jordan, Gauss o Cramer."
            )
            return

        try:
            resultado = matrices.resolver_sistema_desde_ecuaciones(raw_text, metodo=metodo, mostrar_pasos=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar las ecuaciones: {e}")
            return

        datos = resultado.get("matriz", [])
        variables = resultado.get("variables", [])
        ecuaciones_norm = resultado.get("ecuaciones", [])
        res = resultado.get("resultado", {})

        self.clear_matrix_frame()
        self.result_text.delete(1.0, tk.END)
        self.steps_text.delete(1.0, tk.END)

        if ecuaciones_norm:
            self.steps_text.insert(tk.END, "Ecuaciones normalizadas:\n")
            for eq in ecuaciones_norm:
                self.steps_text.insert(tk.END, f"  {eq}\n")
            self.steps_text.insert(tk.END, "\n")

        if datos:
            dims = f" ({len(datos)}x{len(datos[0])})" if datos and datos[0] else ""
            matrix_str = self._format_matrix_for_display(datos)
            display_label = ttk.Label(self.matrix_frame, text=f"Matriz generada{dims}:\n{matrix_str}", style='Result.TLabel', justify=tk.LEFT)
            display_label.pack(pady=6, padx=8, anchor='w')
            self.result_text.insert(tk.END, f"Matriz generada{dims}:\n{matrix_str}\n\n")
            self._save_generated_matrix_from_equations(datos, ecuaciones_norm, raw_text, metodo)

        if variables:
            self.result_text.insert(tk.END, "Variables: " + ", ".join(variables) + "\n\n")

        mensaje = res.get("mensaje")
        if mensaje:
            self.result_text.insert(tk.END, mensaje + "\n\n")

        solucion = res.get("solucion")
        if isinstance(solucion, dict):
            for var, val in solucion.items():
                self.result_text.insert(tk.END, f"{var} = {val}\n")
            if solucion:
                self.result_text.insert(tk.END, "\n")
        elif isinstance(solucion, str):
            self.result_text.insert(tk.END, solucion + "\n\n")

        pasos = res.get("pasos", [])
        if pasos:
            self.steps_text.insert(tk.END, "Procedimiento:\n")
            for idx, paso in enumerate(pasos, start=1):
                descripcion = paso.get("descripcion", "")
                self.steps_text.insert(tk.END, f"Paso {idx}: {descripcion}\n")
                if 'matriz' in paso:
                    self.steps_text.insert(tk.END, self._format_matrix_for_display(paso['matriz']) + "\n")
        elif mensaje:
            self.steps_text.insert(tk.END, mensaje + "\n")

    def _save_generated_matrix_from_equations(self, datos, ecuaciones_norm, raw_text, metodo):
        """
        Guarda la matriz generada desde ecuaciones en matriz.json y también persiste
        las ecuaciones (ecuaciones.json). Si el nombre es inválido/ vacío, solicita uno.
        """
        name = self.name_entry.get().strip()
        if not name or not name.isalpha() or not name.isupper() or len(name) != 1:
            name = simpledialog.askstring("Guardar matriz", "Ingresa un nombre (una letra mayúscula A-Z) para guardar la matriz generada:")
            if not name:
                return
            name = name.strip()
        if not name or not name.isalpha() or not name.isupper() or len(name) != 1:
            messagebox.showwarning("Nombre de matriz", "El nombre debe ser una sola letra mayúscula (A-Z) para guardar la matriz generada.")
            return
        try:
            filas = len(datos)
            columnas = len(datos[0]) if datos and datos[0] else 0
            matriz_payload = {"nombre": name, "filas": filas, "columnas": columnas, "datos": datos}
            persistencia.guardar_matriz(name, matriz_payload)
            try:
                persistencia.guardar_ecuacion(
                    name,
                    {"nombre": name, "ecuaciones": ecuaciones_norm, "raw": raw_text, "metodo": metodo, "matriz": datos},
                )
            except Exception:
                pass
            self.update_matrix_list()
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudo guardar la matriz generada: {e}")

    def check_independence(self):
        matrix_name = getattr(self, 'selected_matrix', None)

        if not matrix_name:
            selection = self.matrix_listbox.curselection()
            if selection:
                matrix_name = self.matrix_listbox.get(selection[0])
            else:
                messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
                return
        
        try:
            matriz_data = persistencia.cargar_matriz(matrix_name)
            if matriz_data is None:
                messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")
                return

            matriz_obj = matrices.Matriz(matriz_data['datos'])
            
            # Extraer los vectores columna de la matriz de datos
            datos = matriz_data['datos']
            if not datos or not datos[0]:
                messagebox.showerror("Error", "La matriz está vacía y no se puede procesar.")
                return
            
            num_filas = len(datos)
            num_columnas = len(datos[0])
            vectores_columna = [[datos[i][j] for i in range(num_filas)] for j in range(num_columnas)]

            # Llamar a la función independencia_vectores con los vectores columna
            resultado = matriz_obj.independencia_vectores(vectores_columna)

            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)

            # Mostrar el mensaje principal del resultado
            if "mensaje" in resultado:
                self.result_text.insert(tk.END, resultado["mensaje"] + "\n\n")

            # Mostrar los pasos si existen
            if "pasos" in resultado and resultado["pasos"]:
                for idx, paso in enumerate(resultado["pasos"]):
                    self.steps_text.insert(tk.END, f"Paso {idx+1}: {paso['descripcion']}\n")
                    if 'matriz' in paso:
                        formatted_step_matrix = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted_step_matrix + "\n")
            
        except AttributeError:
            messagebox.showerror("Error", "La función 'independencia_vectores' no está implementada en la clase Matriz.")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la verificación de independencia: {e}")

    def create_matrix(self):
        name = self.name_entry.get().strip()
        
        # Validación del nombre de la matriz
        if not name or not name.isalpha() or not name.isupper() or len(name) != 1:
            messagebox.showerror("Nombre inválido", "El nombre de la matriz debe ser una única letra mayúscula (A-Z).")
            return
        
        # Validar si el nombre de la matriz ya existe
        todas_matrices = persistencia.cargar_todas_matrices()
        if name in todas_matrices:
            messagebox.showerror("Nombre en uso", f"Ya existe una matriz con el nombre '{name}'. Por favor, elige otro nombre.")
            return
            
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            if rows <= 0 or cols <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Filas y columnas deben ser números enteros positivos.")
            return
        
        self.create_matrix_input_ui(rows, cols, name)
    
    def modify_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz para modificar.")
            return

        matrix_name = self.matrix_listbox.get(selection[0])
        matrix_data = persistencia.cargar_matriz(matrix_name)

        if not matrix_data:
            messagebox.showerror("Error", f"No se pudo cargar la matriz '{matrix_name}'.")
            return

        self.create_matrix_input_ui(matrix_data['filas'], matrix_data['columnas'], matrix_name, is_modification=True, data=matrix_data['datos'])

    def create_matrix_input_ui(self, rows, cols, name, is_modification=False, data=None):
        # Limpiar frame anterior
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        # Guardar datos originales para comparación posterior si es modificación
        if is_modification:
            self.original_matrix_data_for_modification = {
                'filas': rows,
                'columnas': cols,
                'datos': [row[:] for row in data] # Copia profunda
            }

        # Crear widgets para redimensionar si es modificación
        if is_modification:
            resize_frame = ttk.Frame(self.matrix_frame, style='Dark.TFrame')
            resize_frame.grid(row=0, column=0, columnspan=cols + 1, pady=(0, 10), sticky="ew")
            
            ttk.Label(resize_frame, text="Filas:", style='Dark.TLabel').pack(side=tk.LEFT, padx=(0, 5))
            mod_rows_var = tk.StringVar(value=str(rows))
            mod_rows_spinbox = tk.Spinbox(resize_frame, from_=1, to=20, width=5, textvariable=mod_rows_var, bg=self.palette["input"], fg=self.palette["text"])
            mod_rows_spinbox.pack(side=tk.LEFT, padx=(0, 10))

            ttk.Label(resize_frame, text="Columnas:", style='Dark.TLabel').pack(side=tk.LEFT, padx=(0, 5))
            mod_cols_var = tk.StringVar(value=str(cols))
            mod_cols_spinbox = tk.Spinbox(resize_frame, from_=1, to=20, width=5, textvariable=mod_cols_var, bg=self.palette["input"], fg=self.palette["text"])
            mod_cols_spinbox.pack(side=tk.LEFT, padx=(0, 20))

            ttk.Button(resize_frame, text="Redimensionar", style='Dark.TButton',
                       command=lambda: self.redraw_matrix_entries_for_modification(mod_rows_var, mod_cols_var, name, data)).pack(side=tk.LEFT)

        # Crear etiquetas de columna
        for j in range(cols):
            ttk.Label(self.matrix_frame, text=f"Col {j+1}").grid(row=1, column=j+1, padx=5, pady=2)

        # Crear entradas para la matriz
        entries = []
        for i in range(rows):
            row_entries = []
            ttk.Label(self.matrix_frame, text=f"Fila {i+1}").grid(row=i+2, column=0, padx=5, pady=2)
            for j in range(cols):
                entry = ttk.Entry(self.matrix_frame, width=8)
                default_value = "0"
                if data and i < len(data) and j < len(data[i]):
                    default_value = str(data[i][j])
                entry.insert(0, default_value)
                entry.grid(row=i+2, column=j+1, padx=2, pady=2)
                row_entries.append(entry)
            entries.append(row_entries)

        # Botón para guardar
        button_text = "Actualizar Matriz" if is_modification else "Guardar Matriz"
        command = lambda: self.update_matrix_data(entries, int(mod_rows_var.get()), int(mod_cols_var.get()), name) if is_modification else self.save_matrix_data(entries, rows, cols, name)
        button_frame = ttk.Frame(self.matrix_frame, style='Dark.TFrame')
        button_frame.grid(row=rows+3, column=0, columnspan=cols+1, pady=10)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text=button_text, command=command).pack(side=tk.LEFT, expand=True, fill='x', padx=2)
        ttk.Button(button_frame, text="Cancelar", command=self.clear_matrix_frame).pack(side=tk.LEFT, expand=True, fill='x', padx=2)

    def clear_matrix_frame(self):
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

    def redraw_matrix_entries_for_modification(self, rows_var, cols_var, name, old_data):
        try:
            new_rows = int(rows_var.get())
            new_cols = int(cols_var.get())
            if new_rows <= 0 or new_cols <= 0: raise ValueError

            # Crear nueva matriz de datos manteniendo los valores antiguos que quepan
            new_data = [[0] * new_cols for _ in range(new_rows)]
            for i in range(min(new_rows, len(old_data))):
                for j in range(min(new_cols, len(old_data[0]))):
                    new_data[i][j] = old_data[i][j]
            
            self.create_matrix_input_ui(new_rows, new_cols, name, is_modification=True, data=new_data)

        except ValueError:
            messagebox.showerror("Dimensiones inválidas", "Las filas y columnas deben ser números enteros positivos.")

    def update_matrix_data(self, entries, rows, cols, name):
        try:
            datos = self._extract_matrix_values(entries)

            original = self.original_matrix_data_for_modification
            if original['filas'] == rows and original['columnas'] == cols and original['datos'] == datos:
                for widget in self.matrix_frame.winfo_children():
                    widget.destroy()
                return

            if actualizar_matriz(name, datos, rows, cols):
                messagebox.showinfo("Éxito", f"Matriz '{name}' actualizada exitosamente.")
                self.update_matrix_list()
                for widget in self.matrix_frame.winfo_children():
                    widget.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar la matriz '{name}'.")
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos en todas las celdas.")

    def save_matrix_data(self, entries, rows, cols, name):
        try:
            datos = self._extract_matrix_values(entries)

            crear_matriz(name, rows, cols, datos)
            messagebox.showinfo("Éxito", f"Matriz '{name}' creada y guardada exitosamente.")
            self.update_matrix_list()

            self.name_entry.delete(0, tk.END)
            self.rows_var.set("0")
            self.cols_var.set("0")
            for widget in self.matrix_frame.winfo_children():
                widget.destroy()

        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos en todas las celdas.")
    
    # --- Funciones CRUD para la UI de Vectores ---

    def create_vector_set_ui(self):
        name = self.vector_name_entry.get().strip()
        if not name or not name.isalpha() or not name.isupper() or len(name) != 1:
            messagebox.showerror("Nombre inválido", "El nombre del conjunto debe ser una única letra mayúscula (A-Z).")
            return
        
        if name in persistencia.cargar_todos_vectores():
            messagebox.showerror("Nombre en uso", f"Ya existe un conjunto de vectores con el nombre '{name}'.")
            return

        try:
            num_vectores = int(self.num_vectors_var.get())
            dimension = int(self.dim_vectors_var.get())
            if num_vectores <= 0 or dimension <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El número y la dimensión de vectores deben ser enteros positivos.")
            return
        
        self.draw_vector_entries(num_vectores, dimension, name)

    # Guardar Vectores 
    def save_vector_set_data(self, entries, num_vectores, dimension, name):
        try:
            datos = self._extract_vector_values(entries)

            if crear_conjunto_vectores(name, num_vectores, dimension, datos):
                messagebox.showinfo("Éxito", f"Conjunto de vectores '{name}' guardado.")
                self.update_vector_set_list()
                self.vector_name_entry.delete(0, tk.END)
                self.num_vectors_var.set("0")
                self.dim_vectors_var.set("0")
                self.clear_vector_entries_frame()
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos.")

    
    def modify_vector_set_ui(self):
        selection = self.vector_set_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Selecciona un conjunto de vectores para modificar.")
            return

        name = self.vector_set_listbox.get(selection[0])
        data = persistencia.cargar_conjunto_vectores(name)
        if not data:
            messagebox.showerror("Error", f"No se pudo cargar el conjunto '{name}'.")
            return
        
        self.draw_vector_entries(data['num_vectores'], data['dimension'], name, is_modification=True, data=data['datos'])

    def update_vector_set_data(self, entries, num_vectores, dimension, name):
        try:
            datos = self._extract_vector_values(entries)

            original = self.original_vector_data_for_modification
            if original['num_vectores'] == num_vectores and original['dimension'] == dimension and original['datos'] == datos:
                self.clear_vector_entries_frame()
                return

            if actualizar_conjunto_vectores(name, datos, num_vectores, dimension):
                messagebox.showinfo("Éxito", f"Conjunto '{name}' actualizado.")
                self.update_vector_set_list()
                self.clear_vector_entries_frame()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el conjunto '{name}'.")
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de que todos los valores sean números válidos.")

    def delete_vector_set(self):
        selection = self.vector_set_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Selecciona un conjunto para eliminar.")
            return
        
        name = self.vector_set_listbox.get(selection[0])
        if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar el conjunto de vectores '{name}'?"):
            if persistencia.eliminar_conjunto_vectores(name):
                messagebox.showinfo("Éxito", f"Conjunto '{name}' eliminado.")
                self.update_vector_set_list()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el conjunto '{name}'.")

    def _extract_matrix_values(self, entries):
        """Refactorización: transforma entradas UI en datos numéricos para matrices."""
        return [[float(entry.get()) for entry in row] for row in entries]

    def _extract_vector_values(self, entries):
        """Refactorización: transforma entradas UI en datos numéricos para conjuntos de vectores."""
        return [[float(entry.get()) for entry in column] for column in entries]

    def show_result(self, text):
        self.result_text.delete(1.0, tk.END)
        self.steps_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)

    # ---------------- Botones Limpiar por pestaña ----------------
    def clear_calculator_tab(self):
        try:
            self.name_entry.delete(0, tk.END)
        except Exception:
            pass
        try:
            self.method_var.set(" ")
        except Exception:
            pass
        try:
            self.rows_var.set("0"); self.cols_var.set("0")
        except Exception:
            pass
        try:
            self.clear_matrix_frame()
        except Exception:
            pass
        try:
            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)
        except Exception:
            pass
        try:
            self.matrix_listbox.selection_clear(0, tk.END)
        except Exception:
            pass
        self.selected_matrix = None
        self.selected_method = None

    def clear_independence_tab(self):
        try:
            self.vector_name_entry.delete(0, tk.END)
        except Exception:
            pass
        try:
            self.num_vectors_var.set("0"); self.dim_vectors_var.set("0")
        except Exception:
            pass
        try:
            self.clear_vector_entries_frame()
        except Exception:
            pass
        try:
            self.independence_result_text.delete(1.0, tk.END)
            self.independence_steps_text.delete(1.0, tk.END)
        except Exception:
            pass
        try:
            self.vector_set_listbox.selection_clear(0, tk.END)
        except Exception:
            pass
        self.selected_vector_set = None

    def clear_ops_tab(self):
        try:
            self.ops_name_entry.delete(0, tk.END)
        except Exception:
            pass
        try:
            self.num_mats_var.set("0"); self.ops_rows_var.set("0"); self.ops_cols_var.set("0")
        except Exception:
            pass
        try:
            self.ops_method_var.set(" ")
        except Exception:
            pass
        try:
            for w in self.ops_entries_frame.winfo_children():
                w.destroy()
        except Exception:
            pass
        try:
            self.ops_result_text.delete(1.0, tk.END)
            self.ops_steps_text.delete(1.0, tk.END)
        except Exception:
            pass
        try:
            self.matrix_set_listbox.selection_clear(0, tk.END)
        except Exception:
            pass
        self.selected_matrix_set = None

    def clear_numeric_tab(self):
        try:
            self.num_name_entry.delete(0, tk.END)
        except Exception:
            pass
        try:
            self.num_method_var.set("Bisección")
        except Exception:
            pass
        for ent in [getattr(self, 'num_expr_entry', None), getattr(self, 'num_a_entry', None), getattr(self, 'num_b_entry', None), getattr(self, 'num_tol_entry', None)]:
            try:
                if ent is not None:
                    ent.delete(0, tk.END)
            except Exception:
                pass
        try:
            self.eq_listbox.selection_clear(0, tk.END)
        except Exception:
            pass
        self.selected_equation = None
        self._num_editing_name = None
        try:
            if hasattr(self, '_num_update_temp_btn') and self._num_update_temp_btn:
                self._num_update_temp_btn.destroy()
                self._num_update_temp_btn = None
        except Exception:
            pass
        try:
            # limpiar resultado y tabla de pasos
            self.num_result_text.delete(1.0, tk.END)
            for item in self.num_tree.get_children():
                self.num_tree.delete(item)
        except Exception:
            pass
        try:
            self.num_eq_data_text.delete(1.0, tk.END)
            # restaurar altura mínima
            self._num_eqdata_autosize(min_lines=1, max_lines=8)
        except Exception:
            pass
        # resetear estado
        try:
            self.num_state['last_result'] = None
            self.num_state['decimal_mode'] = False
            self.num_toggle_btn.config(text='Mostrar decimales')
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixCRUDApp(root)
    root.mainloop()
