from crud import crear_matriz, listar_matrices, ver_matriz, actualizar_matriz, eliminar_matriz, resolver_matriz

def mostrar_menu():
    print("\n--- MENÚ CRUD DE MATRICES ---")
    print("1. Crear una nueva matriz")
    print("2. Listar todas las matrices")
    print("3. Ver una matriz específica")
    print("4. Actualizar una matriz")
    print("5. Eliminar una matriz")
    print("6. Resolver una matriz (Gauss-Jordan)")
    print("7. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción (1-7): ").strip()

        if opcion == '1':
            nombre = input("Nombre de la matriz: ")
            try:
                filas = int(input("Número de filas: "))
                columnas = int(input("Número de columnas: "))
            except ValueError:
                print("Error: Filas y columnas deben ser números enteros.")
                continue

            print("Introduce los datos fila por fila (separados por espacios).")
            print("Ejemplo para una fila de 3 elementos: 2 3 -1")
            datos = []
            for i in range(filas):
                while True:
                    fila_input = input(f"Fila {i+1}: ").split()
                    try:
                        fila_datos = [float(valor) for valor in fila_input]
                        if len(fila_datos) != columnas:
                            print(f"Error: Debes ingresar exactamente {columnas} valores.")
                            continue
                        datos.append(fila_datos)
                        break
                    except ValueError:
                        print("Error: Asegúrate de ingresar solo números separados por espacios.")

            crear_matriz(nombre, filas, columnas, datos)

        elif opcion == '2':
            listar_matrices()

        elif opcion == '3':
            nombre = input("Nombre de la matriz a ver: ")
            ver_matriz(nombre)

        elif opcion == '4':
            print("Función de actualizar no implementada aún.")

        elif opcion == '5':
            nombre = input("Nombre de la matriz a eliminar: ")
            eliminar_matriz(nombre)

        elif opcion == '6':
            nombre = input("Nombre de la matriz a resolver: ")
            resolver_matriz(nombre)

        elif opcion == '7':
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida. Por favor, elige un número del 1 al 7.")

if __name__ == "__main__":
    main()