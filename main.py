import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from crud import crear_matriz, listar_matrices, ver_matriz, actualizar_matriz, eliminar_matriz
import persistencia
import matrices

class MatrixCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Matrices - Modo Oscuro")
        self.root.geometry("900x700")
        self.root.configure(bg="#23272e")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background="#23272e")
        style.configure('Dark.TLabel', background="#23272e", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('Dark.TButton', background="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11), borderwidth=0)
        style.map('Dark.TButton', background=[('active', '#00adb5')])
        style.configure('Title.TLabel', background="#23272e", foreground="#00adb5", font=('Segoe UI', 18, 'bold'))
        style.configure('Result.TLabel', background="#23272e", foreground="#e0e0e0", font=('Consolas', 13))
        style.configure('Entry.TEntry', fieldbackground="#393e46", foreground="#e0e0e0", font=('Segoe UI', 11))
        style.configure('TCombobox', fieldbackground="#393e46", background="#393e46", foreground="#e0e0e0")

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
        main_frame = self.scrollable_frame

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
        ttk.Button(action_frame, text="Eliminar", command=self.delete_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Resolver", command=self.solve_matrix, style='Dark.TButton').pack(side=tk.LEFT, padx=5)

        # Área para ingresar datos de la matriz
        ttk.Label(main_frame, text="Datos de la matriz:", style='Dark.TLabel').grid(row=6, column=0, columnspan=4, sticky="w", pady=(10,5))
        self.matrix_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        self.matrix_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(0,10))

        # Área de resultados (solución y pasos)
        result_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        result_frame.grid(row=8, column=0, columnspan=4, sticky="nsew", pady=(10,0))
        ttk.Label(result_frame, text="Solución", style='Title.TLabel').pack(anchor="w", pady=(0,5))
        self.result_text = tk.Text(result_frame, height=8, width=80, font=('Segoe UI', 13), bg="#23272e", fg="#00adb5", bd=0, highlightthickness=0)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        ttk.Label(result_frame, text="Pasos de solución", style='Title.TLabel').pack(anchor="w", pady=(0,5))
        self.steps_text = tk.Text(result_frame, height=16, width=80, font=('Consolas', 12), bg="#23272e", fg="#e0e0e0", bd=0, highlightthickness=0)
        self.steps_text.pack(fill=tk.BOTH, expand=True)

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
                line += "|"
            
            formatted_str += line + "\n"
            
        return formatted_str

    def update_matrix_list(self):
        self.matrix_listbox.delete(0, tk.END)
        matrices_data = persistencia.cargar_todas_matrices()
        if matrices_data:
            for name in matrices_data.keys():
                self.matrix_listbox.insert(tk.END, name)
    
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
        metodo = getattr(self, 'selected_method', self.method_var.get())
        if not matrix_name:
            selection = self.matrix_listbox.curselection()
            if selection:
                matrix_name = self.matrix_listbox.get(selection[0])
            else:
                messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
                return
        if not metodo:
            metodo = self.method_var.get()
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
                self.result_text.insert(tk.END, "El sistema no tiene solución.\n")
            else:
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
    
    def create_matrix(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Nombre requerido", "Por favor ingresa un nombre para la matriz.")
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
    
    def create_matrix_input_ui(self, rows, cols, name):
        # Limpiar frame anterior
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        # Crear etiquetas de columna
        for j in range(cols):
            ttk.Label(self.matrix_frame, text=f"Col {j+1}").grid(row=0, column=j+1, padx=5, pady=2)
        
        # Crear entradas para la matriz
        entries = []
        for i in range(rows):
            row_entries = []
            ttk.Label(self.matrix_frame, text=f"Fila {i+1}").grid(row=i+1, column=0, padx=5, pady=2)
            for j in range(cols):
                entry = ttk.Entry(self.matrix_frame, width=8)
                entry.insert(0, "0")  # Valor por defecto
                entry.grid(row=i+1, column=j+1, padx=2, pady=2)
                row_entries.append(entry)
            entries.append(row_entries)
        
        # Botón para guardar
        ttk.Button(self.matrix_frame, text="Guardar Matriz", 
                  command=lambda: self.save_matrix_data(entries, rows, cols, name)).grid(
                  row=rows+1, column=0, columnspan=cols+1, pady=10)
    
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