"""
Gestión de un almacén - Simulación con estructuras de datos básicas.
Se utiliza un diccionario global donde cada clave es una estantería y su valor
es una lista de diccionarios con los productos.
"""

import json
import os

# ----------------------------------------------------------------------
# 1. Carga de datos iniciales desde archivo JSON
# ----------------------------------------------------------------------
def cargar_inventario_desde_json(ruta_archivo):
    """
    Carga el inventario inicial desde un archivo JSON.
    Devuelve un diccionario con el formato:
    { "Estantería A": [ {"nombre":..., "cantidad":..., "precio":...}, ... ], ... }
    Si el archivo no existe, devuelve un diccionario vacío.
    """
    if not os.path.exists(ruta_archivo):
        print(f"Archivo '{ruta_archivo}' no encontrado. Se iniciará con almacén vacío.")
        return {}
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print(f"Inventario cargado correctamente desde '{ruta_archivo}'.")
        return datos
    except json.JSONDecodeError:
        print("Error al decodificar el JSON. Se iniciará con almacén vacío.")
        return {}

# ----------------------------------------------------------------------
# 2. Gestión de Entrada de Productos
# ----------------------------------------------------------------------
def agregar_producto(almacen, nombre, cantidad, precio, estanteria):
    """
    Agrega un nuevo producto al almacén o incrementa la cantidad si ya existe.
    Entrada: nombre (str), cantidad (int), precio (float), estanteria (str)
    Salida: Mensaje de confirmación.
    """
    # Validaciones básicas
    if cantidad <= 0 or precio < 0:
        return "Error: La cantidad debe ser positiva y el precio no puede ser negativo."

    # Si la estantería no existe, se crea automáticamente
    if estanteria not in almacen:
        almacen[estanteria] = []
        print(f"(Se ha creado la estantería '{estanteria}')")

    # Buscar si el producto ya está en esa estantería
    for producto in almacen[estanteria]:
        if producto['nombre'].lower() == nombre.lower():
            producto['cantidad'] += cantidad
            # Si el precio es diferente, podríamos decidir actualizarlo o no.
            # Aquí se opta por mantener el precio existente.
            return (f"Producto '{nombre}' ya existía en {estanteria}. "
                    f"Se incrementó su cantidad en {cantidad}. Nueva cantidad: {producto['cantidad']}")

    # Si no existe, se añade como nuevo producto
    nuevo_producto = {
        'nombre': nombre,
        'cantidad': cantidad,
        'precio': precio
    }
    almacen[estanteria].append(nuevo_producto)
    return f"Producto '{nombre}' agregado correctamente a {estanteria}."

# ----------------------------------------------------------------------
# 3. Gestión de Salida de Productos
# ----------------------------------------------------------------------
def retirar_producto(almacen, nombre, cantidad):
    """
    Retira una cantidad específica de un producto del almacén.
    Busca en todas las estanterías y resta de la primera que tenga suficiente.
    Entrada: nombre (str), cantidad (int)
    Salida: Mensaje de éxito o error.
    """
    if cantidad <= 0:
        return "Error: La cantidad a retirar debe ser mayor que cero."

    nombre_lower = nombre.lower()
    for estanteria, productos in almacen.items():
        for producto in productos:
            if producto['nombre'].lower() == nombre_lower:
                if producto['cantidad'] >= cantidad:
                    producto['cantidad'] -= cantidad
                    # Opcional: eliminar el producto si la cantidad llega a 0
                    # if producto['cantidad'] == 0:
                    #     productos.remove(producto)
                    return (f"Se retiraron {cantidad} unidades de '{nombre}' "
                            f"de {estanteria}. Quedan {producto['cantidad']}.")
                else:
                    return (f"Error: Stock insuficiente de '{nombre}' en {estanteria}. "
                            f"Disponible: {producto['cantidad']}, solicitado: {cantidad}.")
    return f"Error: El producto '{nombre}' no se encuentra en el almacén."

# ----------------------------------------------------------------------
# 4. Verificar Disponibilidad de Productos
# ----------------------------------------------------------------------
def verificar_disponibilidad(almacen, nombre):
    """
    Busca un producto en todas las estanterías y muestra cantidad y ubicación.
    Entrada: nombre (str)
    Salida: Cadena con la información de disponibilidad.
    """
    nombre_lower = nombre.lower()
    resultados = []
    for estanteria, productos in almacen.items():
        for producto in productos:
            if producto['nombre'].lower() == nombre_lower:
                resultados.append(f"  - {estanteria}: {producto['cantidad']} unidades")

    if resultados:
        return "Disponibilidad de '{}':\n{}".format(nombre, "\n".join(resultados))
    else:
        return f"El producto '{nombre}' no se encuentra en el almacén."

