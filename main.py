import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from crud import crear_matriz, listar_matrices, ver_matriz, actualizar_matriz, eliminar_matriz
import persistencia
import matrices

class MatrixCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema CRUD de Matrices")
        self.root.geometry("800x600")
        
        # Crear un frame principal con scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear un canvas y scrollbar
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar el evento de scroll con el ratón
        self.scrollable_frame.bind("<Enter>", self._bound_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbound_to_mousewheel)
        
        # Estilo
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        
        self.create_widgets()
        self.update_matrix_list()
        
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def create_widgets(self):
        # Frame principal
        main_frame = self.scrollable_frame
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema CRUD de Matrices", style='Header.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Lista de matrices
        ttk.Label(main_frame, text="Matrices almacenadas:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Frame para lista y botones de acción
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox con scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.matrix_listbox = tk.Listbox(listbox_frame, height=8, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.matrix_listbox.yview)
        self.matrix_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.matrix_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Botones de acción
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(button_frame, text="Ver", command=self.view_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_matrix).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Resolver", command=self.solve_matrix).pack(side=tk.LEFT, padx=5)

        # Método de resolución
        method_frame = ttk.Frame(main_frame)
        method_frame.grid(row=2, column=2, sticky=tk.W, padx=10)
        ttk.Label(method_frame, text="Método:").pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="Gauss-Jordan")
        self.method_combobox = ttk.Combobox(method_frame, textvariable=self.method_var, values=["Gauss-Jordan", "Gauss"], state="readonly", width=12)
        self.method_combobox.pack(side=tk.LEFT, padx=5)

        # Crear nueva matriz
        ttk.Label(main_frame, text="Crear nueva matriz:", style='Header.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        create_frame = ttk.Frame(main_frame)
        create_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(create_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.name_entry = ttk.Entry(create_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(create_frame, text="Filas:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.rows_var = tk.StringVar(value="0")
        self.rows_spinbox = tk.Spinbox(create_frame, from_=1, to=20, width=5, textvariable=self.rows_var)
        self.rows_spinbox.grid(row=0, column=3, padx=5)
        
        ttk.Label(create_frame, text="Columnas:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.cols_var = tk.StringVar(value="0")
        self.cols_spinbox = tk.Spinbox(create_frame, from_=1, to=20, width=5, textvariable=self.cols_var)
        self.cols_spinbox.grid(row=0, column=5, padx=5)
        
        ttk.Button(create_frame, text="Crear", command=self.create_matrix).grid(row=0, column=6, padx=10)
        
        # Área de matriz
        ttk.Label(main_frame, text="Datos de la matriz:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.matrix_frame = ttk.Frame(main_frame)
        self.matrix_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Área de resultados
        ttk.Label(main_frame, text="Resultados:").grid(row=7, column=0, sticky=tk.W, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(main_frame, height=10, width=70, font=('Consolas', 10))
        self.result_text.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
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
            matrix_str = ""
            for fila in matrix_data['datos']:
                matrix_str += "  ".join(f"{x:.2f}" if isinstance(x, float) else str(x) for x in fila) + "\n"
            
            self.show_result(f"Matriz: {matrix_data['nombre']}\n"
                            f"Dimensiones: {matrix_data['filas']}x{matrix_data['columnas']}\n"
                            f"Datos:\n{matrix_str}")
        else:
            messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")
    
    def delete_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
            return
            
        matrix_name = self.matrix_listbox.get(selection[0])
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar la matriz '{matrix_name}'?"):
            # Llamar directamente a la función de persistencia para evitar problemas
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
    
    def solve_matrix(self):
        selection = self.matrix_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selección requerida", "Por favor selecciona una matriz de la lista.")
            return
        matrix_name = self.matrix_listbox.get(selection[0])
        try:
            matriz_data = persistencia.cargar_matriz(matrix_name)
            if matriz_data is None:
                messagebox.showerror("Error", f"No se encontró la matriz '{matrix_name}'.")
                return
            matriz_obj = matrices.Matriz(matriz_data['datos'])
            metodo = self.method_var.get()
            if metodo == "Gauss-Jordan":
                resultado = matriz_obj.gauss_jordan()
            else:
                resultado = matriz_obj.gauss()
            # Mostrar la solución y el procedimiento
            texto = f"Solución del sistema para la matriz '{matrix_name}' usando {metodo}:\n"
            if resultado["solucion"] == "Sin solución" or resultado["solucion"] == "Sistema incompatible, no tiene solución.":
                texto += "El sistema no tiene solución.\n"
            else:
                for variable, valor in resultado["solucion"].items():
                    texto += f"{variable} = {valor}\n"
            texto += "\nProcedimiento paso a paso:\n"
            for paso in resultado["pasos"]:
                texto += f"- {paso['descripcion']}\n"
                for fila in paso['matriz']:
                    texto += "  " + "  ".join(str(x) for x in fila) + "\n"
                texto += "\n"
            self.show_result(texto)
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
        
        # Crear la interfaz para ingresar los datos de la matriz
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
        self.result_text.insert(tk.END, text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatrixCRUDApp(root)
    root.mainloop()