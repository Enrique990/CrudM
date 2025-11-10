import tkinter as tk
from tkinter import ttk, messagebox
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

class MatrixCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Matrices")
        self.root.configure(bg="#23272e")
        
        # Ejecutar en pantalla completa (estilo Windows maximizado). Para modo kiosco se puede usar attributes('-fullscreen', True)
        try:
            self.root.state('zoomed')
        except Exception:
            # Fallback si no está disponible 'zoomed'
            self.root.attributes('-fullscreen', True)

        style = ttk.Style()
        style.theme_use('clam')
        # Estilo para el Notebook y sus pestañas
        style.configure('TNotebook', background="#23272e", borderwidth=0)
        style.configure('TNotebook.Tab', background="#393e46", foreground="#e0e0e0", padding=[10, 5], font=('Segoe UI', 11))
        style.map('TNotebook.Tab', background=[('selected', '#00adb5'), ('active', '#2d323a')], foreground=[('selected', '#23272e')])

        style.configure('Dark.TFrame', background="#23272e")
        style.configure('Dark.TLabel', background="#23272e", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('Dark.TButton', background="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11), borderwidth=0)
        style.map('Dark.TButton', background=[('active', '#00adb5')])
        style.configure('Title.TLabel', background="#23272e", foreground="#00adb5", font=('Segoe UI', 18, 'bold'))
        style.configure('Result.TLabel', background="#23272e", foreground="#e0e0e0", font=('Consolas', 13))
        style.configure('Entry.TEntry', fieldbackground="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('TCombobox', fieldbackground="#393e46", background="#393e46", foreground="#000000")

        # --- Creación del Notebook para manejar las pestañas ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- Pestaña 1: Operadores de Matrices (primera) ---
        self.operators_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.operators_tab, text='Operadores de Matrices')
        self.create_operators_widgets(self.operators_tab)

        # --- Pestaña 2: Calculadora de Matrices ---
        self.calculator_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.calculator_tab, text='Calculadora de Matrices')
        self.create_calculator_widgets(self.calculator_tab)

        # --- Pestaña 3: Independencia de Vectores (última) ---
        self.independence_tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.independence_tab, text='Independencia de Vectores')
        self.create_independence_widgets(self.independence_tab)

        self.selected_matrix = None
        self.selected_method = None

        self.update_matrix_list()
        self.update_vector_set_list()
        self.update_matrix_set_list()
        # Fijar el tamaño inicial de ambos listboxes una sola vez (sin sincronizaciones posteriores)
        self._apply_initial_listbox_size()

    def create_calculator_widgets(self, parent_frame):
        """Crea todos los widgets para la pestaña de la calculadora de matrices."""
        # Frame principal con scroll + panel de Procedimiento a la derecha
        main_frame = ttk.Frame(parent_frame, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Contenedor para el área scrolleable (izquierda)
        content_stack = ttk.Frame(main_frame, style='Dark.TFrame')
        content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(content_stack, bg="#23272e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(content_stack, orient=tk.VERTICAL, command=self.canvas.yview)
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
        self.calc_proc_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        self.calc_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12, 0), pady=0)
        # Estructura interna del panel de procedimiento (label + text con scrollbar)
        ttk.Label(self.calc_proc_panel, text="Procedimiento", style='Title.TLabel').pack(anchor='nw', pady=(10, 5))
        calc_steps_container = ttk.Frame(self.calc_proc_panel, style='Dark.TFrame')
        calc_steps_container.pack(fill=tk.BOTH, expand=True)
        calc_steps_container.rowconfigure(0, weight=1)
        calc_steps_container.columnconfigure(0, weight=1)
        self.steps_text = tk.Text(calc_steps_container, font=('Consolas', 12), bg="#23272e", fg="#e0e0e0", bd=0, highlightthickness=0, width=50)
        self.steps_text.grid(row=0, column=0, sticky='nsew')
        calc_steps_scrollbar = ttk.Scrollbar(calc_steps_container, orient=tk.VERTICAL, command=self.steps_text.yview)
        calc_steps_scrollbar.grid(row=0, column=1, sticky='ns')
        self.steps_text.configure(yscrollcommand=calc_steps_scrollbar.set)

        # Envoltura que ocupa todo el ancho y centra el contenido en columna media
        self.center_wrapper = ttk.Frame(self.scrollable_frame, style='Dark.TFrame')
        self.center_wrapper.pack(fill='x', expand=True)
        # Distribución: columna 0 = panel izquierdo (no expandir), columna 1 = contenido (expandir), columna 2 = separador derecho (no expandir)
        self.center_wrapper.grid_columnconfigure(0, weight=0)
        self.center_wrapper.grid_columnconfigure(1, weight=1)
        self.center_wrapper.grid_columnconfigure(2, weight=0)

        # Frame contenedor centrado
        self.content_container = ttk.Frame(self.center_wrapper, style='Dark.TFrame')
        # Mover el contenido hacia la izquierda con margen de separación respecto al panel lateral
        self.content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')  # <-- Ajusta el margen izquierdo/derecho del contenido (Calculadora)

        # --- Panel lateral izquierdo para la lista de Matrices almacenadas ---
        # Ajuste vertical del layout para que los elementos laterales se estiren en Y
        self.center_wrapper.grid_rowconfigure(0, weight=1)
        # Panel izquierdo anclado a la esquina superior izquierda de la pestaña de Calculadora
        self.calc_left_panel = ttk.Frame(self.center_wrapper, style='Dark.TFrame')
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

    def create_widgets(self):
        # El contenido de este método ahora se dibuja dentro de self.content_container
        main_frame = self.content_container

        # Título
        title_label = ttk.Label(main_frame, text="Calculadora de Matrices", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20), sticky="w")

        # Campo de entrada de ecuación (nombre)
        ttk.Label(main_frame, text="Nombre de la matriz:", style='Dark.TLabel').grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(main_frame, width=18, style='Entry.TEntry')
        self.name_entry.grid(row=1, column=1, sticky="w", padx=(0, 20))

        # Selector de método
        ttk.Label(main_frame, text="Método:", style='Dark.TLabel').grid(row=1, column=2, sticky="e", padx=(0,5))
        self.method_var = tk.StringVar(value=" ")
        self.method_combobox = ttk.Combobox(
            main_frame,
            textvariable=self.method_var,
            values=[
                "Gauss-Jordan",
                "Gauss",
                "Cramer",
                "Transponer",
                "Inversa",
                "Determinante",
                "Independencia",
            ],
            state="readonly",
            width=16,
        )
        self.method_combobox.grid(row=1, column=3, sticky="w")
        self.method_combobox.bind('<<ComboboxSelected>>', self._on_method_select)

        # Campos de filas y columnas
        ttk.Label(main_frame, text="Filas:", style='Dark.TLabel').grid(row=2, column=0, sticky="w", pady=5)
        self.rows_var = tk.StringVar(value="0")
        self.rows_spinbox = tk.Spinbox(main_frame, from_=1, to=20, width=6, textvariable=self.rows_var, bg="#393e46", fg="#e0e0e0", font=('Segoe UI', 11))
        self.rows_spinbox.grid(row=2, column=1, sticky="w", padx=(0, 20))
        ttk.Label(main_frame, text="Columnas:", style='Dark.TLabel').grid(row=2, column=2, sticky="e", padx=(0,5))
        self.cols_var = tk.StringVar(value="0")
        self.cols_spinbox = tk.Spinbox(main_frame, from_=1, to=20, width=6, textvariable=self.cols_var, bg="#393e46", fg="#e0e0e0", font=('Segoe UI', 11))
        self.cols_spinbox.grid(row=2, column=3, sticky="w")

        # Botón crear matriz
        ttk.Button(main_frame, text="Crear matriz", command=self.create_matrix, style='Dark.TButton').grid(row=3, column=0, columnspan=4, pady=(10, 20), sticky="ew")

        # Lista de matrices
        # --- Lista de Matrices en panel lateral izquierdo (Calculadora) ---
        # Etiqueta en esquina superior izquierda
        ttk.Label(self.calc_left_panel, text="Matrices almacenadas:", style='Dark.TLabel')\
            .grid(row=0, column=0, sticky="nw", pady=(12,5), padx=(20,0))  # <-- Coordenadas etiqueta (Calculadora)

        # Contenedor con scrollbar para la lista de matrices (panel izquierdo)
        matrix_list_frame = ttk.Frame(self.calc_left_panel, style='Dark.TFrame')
        # Colocar la lista justo debajo de la etiqueta y hacer que ocupe todo el alto disponible
        matrix_list_frame.grid(row=1, column=0, sticky="nsew", pady=(0,10), padx=(20,0))  # <-- Coordenadas/Tamaño lista (Calculadora)
        # Permitir estiramiento horizontal/vertical del listbox dentro del frame
        matrix_list_frame.grid_columnconfigure(0, weight=1)
        matrix_list_frame.grid_rowconfigure(0, weight=1)  # <-- Ajusta el estiramiento vertical del listbox
        # Guardar referencia para sincronizar tamaño con el listbox de vectores
        self.matrix_list_frame = matrix_list_frame
        matrix_list_frame.grid_propagate(False)
        matrix_list_frame.configure(width=260, height=705)

        self.matrix_listbox = tk.Listbox(matrix_list_frame, height=6, font=('Segoe UI', 11), bg="#393e46", fg="#e0e0e0", selectbackground="#00adb5", selectforeground="#23272e", borderwidth=0, highlightthickness=0, exportselection=0)
        self.matrix_listbox.grid(row=0, column=0, sticky="nsew")
        matrix_scrollbar = ttk.Scrollbar(matrix_list_frame, orient=tk.VERTICAL, command=self.matrix_listbox.yview)
        matrix_scrollbar.grid(row=0, column=1, sticky="ns")  # <-- Side bar (scroll) asociado a la lista (Calculadora)
        self.matrix_listbox.configure(yscrollcommand=matrix_scrollbar.set)
        self.matrix_listbox.bind('<<ListboxSelect>>', self._on_matrix_select)

        # Botonera centrada (alinea con "Crear matriz")
        action_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        action_frame.grid(row=5, column=0, columnspan=4)
        action_buttons = ttk.Frame(action_frame, style='Dark.TFrame')
        action_buttons.pack(anchor='center')
        ttk.Button(action_buttons, text="Ver", command=self.view_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Modificar", command=self.modify_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Eliminar", command=self.delete_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons, text="Resolver", command=self.solve_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        # Área para ingresar datos de la matriz
        ttk.Label(main_frame, text="Datos de la matriz:", style='Title.TLabel').grid(row=6, column=0, columnspan=4, sticky="w", pady=(10,5))
        self.matrix_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        self.matrix_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(0,10))

    # Área de resultados (solución) con su propio scroll (los pasos se movieron al panel derecho)
        result_container = ttk.Frame(main_frame, style='Dark.TFrame')
        result_container.grid(row=8, column=0, columnspan=4, sticky="nsew", pady=(10,0))
        result_container.grid_rowconfigure(1, weight=1)
        result_container.grid_columnconfigure(0, weight=1)

        ttk.Label(result_container, text="Resultado", style='Title.TLabel').grid(row=0, column=0, sticky="w", pady=(0,5))
        
        # Frame para el texto de resultados con scroll
        solution_frame = ttk.Frame(result_container)
        solution_frame.grid(row=1, column=0, sticky="nsew")
        solution_frame.grid_rowconfigure(0, weight=1)
        solution_frame.grid_columnconfigure(0, weight=1)

        self.result_text = tk.Text(solution_frame, height=16, width=79, font=('Segoe UI', 13), bg="#23272e", fg="#00adb5", bd=0, highlightthickness=0)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        result_scrollbar = ttk.Scrollbar(solution_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

    # (Sección de "Pasos" eliminada aquí; ahora vive en self.calc_proc_panel)

    def create_independence_widgets(self, parent_frame):
        """Crea todos los widgets para la pestaña de independencia de vectores
        con la misma estructura de layout/scroll que la pestaña de matrices."""

        # --- Contenedor con scroll (izquierda) + Procedimiento a la derecha ---
        main_frame = ttk.Frame(parent_frame, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        vector_content_stack = ttk.Frame(main_frame, style='Dark.TFrame')
        vector_content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vector_canvas = tk.Canvas(vector_content_stack, bg="#23272e", highlightthickness=0)
        vector_scrollbar = ttk.Scrollbar(vector_content_stack, orient=tk.VERTICAL, command=self.vector_canvas.yview)
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
        self.ind_proc_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        self.ind_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12,0), pady=0)
        ttk.Label(self.ind_proc_panel, text="Procedimiento", style='Title.TLabel').pack(anchor='nw', pady=(10,5))
        ind_steps_container = ttk.Frame(self.ind_proc_panel, style='Dark.TFrame')
        ind_steps_container.pack(fill=tk.BOTH, expand=True)
        ind_steps_container.rowconfigure(0, weight=1)
        ind_steps_container.columnconfigure(0, weight=1)
        self.independence_steps_text = tk.Text(ind_steps_container, font=('Consolas', 12), bg="#23272e", fg="#e0e0e0", bd=0, highlightthickness=0, width=50)
        self.independence_steps_text.grid(row=0, column=0, sticky='nsew')
        ind_steps_scrollbar = ttk.Scrollbar(ind_steps_container, orient=tk.VERTICAL, command=self.independence_steps_text.yview)
        ind_steps_scrollbar.grid(row=0, column=1, sticky='ns')
        self.independence_steps_text.configure(yscrollcommand=ind_steps_scrollbar.set)

    # --- Contenedor de contenido centrado ---
        self.vector_center_wrapper = ttk.Frame(self.vector_scrollable_frame, style='Dark.TFrame')
        self.vector_center_wrapper.pack(fill='x', expand=True)
        # Distribución: 0 = panel izquierdo (no expandir), 1 = contenido (expandir), 2 = separador derecho (no expandir)
        self.vector_center_wrapper.grid_columnconfigure(0, weight=0)
        self.vector_center_wrapper.grid_columnconfigure(1, weight=1)
        self.vector_center_wrapper.grid_columnconfigure(2, weight=0)

        self.vector_content_container = ttk.Frame(self.vector_center_wrapper, style='Dark.TFrame')
        # Mover contenido a la izquierda con margen respecto al panel lateral
        self.vector_content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')  # <-- Ajusta margen contenido (Vectores)

        # --- Panel lateral izquierdo para Conjuntos de Vectores ---
        # Permite estiramiento vertical del panel lateral
        self.vector_center_wrapper.grid_rowconfigure(0, weight=1)
        self.vec_left_panel = ttk.Frame(self.vector_center_wrapper, style='Dark.TFrame')
        # Coordenadas panel izquierdo (Vectores): esquina superior izquierda
        self.vec_left_panel.grid(row=0, column=0, sticky='nsw', padx=(0,10), pady=(0,0))  # <-- Coordenadas/Tamaño panel lateral (Vectores)
        self.vec_left_panel.grid_columnconfigure(0, weight=1)
        self.vec_left_panel.grid_rowconfigure(1, weight=1)  # <-- La fila 1 contendrá la lista; se estira en Y

        container = self.vector_content_container
        # Configurar columnas para que escalen horizontalmente
        for c in range(4):
            container.grid_columnconfigure(c, weight=1)

        # Título
        ttk.Label(container, text="Independencia de Vectores", style='Title.TLabel').grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 20))

        # --- Controles superiores ---
        ttk.Label(container, text="Nombre:", style='Dark.TLabel').grid(row=1, column=0, sticky='w')
        self.vector_name_entry = ttk.Entry(container, width=18, style='Entry.TEntry')
        self.vector_name_entry.grid(row=1, column=1, sticky='w', padx=(0, 20))

        ttk.Label(container, text="Nº Vectores:", style='Dark.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.num_vectors_var = tk.StringVar(value="0")
        num_vectors_spinbox = tk.Spinbox(container, from_=1, to=20, width=6, textvariable=self.num_vectors_var, bg="#393e46", fg="#e0e0e0")
        num_vectors_spinbox.grid(row=2, column=1, sticky='w', padx=(0,20))

        ttk.Label(container, text="Dimensión:", style='Dark.TLabel').grid(row=2, column=2, sticky='e', padx=(0,5))
        self.dim_vectors_var = tk.StringVar(value="0")
        dim_vectors_spinbox = tk.Spinbox(container, from_=1, to=20, width=6, textvariable=self.dim_vectors_var, bg="#393e46", fg="#e0e0e0")
        dim_vectors_spinbox.grid(row=2, column=3, sticky='w')

        ttk.Button(container, text="Crear Conjunto de Vectores", style='Dark.TButton', command=self.create_vector_set_ui).grid(row=3, column=0, columnspan=4, pady=(10, 20), sticky='ew')

        # --- Lista de Conjuntos y Acciones (distribución similar a matrices) ---
        # --- Lista de Conjuntos de Vectores en panel lateral izquierdo (Vectores) ---
        ttk.Label(self.vec_left_panel, text="Conjuntos de Vectores Almacenados:", style='Dark.TLabel')\
            .grid(row=0, column=0, sticky='nw', pady=(12,5), padx=(20,0))  # <-- Coordenadas etiqueta (Vectores)
        # Contenedor con scrollbar para la lista de conjuntos de vectores
        vector_list_frame = ttk.Frame(self.vec_left_panel, style='Dark.TFrame')
        vector_list_frame.grid_propagate(False)
        vector_list_frame.configure(width=260, height=705)
        vector_list_frame.grid(row=1, column=0, sticky='nsew', pady=(0,10), padx=(20,0))  # <-- Coordenadas/Tamaño lista (Vectores)
        vector_list_frame.grid_columnconfigure(0, weight=1)
        vector_list_frame.grid_rowconfigure(0, weight=1)
        # Guardar referencia para sincronizar tamaño con el listbox de matrices
        self.vector_list_frame = vector_list_frame

        self.vector_set_listbox = tk.Listbox(vector_list_frame, height=6, font=('Segoe UI', 11), bg="#393e46", fg="#e0e0e0", selectbackground="#00adb5", selectforeground="#23272e", borderwidth=0, highlightthickness=0, exportselection=0)
        self.vector_set_listbox.grid(row=0, column=0, sticky='nsew')
        vector_scrollbar = ttk.Scrollbar(vector_list_frame, orient=tk.VERTICAL, command=self.vector_set_listbox.yview)
        vector_scrollbar.grid(row=0, column=1, sticky='ns')  # <-- Side bar (scroll) asociado a la lista (Vectores)
        self.vector_set_listbox.configure(yscrollcommand=vector_scrollbar.set)
        self.vector_set_listbox.bind('<<ListboxSelect>>', self._on_vector_set_select)

        # Botonera centrada (alinea con "Crear Conjunto de Vectores")
        vector_action_frame = ttk.Frame(container, style='Dark.TFrame')
        vector_action_frame.grid(row=5, column=0, columnspan=4)
        vector_action_buttons = ttk.Frame(vector_action_frame, style='Dark.TFrame')
        vector_action_buttons.pack(anchor='center')
        ttk.Button(vector_action_buttons, text="Ver", command=self.view_vector_set, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(vector_action_buttons, text="Modificar", command=self.modify_vector_set_ui, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(vector_action_buttons, text="Eliminar", command=self.delete_vector_set, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        # Ubicar Verificar Independencia junto a Eliminar
        ttk.Button(vector_action_buttons, text="Verificar Independencia", command=self.run_independence_check, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        # --- Área de datos de vectores ---
        ttk.Label(container, text="Datos del conjunto:", style='Title.TLabel').grid(row=6, column=0, columnspan=4, sticky='w', pady=(10,5))
        self.vector_entries_frame = ttk.Frame(container, style='Dark.TFrame')
        self.vector_entries_frame.grid(row=7, column=0, columnspan=4, sticky='ew', pady=(0,10))

        # --- Área de resultados con scroll (igual estilo que matrices) ---
        results_container = ttk.Frame(container, style='Dark.TFrame')
        results_container.grid(row=8, column=0, columnspan=4, sticky='nsew', pady=(10,0))
        results_container.grid_rowconfigure(1, weight=1)
        results_container.grid_rowconfigure(3, weight=1)
        results_container.grid_columnconfigure(0, weight=1)

        ttk.Label(results_container, text="Resultado", style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        solution_frame_vec = ttk.Frame(results_container)
        solution_frame_vec.grid(row=1, column=0, sticky='nsew')
        solution_frame_vec.grid_rowconfigure(0, weight=1)
        solution_frame_vec.grid_columnconfigure(0, weight=1)

        self.independence_result_text = tk.Text(solution_frame_vec, height=16, width=79, font=('Segoe UI', 13), bg="#23272e", fg="#00adb5", bd=0, highlightthickness=0)
        self.independence_result_text.grid(row=0, column=0, sticky='nsew')
        result_scrollbar_vec = ttk.Scrollbar(solution_frame_vec, orient=tk.VERTICAL, command=self.independence_result_text.yview)
        result_scrollbar_vec.grid(row=0, column=1, sticky='ns')
        self.independence_result_text.configure(yscrollcommand=result_scrollbar_vec.set)

    # (Procedimiento movido al panel derecho)

    def create_operators_widgets(self, parent_frame):
        """Crea la pestaña para operar conjuntos de matrices (sumar, restar, multiplicar)."""
        # Contenedor con scroll (izquierda) + Procedimiento a la derecha
        main_frame = ttk.Frame(parent_frame, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        ops_content_stack = ttk.Frame(main_frame, style='Dark.TFrame')
        ops_content_stack.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.ops_canvas = tk.Canvas(ops_content_stack, bg="#23272e", highlightthickness=0)
        ops_scrollbar = ttk.Scrollbar(ops_content_stack, orient=tk.VERTICAL, command=self.ops_canvas.yview)
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
        self.ops_proc_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        self.ops_proc_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12,0), pady=0)
        ttk.Label(self.ops_proc_panel, text="Procedimiento", style='Title.TLabel').pack(anchor='nw', pady=(10,5))
        ops_steps_container = ttk.Frame(self.ops_proc_panel, style='Dark.TFrame')
        ops_steps_container.pack(fill=tk.BOTH, expand=True)
        ops_steps_container.rowconfigure(0, weight=1)
        ops_steps_container.columnconfigure(0, weight=1)
        self.ops_steps_text = tk.Text(ops_steps_container, font=('Consolas', 12), bg="#23272e", fg="#e0e0e0", bd=0, highlightthickness=0, width=50)
        self.ops_steps_text.grid(row=0, column=0, sticky='nsew')
        steps_scrollbar_ops_right = ttk.Scrollbar(ops_steps_container, orient=tk.VERTICAL, command=self.ops_steps_text.yview)
        steps_scrollbar_ops_right.grid(row=0, column=1, sticky='ns')
        self.ops_steps_text.configure(yscrollcommand=steps_scrollbar_ops_right.set)

    # Wrapper centrado
        self.ops_center_wrapper = ttk.Frame(self.ops_scrollable_frame, style='Dark.TFrame')
        self.ops_center_wrapper.pack(fill='x', expand=True)
        # Distribución: 0 = panel izquierdo (no expandir), 1 = contenido (expandir), 2 = separador derecho (no expandir)
        self.ops_center_wrapper.grid_columnconfigure(0, weight=0)
        self.ops_center_wrapper.grid_columnconfigure(1, weight=1)
        self.ops_center_wrapper.grid_columnconfigure(2, weight=0)
        self.ops_content_container = ttk.Frame(self.ops_center_wrapper, style='Dark.TFrame')
        # Mover contenido a la izquierda con margen respecto al panel lateral
        self.ops_content_container.grid(row=0, column=1, padx=(0,20), pady=20, sticky='nw')  # <-- Ajusta margen contenido (Operadores)

        # --- Panel lateral izquierdo para Conjuntos de Matrices (Operadores) ---
        self.ops_center_wrapper.grid_rowconfigure(0, weight=1)
        self.ops_left_panel = ttk.Frame(self.ops_center_wrapper, style='Dark.TFrame')
        # Coordenadas panel izquierdo (Operadores): esquina superior izquierda
        self.ops_left_panel.grid(row=0, column=0, sticky='nsw', padx=(0,10), pady=(0,0))  # <-- Coordenadas/Tamaño panel lateral (Operadores)
        self.ops_left_panel.grid_columnconfigure(0, weight=1)
        self.ops_left_panel.grid_rowconfigure(1, weight=1)  # <-- La fila 1 contendrá la lista; se estira en Y

        container = self.ops_content_container
        # Ocho columnas para alinear Nombre / Nº Matrices / Filas / Columnas / Operación en una sola fila
        for c in range(8):
            container.grid_columnconfigure(c, weight=1)

        # Título
        ttk.Label(container, text="Operadores de Matrices", style='Title.TLabel').grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 20))

        # Controles superiores
        ttk.Label(container, text="Nombre del conjunto:", style='Dark.TLabel').grid(row=1, column=0, sticky='w')
        self.ops_name_entry = ttk.Entry(container, width=18, style='Entry.TEntry')
        self.ops_name_entry.grid(row=1, column=1, sticky='w', padx=(0, 20))

        ttk.Label(container, text="Nº Matrices:", style='Dark.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.num_mats_var = tk.StringVar(value="0")
        num_mats_spin = tk.Spinbox(container, from_=1, to=10, width=6, textvariable=self.num_mats_var, bg="#393e46", fg="#e0e0e0")
        num_mats_spin.grid(row=2, column=1, sticky='w', padx=(0, 20))

        ttk.Label(container, text="Filas:", style='Dark.TLabel').grid(row=2, column=2, sticky='e')
        self.ops_rows_var = tk.StringVar(value="0")
        ops_rows_spin = tk.Spinbox(container, from_=1, to=20, width=6, textvariable=self.ops_rows_var, bg="#393e46", fg="#e0e0e0")
        ops_rows_spin.grid(row=2, column=3, sticky='w')

        ttk.Label(container, text="Columnas:", style='Dark.TLabel').grid(row=2, column=4, sticky='e')
        self.ops_cols_var = tk.StringVar(value="0")
        ops_cols_spin = tk.Spinbox(container, from_=1, to=20, width=6, textvariable=self.ops_cols_var, bg="#393e46", fg="#e0e0e0")
        ops_cols_spin.grid(row=2, column=5, sticky='w')

        # Selector de operación al lado derecho de Filas y Columnas
        ttk.Label(container, text="Operación:", style='Dark.TLabel').grid(row=2, column=6, sticky='e', padx=(10,5))
        self.ops_method_var = tk.StringVar(value=" ")
        self.ops_method_combobox = ttk.Combobox(container, textvariable=self.ops_method_var, values=["Suma", "Resta", "Multiplicación"], state="readonly", width=16)
        self.ops_method_combobox.grid(row=2, column=7, sticky='w')

        ttk.Button(container, text="Crear Conjunto de Matrices", style='Dark.TButton', command=self.create_matrix_set_ui).grid(row=3, column=0, columnspan=8, pady=(10, 20), sticky='ew')

        # Lista de conjuntos + acciones
        # --- Lista de Conjuntos de Matrices en panel lateral izquierdo (Operadores) ---
        ttk.Label(self.ops_left_panel, text="Conjuntos de Matrices Almacenados:", style='Dark.TLabel')\
            .grid(row=0, column=0, sticky='nw', pady=(12,5), padx=(20,0))  # <-- Coordenadas etiqueta (Operadores)
        ops_list_frame = ttk.Frame(self.ops_left_panel, style='Dark.TFrame')
        ops_list_frame.grid_propagate(False)
        ops_list_frame.configure(width=260, height=705)
        ops_list_frame.grid(row=1, column=0, sticky='nsew', pady=(0,10), padx=(20,0))  # <-- Coordenadas/Tamaño lista (Operadores)
        ops_list_frame.grid_columnconfigure(0, weight=1)
        ops_list_frame.grid_rowconfigure(0, weight=1)
        self.matrix_set_listbox = tk.Listbox(ops_list_frame, height=6, font=('Segoe UI', 11), bg="#393e46", fg="#e0e0e0", selectbackground="#00adb5", selectforeground="#23272e", borderwidth=0, highlightthickness=0, exportselection=0)
        self.matrix_set_listbox.grid(row=0, column=0, sticky='nsew')
        ops_scrollbar_list = ttk.Scrollbar(ops_list_frame, orient=tk.VERTICAL, command=self.matrix_set_listbox.yview)
        ops_scrollbar_list.grid(row=0, column=1, sticky='ns')  # <-- Side bar (scroll) asociado a la lista (Operadores)
        self.matrix_set_listbox.configure(yscrollcommand=ops_scrollbar_list.set)
        self.matrix_set_listbox.bind('<<ListboxSelect>>', self._on_matrix_set_select)

        # Botonera centrada (alinea con "Crear Conjunto de Matrices")
        ops_action_frame = ttk.Frame(container, style='Dark.TFrame')
        ops_action_frame.grid(row=5, column=0, columnspan=8)
        ops_action_buttons = ttk.Frame(ops_action_frame, style='Dark.TFrame')
        ops_action_buttons.pack(anchor='center')
        ttk.Button(ops_action_buttons, text="Ver", style='Dark.TButton', command=self.view_matrix_set).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_action_buttons, text="Modificar", style='Dark.TButton', command=self.modify_matrix_set_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_action_buttons, text="Eliminar", style='Dark.TButton', command=self.delete_matrix_set).pack(side=tk.LEFT, padx=5)
        # Botón Resolver al lado derecho de Eliminar
        ttk.Button(ops_action_buttons, text="Resolver", style='Dark.TButton', command=self.run_matrix_operation).pack(side=tk.LEFT, padx=5)

        # Área de entradas de matrices
        ttk.Label(container, text="Datos del conjunto:", style='Title.TLabel').grid(row=6, column=0, columnspan=8, sticky='w', pady=(10,5))
        self.ops_entries_frame = ttk.Frame(container, style='Dark.TFrame')
        self.ops_entries_frame.grid(row=7, column=0, columnspan=8, sticky='ew', pady=(0,10))

        # Resultados
        results_container = ttk.Frame(container, style='Dark.TFrame')
        results_container.grid(row=8, column=0, columnspan=8, sticky='nsew', pady=(10,0))
        results_container.grid_rowconfigure(1, weight=1)
        results_container.grid_columnconfigure(0, weight=1)
        ttk.Label(results_container, text="Resultado", style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0,5))
        solution_frame_ops = ttk.Frame(results_container)
        solution_frame_ops.grid(row=1, column=0, sticky='nsew')
        solution_frame_ops.grid_rowconfigure(0, weight=1)
        solution_frame_ops.grid_columnconfigure(0, weight=1)
        self.ops_result_text = tk.Text(solution_frame_ops, height=16, width=79, font=('Segoe UI', 13), bg="#23272e", fg="#00adb5", bd=0, highlightthickness=0)
        self.ops_result_text.grid(row=0, column=0, sticky='nsew')
        result_scrollbar_ops = ttk.Scrollbar(solution_frame_ops, orient=tk.VERTICAL, command=self.ops_result_text.yview)
        result_scrollbar_ops.grid(row=0, column=1, sticky='ns')
        self.ops_result_text.configure(yscrollcommand=result_scrollbar_ops.set)

    # (Procedimiento movido al panel derecho)

    def _on_matrix_set_select(self, event):
        sel = self.matrix_set_listbox.curselection()
        if sel:
            self.selected_matrix_set = self.matrix_set_listbox.get(sel[0])

    def update_matrix_set_list(self):
        if not hasattr(self, 'matrix_set_listbox'):
            return
        self.matrix_set_listbox.delete(0, tk.END)
        data = persistencia.cargar_todos_conjuntos_matrices()
        if data:
            for name in data.keys():
                self.matrix_set_listbox.insert(tk.END, name)

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
            messagebox.showwarning("Selección requerida", "Selecciona un conjunto de matrices.")
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
            # Helpers de formateo local para valores y matrices
            def fmt_val(v):
                try:
                    f = float(v)
                    s = ("{:.6f}".format(f)).rstrip('0').rstrip('.')
                    return s if s else "0"
                except Exception:
                    return str(v)

            def show_matrix_block(title, mat_list):
                self.ops_steps_text.insert(tk.END, f"{title}\n")
                self.ops_steps_text.insert(tk.END, self._format_matrix_for_display(mat_list))
                self.ops_steps_text.insert(tk.END, "\n")

            if op == "Suma":
                # Mostrar matrices iniciales
                for idx, m in enumerate(mats, start=1):
                    show_matrix_block(f"M{idx}:", m.to_list())

                res = mats[0]
                paso = 1
                for idx, M in enumerate(mats[1:], start=2):
                    A = res.to_list()
                    B = M.to_list()
                    R = res.sumar(M).to_list()
                    self.ops_steps_text.insert(tk.END, f"Paso {paso}: R{paso} = {'R'+str(paso-1) if paso>1 else 'M1'} + M{idx}\n")
                    # Detalle elemento a elemento
                    for i in range(len(A)):
                        for j in range(len(A[0])):
                            self.ops_steps_text.insert(
                                tk.END,
                                f"  r[{i+1},{j+1}] = {fmt_val(A[i][j])} + {fmt_val(B[i][j])} = {fmt_val(R[i][j])}\n",
                            )
                    show_matrix_block("\nResultado parcial:", R)
                    res = matrices.Matriz(R)
                    paso += 1

                self.ops_result_text.insert(tk.END, "Resultado de la suma:\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))

            elif op == "Resta":
                for idx, m in enumerate(mats, start=1):
                    show_matrix_block(f"M{idx}:", m.to_list())

                res = mats[0]
                paso = 1
                for idx, M in enumerate(mats[1:], start=2):
                    A = res.to_list()
                    B = M.to_list()
                    R = res.restar(M).to_list()
                    self.ops_steps_text.insert(tk.END, f"Paso {paso}: R{paso} = {'R'+str(paso-1) if paso>1 else 'M1'} - M{idx}\n")
                    for i in range(len(A)):
                        for j in range(len(A[0])):
                            self.ops_steps_text.insert(
                                tk.END,
                                f"  r[{i+1},{j+1}] = {fmt_val(A[i][j])} - {fmt_val(B[i][j])} = {fmt_val(R[i][j])}\n",
                            )
                    show_matrix_block("\nResultado parcial:", R)
                    res = matrices.Matriz(R)
                    paso += 1

                self.ops_result_text.insert(tk.END, "Resultado de la resta (M1 - M2 - ...):\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))

            elif op == "Multiplicación":
                # Mostrar matrices iniciales
                for idx, m in enumerate(mats, start=1):
                    show_matrix_block(f"M{idx}:", m.to_list())

                res = mats[0]
                paso = 1
                for idx, M in enumerate(mats[1:], start=2):
                    A = res.to_list()
                    B = M.to_list()
                    # Compatibilidad
                    if len(A[0]) != len(B):
                        raise ValueError(f"Dimensiones incompatibles para multiplicación: {len(A)}x{len(A[0])} * {len(B)}x{len(B[0])}")
                    n, p, mcols = len(A), len(B[0]), len(A[0])
                    R = [[0.0 for _ in range(p)] for __ in range(n)]
                    self.ops_steps_text.insert(tk.END, f"Paso {paso}: R{paso} = {'R'+str(paso-1) if paso>1 else 'M1'} @ M{idx}\n")
                    for i in range(n):
                        for j in range(p):
                            terms = []
                            s = 0.0
                            for k in range(mcols):
                                terms.append(f"{fmt_val(A[i][k])}*{fmt_val(B[k][j])}")
                                s += float(A[i][k]) * float(B[k][j])
                            R[i][j] = s
                            self.ops_steps_text.insert(
                                tk.END,
                                f"  r[{i+1},{j+1}] = " + " + ".join(terms) + f" = {fmt_val(s)}\n",
                            )
                    show_matrix_block("\nResultado parcial:", R)
                    res = matrices.Matriz(R)
                    paso += 1

                self.ops_result_text.insert(tk.END, "Resultado de la multiplicación (M1 @ M2 @ ...):\n")
                self.ops_result_text.insert(tk.END, self._format_matrix_for_display(res.to_list()))
            else:
                messagebox.showerror("Operación desconocida", op)
                return
        except Exception as e:
            messagebox.showerror("Error en operación", str(e))

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
    
    def update_vector_set_list(self):
        self.vector_set_listbox.delete(0, tk.END)
        vector_sets_data = persistencia.cargar_todos_vectores()
        if vector_sets_data:
            for name in vector_sets_data.keys():
                self.vector_set_listbox.insert(tk.END, name)

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

    def _on_vector_set_select(self, event):
        selection = self.vector_set_listbox.curselection()
        if selection:
            self.selected_vector_set = self.vector_set_listbox.get(selection[0])

    def _on_method_select(self, event):
        self.selected_method = self.method_var.get()

    def solve_matrix(self):
        matrix_name = getattr(self, 'selected_matrix', None)
        metodo = getattr(self, 'selected_method', None) # Cambiado para forzar selección

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
                for paso in resultado.get("pasos", []):
                    self.steps_text.insert(tk.END, f"{paso.get('descripcion','')}\n")
                    if 'matriz' in paso:
                        formatted = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted + "\n")
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
            # Mostrar los pasos si existen
            if "pasos" in resultado and resultado["pasos"]:
                for idx, paso in enumerate(resultado["pasos"]):
                    self.steps_text.insert(tk.END, f"Paso {idx+1}: {paso['descripcion']}\n")
                    if 'matriz' in paso:
                        formatted_step_matrix = self._format_matrix_for_display(paso['matriz'])
                        self.steps_text.insert(tk.END, formatted_step_matrix + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la resolución de la matriz: {e}")
    
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
            mod_rows_spinbox = tk.Spinbox(resize_frame, from_=1, to=20, width=5, textvariable=mod_rows_var, bg="#393e46", fg="#e0e0e0")
            mod_rows_spinbox.pack(side=tk.LEFT, padx=(0, 10))

            ttk.Label(resize_frame, text="Columnas:", style='Dark.TLabel').pack(side=tk.LEFT, padx=(0, 5))
            mod_cols_var = tk.StringVar(value=str(cols))
            mod_cols_spinbox = tk.Spinbox(resize_frame, from_=1, to=20, width=5, textvariable=mod_cols_var, bg="#393e46", fg="#e0e0e0")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixCRUDApp(root)
    root.mainloop()