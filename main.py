import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from crud import crear_matriz, listar_matrices, ver_matriz, actualizar_matriz, eliminar_matriz
import persistencia
import matrices

class MatrixCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Matrices")
        self.root.configure(bg="#23272e")

        # Centrar la ventana en la pantalla
        window_width = 900
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background="#23272e")
        style.configure('Dark.TLabel', background="#23272e", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('Dark.TButton', background="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11), borderwidth=0)
        style.map('Dark.TButton', background=[('active', '#00adb5')])
        style.configure('Title.TLabel', background="#23272e", foreground="#00adb5", font=('Segoe UI', 16, 'bold'))
        style.configure('Result.TLabel', background="#23272e", foreground="#e0e0e0", font=('Consolas', 13))
        style.configure('Entry.TEntry', fieldbackground="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('TCombobox', fieldbackground="#393e46", background="#393e46", foreground="#000000")

        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Usar PanedWindow para separar lista (izq) y trabajo (der)
        paned = ttk.Panedwindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left: lista y acciones
        left_frame = ttk.Frame(paned, width=260, style='Dark.TFrame')
        left_frame.pack_propagate(False)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Matrices almacenadas", style='Title.TLabel').pack(anchor="w", pady=(0,8), padx=10)

        self.matrix_listbox = tk.Listbox(left_frame, height=20, font=('Segoe UI', 11), bg="#393e46", fg="#e0e0e0", selectbackground="#00adb5", selectforeground="#23272e", borderwidth=0, highlightthickness=0, exportselection=0)
        self.matrix_listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        self.matrix_listbox.bind('<<ListboxSelect>>', self._on_matrix_select)

        action_frame = ttk.Frame(left_frame, style='Dark.TFrame')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(action_frame, text="Ver", command=self.view_matrix, style='Dark.TButton').pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)
        ttk.Button(action_frame, text="Modificar", command=self.modify_matrix, style='Dark.TButton').pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)
        ttk.Button(action_frame, text="Eliminar", command=self.delete_matrix, style='Dark.TButton').pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

        # Right: creación, editor, operador, resultados
        right_frame = ttk.Frame(paned, style='Dark.TFrame')
        paned.add(right_frame, weight=4)

        # Header / creación rápida
        header_frame = ttk.Frame(right_frame, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        ttk.Label(header_frame, text="Calculadora de Matrices", style='Title.TLabel').grid(row=0, column=0, columnspan=4, sticky="w")

        ttk.Label(header_frame, text="Nombre:", style='Dark.TLabel').grid(row=1, column=0, sticky="w", pady=6)
        self.name_entry = ttk.Entry(header_frame, width=6, style='Entry.TEntry')
        self.name_entry.grid(row=1, column=1, sticky="w", padx=(5,15))

        ttk.Label(header_frame, text="Filas:", style='Dark.TLabel').grid(row=1, column=2, sticky="e")
        self.rows_var = tk.StringVar(value="1")
        self.rows_spinbox = tk.Spinbox(header_frame, from_=1, to=20, width=5, textvariable=self.rows_var, bg="#393e46", fg="#e0e0e0", font=('Segoe UI', 11))
        self.rows_spinbox.grid(row=1, column=3, sticky="w", padx=(5,15))

        ttk.Label(header_frame, text="Columnas:", style='Dark.TLabel').grid(row=1, column=4, sticky="e")
        self.cols_var = tk.StringVar(value="1")
        self.cols_spinbox = tk.Spinbox(header_frame, from_=1, to=20, width=5, textvariable=self.cols_var, bg="#393e46", fg="#e0e0e0", font=('Segoe UI', 11))
        self.cols_spinbox.grid(row=1, column=5, sticky="w", padx=(5,15))

        ttk.Label(header_frame, text="Método:", style='Dark.TLabel').grid(row=2, column=0, sticky="w", pady=(6,0))
        self.method_var = tk.StringVar(value="Gauss-Jordan")
        self.method_combobox = ttk.Combobox(header_frame, textvariable=self.method_var, values=["Gauss-Jordan", "Gauss"], state="readonly", width=14)
        self.method_combobox.grid(row=2, column=1, sticky="w", pady=(6,0))
        self.method_combobox.bind('<<ComboboxSelected>>', self._on_method_select)

        # Botón para comprobar independencia lineal de vectores
        ttk.Button(header_frame, text="Vectores", command=self.open_vector_checker, style='Dark.TButton').grid(row=2, column=2, sticky="w", padx=5, pady=(6,0))
        
        ttk.Button(header_frame, text="Crear matriz", command=self.create_matrix, style='Dark.TButton').grid(row=2, column=3, columnspan=2, sticky="w", padx=5, pady=(6,0))

        ttk.Button(header_frame, text="Resolver seleccionada", command=self.solve_matrix, style='Dark.TButton').grid(row=2, column=5, sticky="e", padx=5, pady=(6,0))

        # Area de edición de matriz (crear/editar)
        editor_label = ttk.Label(right_frame, text="Editor de matriz (crear/editar)", style='Title.TLabel')
        editor_label.pack(anchor="w", padx=10, pady=(6,0))

        # Crear un área de editor desplazable (canvas + scrollbar).
        # self.matrix_canvas_frame es el contenedor que se mostrará/ocultará.
        self.matrix_canvas_frame = ttk.Frame(right_frame, style='Dark.TFrame')
        self.matrix_canvas = tk.Canvas(self.matrix_canvas_frame, bg="#23272e", highlightthickness=0)
        self.matrix_scrollbar = ttk.Scrollbar(self.matrix_canvas_frame, orient=tk.VERTICAL, command=self.matrix_canvas.yview)
        self.matrix_canvas.configure(yscrollcommand=self.matrix_scrollbar.set)

        # Frame interior donde colocaremos los widgets del editor
        self.matrix_frame = ttk.Frame(self.matrix_canvas, style='Dark.TFrame', relief=tk.FLAT)
        self._matrix_window = self.matrix_canvas.create_window((0, 0), window=self.matrix_frame, anchor='nw')

        # Ajustes de empaquetado (no mostrar por defecto, se mostrará con create_matrix_input_ui)
        self.matrix_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.matrix_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Actualizar la región desplazable cuando cambie el tamaño del contenido
        def _on_frame_configure(event):
            self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))
        self.matrix_frame.bind("<Configure>", _on_frame_configure)

        # Asegurar que la ventana interior se ajuste al ancho del canvas
        def _on_canvas_configure(event):
            self.matrix_canvas.itemconfig(self._matrix_window, width=event.width)
        self.matrix_canvas.bind("<Configure>", _on_canvas_configure)
        # no hacer pack aquí para evitar dejar espacio vacío al iniciar

        # Operador de matrices (A op B)
        op_container = ttk.Labelframe(right_frame, text="Operador de matrices", style='Dark.TFrame')
        op_container.pack(fill=tk.X, padx=10, pady=(6,8))

        op_inner = ttk.Frame(op_container, style='Dark.TFrame')
        op_inner.pack(fill=tk.X, padx=8, pady=6)

        ttk.Label(op_inner, text="Matriz A:", style='Dark.TLabel').grid(row=0, column=0, sticky="w")
        self.op_a_var = tk.StringVar()
        self.op_a_cb = ttk.Combobox(op_inner, textvariable=self.op_a_var, values=[], state='readonly', width=10)
        self.op_a_cb.grid(row=0, column=1, padx=(5, 15))

        ttk.Label(op_inner, text="Matriz B:", style='Dark.TLabel').grid(row=0, column=2, sticky="w")
        self.op_b_var = tk.StringVar()
        self.op_b_cb = ttk.Combobox(op_inner, textvariable=self.op_b_var, values=[], state='readonly', width=10)
        self.op_b_cb.grid(row=0, column=3, padx=(5, 15))

        ttk.Label(op_inner, text="Operación:", style='Dark.TLabel').grid(row=1, column=0, sticky="w", pady=(8,0))
        self.op_var = tk.StringVar(value='Sumar')
        self.op_cb = ttk.Combobox(op_inner, textvariable=self.op_var, values=['Sumar', 'Restar', 'Multiplicar'], state='readonly', width=12)
        self.op_cb.grid(row=1, column=1, sticky='w', pady=(8,0))

        ttk.Button(op_inner, text="Operar", command=self.perform_matrix_operation, style='Dark.TButton').grid(row=1, column=2, padx=5, pady=(8,0))
        ttk.Button(op_inner, text="Guardar resultado", command=self.save_operation_result, style='Dark.TButton').grid(row=1, column=3, padx=5, pady=(8,0))

        # Notebook para Resultado y Pasos
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6,0))

        # Resultado tab
        result_tab = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(result_tab, text="Resultado")

        self.result_text = tk.Text(result_tab, height=8, width=60, font=('Segoe UI', 13), bg="#23272e", fg="#00adb5", bd=0, highlightthickness=0)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        result_scrollbar = ttk.Scrollbar(result_tab, orient=tk.VERTICAL, command=self.result_text.yview)
        result_scrollbar.place(relx=0.985, rely=0.02, relheight=0.96)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        # Pasos tab
        steps_tab = ttk.Frame(notebook, style='Dark.TFrame')
        notebook.add(steps_tab, text="Pasos de solución")

        self.steps_text = tk.Text(steps_tab, height=16, width=60, font=('Consolas', 12), bg="#23272e", fg="#e0e0e0", bd=0, highlightthickness=0)
        self.steps_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        steps_scrollbar = ttk.Scrollbar(steps_tab, orient=tk.VERTICAL, command=self.steps_text.yview)
        steps_scrollbar.place(relx=0.985, rely=0.02, relheight=0.96)
        self.steps_text.configure(yscrollcommand=steps_scrollbar.set)

        # Inicializar selección y cargar matrices almacenadas al iniciar
        self.selected_matrix = None
        self.selected_method = self.method_var.get()
        self._last_operation_result = None
        self.update_matrix_list()

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
            # Usar símbolos más claros para los paréntesis que encierran la matriz
            # Primera fila: ⎡ ... ⎤
            # Filas intermedias: | ... |
            # Última fila: ⎣ ... ⎦
            if i == 0:
                line += "⎡ "
            elif i == num_rows - 1:
                line += "⎣ "
            else:
                line += "| "
                
            for j, cell in enumerate(row):
                line += cell.rjust(col_widths[j] + 1)
            
            line += " "
            if i == 0:
                line += " ⎤"
            elif i == num_rows - 1:
                line += " ⎦"
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
        # actualizar comboboxes del operador
        names = list(matrices_data.keys()) if matrices_data else []
        self.op_a_cb['values'] = names
        self.op_b_cb['values'] = names

    def view_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
            return
            
        matrix_name = self.matrix_listbox.get(selection[0])
        matrix_data = persistencia.cargar_matriz(matrix_name)
        
        if matrix_data:
            matrix_str = self._format_matrix_for_display(matrix_data['datos'])
            
            self.show_result(f"Matriz: {matrix_data['nombre']}\n"
                            f"Dimensiones: {matrix_data['filas']}x{matrix_data['columnas']}\n\n"
                            f"{matrix_str}")
        else:
            messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")

    def delete_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
            return
            
        matrix_name = self.matrix_listbox.get(selection[0])
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar la matriz '{matrix_name}'?"):
            # Llamar directamente a la función de persistencia
            todas_matrices = persistencia.cargar_todas_matrices()
            
            if matrix_name not in todas_matrices:
                messagebox.showerror("Error", f"No se pudo encontrar la matriz '{matrix_name}'.")
                return
                
            # Eliminar la matriz del diccionario
            del todas_matrices[matrix_name]
            
            # Guardar los cambios
            try:
                with open(persistencia.ARCHIVO_DATOS, 'w') as file:
                    json.dump(todas_matrices, file, indent=4)
                messagebox.showinfo("Éxito", f"Matriz '{matrix_name}' eliminada exitosamente.")
                self.update_matrix_list()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la matriz: {e}")

    def _on_matrix_select(self, event):
        selection = self.matrix_listbox.curselection()
        if selection:
            self.selected_matrix = self.matrix_listbox.get(selection[0])

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
            messagebox.showwarning("Selección requerida", "Por favor selecciona un método de resolución (Gauss o Gauss-Jordan).")
            return

        try:
            matriz_data = persistencia.cargar_matriz(matrix_name)
            if matriz_data is None:
                messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")
                return
            matriz_obj = matrices.Matriz(matriz_data['datos'])
            if metodo == "Gauss-Jordan":
                resultado = matriz_obj.gauss_jordan()
            else:
                resultado = matriz_obj.gauss()
            # Mostrar la solución y el procedimiento
            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)
            if resultado["solucion"] == "Sin solución" or resultado["solucion"] == "Sistema incompatible, no tiene solución.":
                self.result_text.insert(tk.END, "El sistema es inconsistente (no tiene solución).\n")
            else:
                # Mostrar el mensaje de tipo de solución si existe
                if "mensaje" in resultado:
                    self.result_text.insert(tk.END, resultado["mensaje"] + "\n\n")
                for variable, valor in resultado["solucion"].items():
                    self.result_text.insert(tk.END, f"{variable} = {valor}\n")

            for idx, paso in enumerate(resultado["pasos"]):
                self.steps_text.insert(tk.END, f"Paso {idx+1}: {paso['descripcion']}\n")
                
                matriz_paso_float = []
                for fila_str in paso['matriz']:
                    matriz_paso_float.append([float(x) for x in fila_str])

                formatted_step_matrix = self._format_matrix_for_display(paso['matriz'])
                self.steps_text.insert(tk.END, formatted_step_matrix + "\n")

        except Exception as e:
            messagebox.showerror("Error", f"Error durante la resolución: {e}")

    def perform_matrix_operation(self):
        a_name = self.op_a_var.get()
        b_name = self.op_b_var.get()
        op = self.op_var.get()

        if not a_name or not b_name:
            messagebox.showwarning("Selección requerida", "Selecciona las dos matrices A y B para operar.")
            return

        a_data = persistencia.cargar_matriz(a_name)
        b_data = persistencia.cargar_matriz(b_name)
        if a_data is None or b_data is None:
            messagebox.showerror("Error", "No se pudieron cargar una o ambas matrices seleccionadas.")
            return

        try:
            A = matrices.Matriz(a_data['datos'])
            B = matrices.Matriz(b_data['datos'])
            if op == 'Sumar':
                resultado = A.sumar(B)
            elif op == 'Restar':
                resultado = A.restar(B)
            else:
                resultado = A.multiplicar(B)

            # Mostrar resultado y pasos
            self.result_text.delete(1.0, tk.END)
            self.steps_text.delete(1.0, tk.END)
            if 'mensaje' in resultado:
                self.result_text.insert(tk.END, resultado['mensaje'] + "\n\n")
            # mostrar datos
            formatted = self._format_matrix_for_display(resultado['datos'])
            self.result_text.insert(tk.END, formatted)

            for idx, paso in enumerate(resultado['pasos']):
                self.steps_text.insert(tk.END, f"Paso {idx+1}: {paso['descripcion']}\n")
                self.steps_text.insert(tk.END, self._format_matrix_for_display(paso['matriz']) + "\n")

            # guardar temporalmente resultado para que el botón guardado lo use
            self._last_operation_result = resultado

        except Exception as e:
            messagebox.showerror("Error en operación", str(e))

    def save_operation_result(self):
        if not hasattr(self, '_last_operation_result') or not self._last_operation_result:
            messagebox.showwarning("Nada para guardar", "Primero realiza una operación y luego guarda el resultado.")
            return

        # pedir nombre para la nueva matriz
        name = tk.simpledialog.askstring("Nombre", "Introduce un nombre (una letra mayúscula) para la matriz resultado:")
        if not name:
            return
        name = name.strip()
        if not name.isalpha() or not name.isupper() or len(name) != 1:
            messagebox.showerror("Nombre inválido", "El nombre debe ser una sola letra mayúscula (A-Z).")
            return

        todas = persistencia.cargar_todas_matrices()
        if name in todas:
            messagebox.showerror("Nombre en uso", f"Ya existe una matriz con el nombre '{name}'.")
            return

        datos = self._last_operation_result['datos']
        filas = len(datos)
        cols = len(datos[0]) if filas else 0
        crear_matriz(name, filas, cols, datos)
        messagebox.showinfo("Guardado", f"Matriz '{name}' guardada exitosamente.")
        self.update_matrix_list()

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
        # Asegurar que el área de editor desplazable esté visible (se había ocultado con pack_forget)
        if not self.matrix_canvas_frame.winfo_ismapped():
            # usar fill=BOTH para permitir scroll cuando la ventana es pequeña
            self.matrix_canvas_frame.pack(fill=tk.BOTH, padx=10, pady=(6,8), expand=False)

        # Limpiar frame anterior
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        # Guardar datos originales para comparación posterior si es modificación
        if is_modification:
            self.original_matrix_data_for_modification = {
                'filas': rows,
                'columnas': cols,
                'datos': [row[:] for row in data] if data else [[0]*cols for _ in range(rows)] # Copia profunda
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
            ttk.Label(self.matrix_frame, text=f"Col {j+1}", style='Dark.TLabel').grid(row=1, column=j+1, padx=5, pady=2)

        # Crear entradas para la matriz
        entries = []
        for i in range(rows):
            row_entries = []
            ttk.Label(self.matrix_frame, text=f"Fila {i+1}", style='Dark.TLabel').grid(row=i+2, column=0, padx=5, pady=2)
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
        if is_modification:
            command = lambda: self.update_matrix_data(entries, int(mod_rows_var.get()), int(mod_cols_var.get()), name)
            button_text = "Actualizar Matriz"
        else:
            command = lambda: self.save_matrix_data(entries, rows, cols, name)
            button_text = "Guardar Matriz"

        ttk.Button(self.matrix_frame, text=button_text, command=command, style='Dark.TButton').grid(
            row=rows+3, column=0, columnspan=cols+1, pady=10)

    def redraw_matrix_entries_for_modification(self, rows_var, cols_var, name, old_data):
        try:
            new_rows = int(rows_var.get())
            new_cols = int(cols_var.get())
            if new_rows <= 0 or new_cols <= 0:
                raise ValueError

            # Crear nueva matriz de datos manteniendo los valores antiguos que quepan
            new_data = [[0] * new_cols for _ in range(new_rows)]
            for i in range(min(new_rows, len(old_data))):
                for j in range(min(new_cols, len(old_data[0]))):
                    new_data[i][j] = old_data[i][j]
            
            self.create_matrix_input_ui(new_rows, new_cols, name, is_modification=True, data=new_data)

        except ValueError:
            messagebox.showerror("Dimensiones inválidas", "Las filas y columnas deben ser números enteros positivos.")

    def update_matrix_data(self, entries, rows, cols, name):
        datos = []
        try:
            for i in range(rows):
                fila = []
                for j in range(cols):
                    valor = entries[i][j].get()
                    fila.append(float(valor))
                datos.append(fila)

            # Validar si hubo cambios
            original = getattr(self, 'original_matrix_data_for_modification', None)
            if original and original['filas'] == rows and original['columnas'] == cols and original['datos'] == datos:
                # No hay cambios, limpiar y ocultar editor
                for widget in self.matrix_frame.winfo_children():
                    widget.destroy()
                self.matrix_canvas_frame.pack_forget()
                return

            # Intentar actualizar
            updated = False
            try:
                updated = actualizar_matriz(name, datos, rows, cols)
            except Exception:
                updated = False

            if updated:
                messagebox.showinfo("Éxito", f"Matriz '{name}' actualizada exitosamente.")
                self.update_matrix_list()
                for widget in self.matrix_frame.winfo_children():
                    widget.destroy()
                # ocultar editor después de actualizar
                self.matrix_canvas_frame.pack_forget()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar la matriz '{name}'.")

        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos en todas las celdas.")

    def save_matrix_data(self, entries, rows, cols, name):
        datos = []
        try:
            for i in range(rows):
                fila = []
                for j in range(cols):
                    valor = entries[i][j].get()
                    fila.append(float(valor))
                datos.append(fila)
            
            crear_matriz(name, rows, cols, datos)
            messagebox.showinfo("Éxito", f"Matriz '{name}' creada y guardada exitosamente.")
            self.update_matrix_list()
            
            # Limpiar entradas y resetear valores a 0
            self.name_entry.delete(0, tk.END)
            self.rows_var.set("1")
            self.cols_var.set("1")
            for widget in self.matrix_frame.winfo_children():
                widget.destroy()
            # ocultar editor al terminar
            self.matrix_canvas_frame.pack_forget()
                 
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos en todas las celdas.")
    
    def show_result(self, text):
        self.result_text.delete(1.0, tk.END)
        self.steps_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)

    # --- Interfaz para comprobar independencia de vectores (entrada horizontal) ---
    def open_vector_checker(self):
        win = tk.Toplevel(self.root)
        win.title("Comprobar independencia de vectores")
        win.geometry("700x420")
        win.configure(bg="#23272e")

        top_frame = ttk.Frame(win, style='Dark.TFrame')
        top_frame.pack(fill=tk.X, padx=10, pady=(10,0))

        ttk.Label(top_frame, text="Introduce vectores (horizontal):", style='Title.TLabel').grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(top_frame, text="Modo de visualización:", style='Dark.TLabel').grid(row=1, column=0, sticky="w", pady=(6,0))
        self._vec_orientation = tk.StringVar(value="columnas")
        orientation_cb = ttk.Combobox(top_frame, textvariable=self._vec_orientation,
                                     values=["columnas", "filas"],
                                     state='readonly', width=18)
        orientation_cb.grid(row=1, column=1, sticky="w", pady=(6,0))
        ttk.Label(top_frame, text="(columnas = vertical, filas = horizontal)", style='Dark.TLabel').grid(row=1, column=2, sticky="w", pady=(6,0), padx=(8,0))

        paste_btn = ttk.Button(top_frame, text="Pegar desde portapapeles", style='Dark.TButton',
                               command=lambda: self._paste_clipboard_to_text(txt))
        paste_btn.grid(row=1, column=3, sticky="e", padx=6, pady=(6,0))

        help_label = ttk.Label(win, text=(
            "Formato: escribe un vector por línea, componentes separados por espacio o coma.\n"
            "Ejemplo:\n  1 0 3\n  0 1 2\n\n"
            "Luego elige cómo quieres formar/mostrar la matriz:\n"
            "- 'columnas' -> cada vector será una columna (matriz vertical)\n"
            "- 'filas'    -> cada vector será una fila (matriz horizontal)"
        ), style='Dark.TLabel', justify='left')
        help_label.pack(anchor="w", padx=12, pady=(6,0))

        txt = scrolledtext.ScrolledText(win, height=14, font=('Consolas', 11), bg="#23272e", fg="#e0e0e0", bd=0)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(6,6))

        btn_frame = ttk.Frame(win, style='Dark.TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=8)
        ttk.Button(btn_frame, text="Comprobar", command=lambda: self._check_vectors_text(txt.get("1.0", tk.END), win), style='Dark.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cerrar", command=win.destroy, style='Dark.TButton').pack(side=tk.RIGHT, padx=4)

    def _paste_clipboard_to_text(self, text_widget):
        try:
            data = self.root.clipboard_get()
            # pegar reemplazando el contenido para evitar mezclas
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, data)
        except Exception:
            messagebox.showwarning("Portapapeles", "No hay texto en el portapapeles o no se pudo acceder a él.")

    def _check_vectors_text(self, text, parent_window=None):
        # Asumimos entrada horizontal: un vector por línea
        try:
            vectors = matrices.parse_vectors_text(text)  # debe aceptar vectores horizontales
        except Exception as e:
            messagebox.showerror("Entrada inválida", f"Error leyendo vectores: {e}")
            return

        # Analizar independencia usando la representación canónica (vectores como columnas)
        try:
            analysis = matrices.analyze_vectors(vectors)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo analizar los vectores: {e}")
            return

        orientation = getattr(self, '_vec_orientation', tk.StringVar(value="columnas")).get()
        # Preparar matriz para mostrar según la orientación elegida
        if orientation == "filas":
            A_display = matrices.vectors_to_row_matrix(vectors)
        else:
            A_display = matrices.vectors_to_column_matrix(vectors)

        rank = analysis.get("rank")
        k = len(vectors)
        independent = analysis.get("independent")
        relation = analysis.get("relation")

        # Construir salida: primero la conclusión principal y luego una explicación sencilla
        lines = []
        lines.append("")  # espacio superior
        if independent:
            lines.append("CONCLUSIÓN PRINCIPAL: Los vectores son LINEALMENTE INDEPENDIENTES.")
            lines.append(f"Explicación breve: el rango de la matriz formada por los vectores como columnas es {rank}, igual al número de vectores ({k}).")
            lines.append("Por tanto, la única combinación lineal que produce el vector cero es la combinación trivial (todos los coeficientes = 0).")
        else:
            lines.append("CONCLUSIÓN PRINCIPAL: Los vectores son LINEALMENTE DEPENDIENTES.")
            lines.append(f"Explicación breve: el rango de la matriz formada por los vectores como columnas es {rank}, menor que el número de vectores ({k}).")
            lines.append("Por tanto, existe una combinación lineal no trivial (coeficientes no todos cero) que da el vector cero.")
            if relation:
                coef_str = ", ".join([f"{c:.6g}" for c in relation])
                lines.append("Ejemplo de relación no trivial (coeficientes correspondientes a cada vector):")
                lines.append(f"[{coef_str}]")

        # Información adicional compacta
        lines.append("")
        lines.append(f"Matriz mostrada ({orientation}): {len(A_display)} x {len(A_display[0]) if A_display else 0}")
        lines.append(f"Rango (evaluado sobre vectores como columnas) = {rank}")

        self.result_text.delete(1.0, tk.END)
        self.steps_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "\n".join(lines))

        # Mostrar la matriz formada con la orientación elegida
        self.steps_text.insert(tk.END, "Matriz formada:\n")
        self.steps_text.insert(tk.END, self._format_matrix_for_display(A_display))

        if parent_window:
            try:
                parent_window.lift()
            except Exception:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixCRUDApp(root)
    root.mainloop()