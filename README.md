Enrique - (crud.py, main.py)

Alicia - (matrices.py)

Stephany - (Persistencia.py)

Funcionalidades
Crear, listar, ver, actualizar y eliminar matrices

Resolver sistemas de ecuaciones lineales usando el método de Gauss-Jordan

Almacenamiento persistente en archivo JSON

Estructura del Proyecto

CrudM
├── main.py              # Interfaz de usuario y menú principal
├── crud.py              # Orquestación entre interfaz, operaciones y almacenamiento
├── matrices.py          # Implementación del algoritmo de Gauss-Jordan
├── Persistencia.py      # Gestión de persistencia en archivo JSON
└── matriz.json          # Archivo de datos (se crea automáticamente)

Flujo de Datos entre Módulos
main.py → crud.py: El menú principal llama a funciones del CRUD según la opción seleccionada

crud.py → Persistencia.py: Las operaciones CRUD utilizan las funciones de persistencia para guardar/cargar datos

crud.py → matrices.py: Para resolver matrices, se llama al algoritmo de Gauss-Jordan

Persistencia.py → matriz.json: Todas las matrices se guardan en formato JSON

Dependencias entre Archivos
main.py depende de crud.py

crud.py depende de Persistencia.py y matrices.py

Persistencia.py y matrices.py son módulos independientes

Funciones Principales por Módulo
main.py (Enrique)
mostrar_menu(): Muestra las opciones disponibles en consola

main(): Función principal con loop del programa y gestión de entradas

crud.py (Enrique)
crear_matriz(): Recibe datos de usuario y guarda nueva matriz

listar_matrices(): Muestra nombres de todas las matrices almacenadas

ver_matriz(): Muestra detalles de una matriz específica

actualizar_matriz(): Modifica una matriz existente

eliminar_matriz(): Elimina una matriz del sistema

resolver_matriz(): Coordina la resolución de matrices con Gauss-Jordan

Persistencia.py (Stephany)
cargar_todas_matrices(): Lee y devuelve todas las matrices desde JSON

guardar_matriz(): Guarda o actualiza una matriz en el archivo JSON

cargar_matriz(): Busca y devuelve una matriz específica por nombre

eliminar_matriz(): Elimina una matriz del archivo JSON

matrices.py (Alicia)
resolver_gauss_jordan(): Implementa el algoritmo de Gauss-Jordan

es_matriz_valida(): Valida la estructura de una matriz

es_matriz_aumentada_valida(): Verifica si es una matriz aumentada válida

intercambiar_filas(): Intercambia filas durante el proceso de solución

Formato de Almacenamiento JSON
Las matrices se guardan con la siguiente estructura:

json
{
  "nombre_matriz": {
    "nombre": "Ejemplo 2x2",
    "filas": 2,
    "columnas": 2,
    "datos": [[1, 2], [3, 4]]
  }
}