# ----------------------------------------------------------------------
# 5. Verificar Estado del Almacén
# ----------------------------------------------------------------------
def estado_almacen(almacen):
    """
    Muestra un resumen del almacén: productos por estantería, total por producto,
    y valor total almacenado.
    Salida: Cadena con el estado completo.
    """
    if not almacen:
        return "El almacén está vacío."

    lineas = []
    lineas.append("=" * 60)
    lineas.append("ESTADO DEL ALMACÉN")
    lineas.append("=" * 60)

    total_general_valor = 0.0
    total_productos_dict = {}  # nombre -> cantidad total

    for estanteria, productos in almacen.items():
        lineas.append(f"\n{estanteria}:")
        if not productos:
            lineas.append("  (vacía)")
            continue

        valor_estanteria = 0.0
        for prod in productos:
            nombre = prod['nombre']
            cantidad = prod['cantidad']
            precio = prod['precio']
            valor = cantidad * precio
            valor_estanteria += valor
            total_general_valor += valor

            # Acumular total por producto
            total_productos_dict[nombre] = total_productos_dict.get(nombre, 0) + cantidad

            lineas.append(f"  - {nombre}: {cantidad} uds, precio: {precio:.2f} €, valor: {valor:.2f} €")
        lineas.append(f"  Valor total de la estantería: {valor_estanteria:.2f} €")

    lineas.append("\n" + "-" * 40)
    lineas.append("TOTALES POR PRODUCTO (todo el almacén):")
    for nombre, total_cant in sorted(total_productos_dict.items()):
        lineas.append(f"  {nombre}: {total_cant} unidades")

    lineas.append("\n" + "=" * 40)
    lineas.append(f"VALOR TOTAL ALMACENADO: {total_general_valor:.2f} €")
    lineas.append("=" * 60)

    return "\n".join(lineas)

# ----------------------------------------------------------------------
# 6. Transferencia de Productos entre Estanterías
# ----------------------------------------------------------------------
def transferir_producto(almacen, nombre, cantidad, est_origen, est_destino):
    """
    Transfiere una cantidad de producto desde una estantería origen a una destino.
    Entrada: nombre (str), cantidad (int), est_origen (str), est_destino (str)
    Salida: Mensaje con el resultado.
    """
    if cantidad <= 0:
        return "Error: La cantidad a transferir debe ser positiva."

    if est_origen not in almacen:
        return f"Error: La estantería origen '{est_origen}' no existe."
    if est_destino not in almacen:
        # Se crea la estantería destino si no existe
        almacen[est_destino] = []

    nombre_lower = nombre.lower()
    # Buscar el producto en la estantería origen
    for producto in almacen[est_origen]:
        if producto['nombre'].lower() == nombre_lower:
            if producto['cantidad'] < cantidad:
                return (f"Error: Cantidad insuficiente en {est_origen}. "
                        f"Disponible: {producto['cantidad']}, solicitado: {cantidad}.")
            # Reducir en origen
            producto['cantidad'] -= cantidad
            precio = producto['precio']  # Se mantiene el mismo precio

            # Añadir en destino (si ya existe, sumar; si no, crear)
            for prod_dest in almacen[est_destino]:
                if prod_dest['nombre'].lower() == nombre_lower:
                    prod_dest['cantidad'] += cantidad
                    break
            else:
                almacen[est_destino].append({
                    'nombre': nombre,
                    'cantidad': cantidad,
                    'precio': precio
                })

            # Si la cantidad en origen queda en 0, podríamos eliminar el producto
            # if producto['cantidad'] == 0:
            #     almacen[est_origen].remove(producto)

            return (f"Transferencia exitosa: {cantidad} unidades de '{nombre}' "
                    f"movidas de {est_origen} a {est_destino}.")
    return f"Error: El producto '{nombre}' no se encuentra en {est_origen}."

# ----------------------------------------------------------------------
# Menú interactivo para probar el sistema
# ----------------------------------------------------------------------
def mostrar_menu():
    print("\n" + "=" * 50)
    print("GESTIÓN DE ALMACÉN - MENÚ PRINCIPAL")
    print("=" * 50)
    print("1. Agregar producto")
    print("2. Retirar producto")
    print("3. Verificar disponibilidad de un producto")
    print("4. Mostrar estado completo del almacén")
    print("5. Transferir producto entre estanterías")
    print("6. Salir")
    print("=" * 50)

def ejecutar_menu(almacen):
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()
        if opcion == "1":
            nombre = input("Nombre del producto: ").strip()
            try:
                cantidad = int(input("Cantidad: "))
                precio = float(input("Precio unitario: "))
            except ValueError:
                print("Error: Cantidad y precio deben ser números válidos.")
                continue
            estanteria = input("Estantería (ej. Estantería A): ").strip()
            print(agregar_producto(almacen, nombre, cantidad, precio, estanteria))

        elif opcion == "2":
            nombre = input("Nombre del producto a retirar: ").strip()
            try:
                cantidad = int(input("Cantidad a retirar: "))
            except ValueError:
                print("Error: La cantidad debe ser un número entero.")
                continue
            print(retirar_producto(almacen, nombre, cantidad))

        elif opcion == "3":
            nombre = input("Nombre del producto a buscar: ").strip()
            print(verificar_disponibilidad(almacen, nombre))

        elif opcion == "4":
            print(estado_almacen(almacen))

        elif opcion == "5":
            nombre = input("Nombre del producto a transferir: ").strip()
            try:
                cantidad = int(input("Cantidad a transferir: "))
            except ValueError:
                print("Error: Cantidad inválida.")
                continue
            origen = input("Estantería origen: ").strip()
            destino = input("Estantería destino: ").strip()
            print(transferir_producto(almacen, nombre, cantidad, origen, destino))

        elif opcion == "6":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

# ----------------------------------------------------------------------
# Punto de entrada principal
# ----------------------------------------------------------------------
if __name__ == "__main__":
    ARCHIVO_JSON = "productos_almacen_volumen.json"
    almacen = cargar_inventario_desde_json(ARCHIVO_JSON)

    # Si se desea ejecutar de forma automática sin menú,
    # se pueden llamar las funciones directamente aquí.
    # Por defecto se lanza el menú interactivo.
    ejecutar_menu(almacen)