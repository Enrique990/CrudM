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
        window_width = 790
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
        style.configure('Title.TLabel', background="#23272e", foreground="#00adb5", font=('Segoe UI', 18, 'bold'))
        style.configure('Result.TLabel', background="#23272e", foreground="#e0e0e0", font=('Consolas', 13))
        style.configure('Entry.TEntry', fieldbackground="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('TCombobox', fieldbackground="#393e46", background="#393e46", foreground="#000000")

        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self.canvas = tk.Canvas(main_frame, bg="#23272e", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Dark.TFrame')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollable_frame.bind("<Enter>", self._bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel)

        # Frame contenedor para centrar el contenido
        self.content_container = ttk.Frame(self.scrollable_frame, style='Dark.TFrame')
        self.content_container.pack(expand=True, padx=20, pady=20)

        self.selected_matrix = None
        self.selected_method = None

        self.create_widgets()
        self.update_matrix_list()

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_widgets(self):
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
        self.method_var = tk.StringVar(value="Gauss-Jordan")
        self.method_combobox = ttk.Combobox(main_frame, textvariable=self.method_var, values=["Gauss-Jordan", "Gauss"], state="readonly", width=14)
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
        ttk.Label(main_frame, text="Matrices almacenadas:", style='Dark.TLabel').grid(row=4, column=0, columnspan=2, sticky="w", pady=(0,5))
        self.matrix_listbox = tk.Listbox(main_frame, height=6, font=('Segoe UI', 11), bg="#393e46", fg="#e0e0e0", selectbackground="#00adb5", selectforeground="#23272e", borderwidth=0, highlightthickness=0, exportselection=0)
        self.matrix_listbox.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0,10))
        self.matrix_listbox.bind('<<ListboxSelect>>', self._on_matrix_select)

        # Botones de acción
        action_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        action_frame.grid(row=5, column=2, columnspan=2, sticky="ew")
        ttk.Button(action_frame, text="Ver", command=self.view_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Modificar", command=self.modify_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self.delete_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Resolver", command=self.solve_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        # Área para ingresar datos de la matriz
        ttk.Label(main_frame, text="Datos de la matriz:", style='Title.TLabel').grid(row=6, column=0, columnspan=4, sticky="w", pady=(10,5))
        self.matrix_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        self.matrix_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(0,10))

        # ----------------- Operador de matrices -----------------
        ttk.Label(main_frame, text="Operador de matrices:", style='Title.TLabel').grid(row=9, column=0, columnspan=4, sticky="w", pady=(10,5))
        op_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        op_frame.grid(row=10, column=0, columnspan=4, sticky="ew", pady=(0,10))

        ttk.Label(op_frame, text="Matriz A:", style='Dark.TLabel').grid(row=0, column=0, sticky="w")
        self.op_a_var = tk.StringVar()
        self.op_a_cb = ttk.Combobox(op_frame, textvariable=self.op_a_var, values=[], state='readonly', width=8)
        self.op_a_cb.grid(row=0, column=1, padx=(5, 20))

        ttk.Label(op_frame, text="Matriz B:", style='Dark.TLabel').grid(row=0, column=2, sticky="w")
        self.op_b_var = tk.StringVar()
        self.op_b_cb = ttk.Combobox(op_frame, textvariable=self.op_b_var, values=[], state='readonly', width=8)
        self.op_b_cb.grid(row=0, column=3, padx=(5, 20))

        ttk.Label(op_frame, text="Operación:", style='Dark.TLabel').grid(row=1, column=0, sticky="w", pady=(8,0))
        self.op_var = tk.StringVar(value='Sumar')
        self.op_cb = ttk.Combobox(op_frame, textvariable=self.op_var, values=['Sumar', 'Restar', 'Multiplicar'], state='readonly', width=12)
        self.op_cb.grid(row=1, column=1, sticky='w', pady=(8,0))

        ttk.Button(op_frame, text="Operar", command=self.perform_matrix_operation, style='Dark.TButton').grid(row=1, column=2, padx=5, pady=(8,0))
        ttk.Button(op_frame, text="Guardar resultado", command=self.save_operation_result, style='Dark.TButton').grid(row=1, column=3, padx=5, pady=(8,0))

        # Área de resultados (solución y pasos) con su propio scroll
        result_container = ttk.Frame(main_frame, style='Dark.TFrame')
        result_container.grid(row=8, column=0, columnspan=4, sticky="nsew", pady=(10,0))
        result_container.grid_rowconfigure(1, weight=1)
        result_container.grid_columnconfigure(0, weight=1)

        ttk.Label(result_container, text="Solución", style='Title.TLabel').grid(row=0, column=0, sticky="w", pady=(0,5))
        
        # Frame para el texto de resultados con scroll
        solution_frame = ttk.Frame(result_container)
        solution_frame.grid(row=1, column=0, sticky="nsew")
        solution_frame.grid_rowconfigure(0, weight=1)
        solution_frame.grid_columnconfigure(0, weight=1)

        self.result_text = tk.Text(solution_frame, height=8, width=80, font=('Segoe UI', 13), bg="#23272e", fg="#00adb5", bd=0, highlightthickness=0)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        result_scrollbar = ttk.Scrollbar(solution_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        ttk.Label(result_container, text="Pasos de solución", style='Title.TLabel').grid(row=2, column=0, sticky="w", pady=(10,5))

        # Frame para el texto de pasos con scroll
        steps_frame = ttk.Frame(result_container)
        steps_frame.grid(row=3, column=0, sticky="nsew")
        steps_frame.grid_rowconfigure(0, weight=1)
        steps_frame.grid_columnconfigure(0, weight=1)

        self.steps_text = tk.Text(steps_frame, height=16, width=80, font=('Consolas', 12), bg="#23272e", fg="#e0e0e0", bd=0, highlightthickness=0)
        self.steps_text.grid(row=0, column=0, sticky="nsew")
        steps_scrollbar = ttk.Scrollbar(steps_frame, orient=tk.VERTICAL, command=self.steps_text.yview)
        steps_scrollbar.grid(row=0, column=1, sticky="ns")
        self.steps_text.configure(yscrollcommand=steps_scrollbar.set)

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
            # Formatear los datos de la matriz para mostrarlos correctamente
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
        ttk.Button(self.matrix_frame, text=button_text, command=command).grid(
            row=rows+3, column=0, columnspan=cols+1, pady=10)

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
        datos = []
        try:
            for i in range(rows):
                fila = []
                for j in range(cols):
                    valor = entries[i][j].get()
                    fila.append(float(valor))
                datos.append(fila)

            # Validar si hubo cambios
            original = self.original_matrix_data_for_modification
            if original['filas'] == rows and original['columnas'] == cols and original['datos'] == datos:
                # No hay cambios, no hacer nada
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
            self.rows_var.set("0")
            self.cols_var.set("0")
            for widget in self.matrix_frame.winfo_children():
                widget.destroy()
                
        except ValueError:
            messagebox.showerror("Error", "Asegúrate de ingresar solo números válidos en todas las celdas.")
    
    def show_result(self, text):
        self.result_text.delete(1.0, tk.END)
        self.steps_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixCRUDApp(root)
    root.mainloop()