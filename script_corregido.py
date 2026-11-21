import csv
import json
from datetime import datetime
from pathlib import Path


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

DIRECTORIO = Path(__file__).resolve().parent

ARCHIVO_CSV = DIRECTORIO / "ventas.csv"
ARCHIVO_LOG = DIRECTORIO / "errores.log"
ARCHIVO_JSON = DIRECTORIO / "resumen.json"

VENDEDORES = {
    "Mateo", "Andrés", "Laura", "Ana", "Carlos", "Sofía"
}

PRODUCTOS = {
    "Impresora", "Webcam", "Audífonos", "Monitor", "Portátil",
    "Memoria RAM", "Mouse", "Tablet", "Teclado",
    "Silla ergonómica", "Disco SSD"
}

COLUMNAS_REQUERIDAS = {"fecha", "vendedor", "producto", "valor"}


# --------------------------------------------------
# VALIDACIÓN
# --------------------------------------------------

def validar_venta(fila):
    """
    Comprueba que una fila tenga los campos y valores esperados.

    Devuelve:
        - Una venta normalizada si es válida.
        - Una lista con los errores encontrados.
    """

    errores = []

    # Comprobamos que la fila tenga exactamente las columnas esperadas.
    if None in fila:
        errores.append(("fila", "", "La fila contiene columnas adicionales"))

    venta = {}

    # Validar fecha
    fecha = (fila.get("fecha") or "").strip()

    try:
        fecha_convertida = datetime.strptime(fecha, "%Y-%m-%d")

        # strptime puede aceptar algunas variaciones del formato.
        # Esta comprobación exige exactamente YYYY-MM-DD.
        if fecha_convertida.strftime("%Y-%m-%d") != fecha:
            raise ValueError

        venta["fecha"] = fecha

    except ValueError:
        errores.append(("fecha", fecha, "La fecha es inválida"))

    # Validar vendedor
    vendedor = (fila.get("vendedor") or "").strip()

    if vendedor not in VENDEDORES:
        errores.append(("vendedor", vendedor, "El vendedor no existe"))
    else:
        venta["vendedor"] = vendedor

    # Validar producto
    producto = (fila.get("producto") or "").strip()

    if producto not in PRODUCTOS:
        errores.append(("producto", producto, "El producto no está en el catálogo"))
    else:
        venta["producto"] = producto

    # Validar valor
    valor_original = (fila.get("valor") or "").strip()

    try:
        valor = int(valor_original)

        if valor < 0:
            raise ValueError

        venta["valor"] = valor

    except ValueError:
        errores.append(("valor", valor_original, "El valor debe ser un entero no negativo"))

    # Si existe al menos un error, descartamos toda la fila.
    if errores:
        return None, errores

    return venta, []


# --------------------------------------------------
# LECTURA DEL CSV Y REGISTRO DE ERRORES
# --------------------------------------------------

def leer_ventas_validas(archivo_csv, archivo_log):
    """
    Lee el CSV fila por fila.

    Registra las filas incorrectas en el log y entrega
    únicamente las ventas válidas mediante un generador.
    """

    with (
        open(archivo_csv, "r", encoding="utf-8-sig", newline="") as csv_file,
        open(archivo_log, "w", encoding="utf-8") as log_file
    ):
        lector = csv.DictReader(csv_file)

        # Comprobamos que el archivo tenga las columnas necesarias.
        if not lector.fieldnames:
            raise ValueError("El CSV está vacío o no contiene encabezados")

        columnas = set(lector.fieldnames)

        if not COLUMNAS_REQUERIDAS.issubset(columnas):
            faltantes = COLUMNAS_REQUERIDAS - columnas
            raise ValueError(f"Faltan columnas obligatorias: {faltantes}")

        # La cabecera ocupa la primera línea del archivo.
        for numero_fila, fila in enumerate(lector, start=2):

            venta, errores = validar_venta(fila)

            if errores:
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for campo, valor, motivo in errores:
                    log_file.write(
                        f"[{ahora}] ERROR | "
                        f"Fila: {numero_fila} | "
                        f"Campo: {campo} | "
                        f"Valor: '{valor}' | "
                        f"Motivo: {motivo}\n"
                    )

                continue

            yield venta


# --------------------------------------------------
# GENERACIÓN DEL RESUMEN
# --------------------------------------------------

def crear_resumen(ventas, archivo_json):
    """
    Agrupa las ventas por mes y vendedor.

    Calcula los totales generales y mensuales durante
    una sola pasada por las ventas válidas.
    """

    total_ventas = 0
    total_ingresos = 0

    ventas_por_mes = {}

    for venta in ventas:

        mes = venta["fecha"][:7]
        vendedor = venta["vendedor"]
        valor = venta["valor"]

        # Inicializamos el mes si todavía no existe.
        ventas_por_mes.setdefault(mes, {
            "total_ventas": 0,
            "ingresos": 0,
            "vendedores": {}
        })

        datos_mes = ventas_por_mes[mes]

        # Actualizamos los totales generales.
        total_ventas += 1
        total_ingresos += valor

        # Actualizamos los totales del mes.
        datos_mes["total_ventas"] += 1
        datos_mes["ingresos"] += valor

        # Inicializamos el vendedor dentro del mes.
        datos_mes["vendedores"].setdefault(vendedor, {
            "cantidad_ventas": 0,
            "ingresos": 0
        })

        datos_vendedor = datos_mes["vendedores"][vendedor]

        # Actualizamos los datos del vendedor.
        datos_vendedor["cantidad_ventas"] += 1
        datos_vendedor["ingresos"] += valor

    # La estructura se construye fuera del bucle.
    # Así también funciona cuando no hay ventas válidas.
    estructura = {
        "resumen": {
            "total_ventas": total_ventas,
            "total_ingresos": total_ingresos,
            "ventas_por_mes": ventas_por_mes
        }
    }

    with open(archivo_json, "w", encoding="utf-8") as json_file:
        json.dump(
            estructura,
            json_file,
            indent=4,
            ensure_ascii=False
        )


# --------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------

def main():

    ventas_validas = leer_ventas_validas(
        ARCHIVO_CSV,
        ARCHIVO_LOG
    )

    crear_resumen(
        ventas_validas,
        ARCHIVO_JSON
    )


if __name__ == "__main__":
    main()