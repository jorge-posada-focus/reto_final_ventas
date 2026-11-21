import os
import csv
import json
from datetime import datetime

DIR_PATH = "F:/Hangx/knowledge/IA/aprendizaje-ia/F0-base/F0.1-python-solido/retos/reto_final_ventas"

vendedores_tienda = ["Mateo","Andrés","Laura","Ana","Carlos","Sofía"]
productos_tienda = ['Impresora', 'Webcam', 'Audífonos', 'Monitor', 'Portátil', 'Memoria RAM', 'Mouse', 'Tablet', 'Teclado', 'Silla ergonómica', 'Disco SSD']

def leer_csv(archivo_ventas):
    with open(archivo_ventas,encoding="utf-8-sig") as ventas:
        csv_reader = csv.DictReader(ventas)
        ventas = list(csv_reader)

    return ventas

def errores_detectados(fuente, archivo_log):
    def es_fecha_valida(fecha,formato="%Y-%m-%d"):
        try:
            datetime.strptime(fecha,formato)
            return (True,)
        except ValueError:
            return (False,"La fecha es inválida")

    def es_vendedor_valido(vendedor,vendedores):
        if vendedor in vendedores:
            return (True,)
        else: return (False,"El vendedor no existe")

    def es_producto_valido(producto,productos):
        if producto in productos:
            return (True,)
        else: return (False,"El producto no está en el catálogo")
    
    def es_valor_valido(valor):
        if valor.isdigit():
            return (True,)
        else: return (False,"El valor no es numérico")

    errores_detectados = []

    for fila in fuente:
        columnas = {
            "fecha": es_fecha_valida(fila["fecha"]),
            "vendedor":es_vendedor_valido(fila["vendedor"],vendedores_tienda), 
            "producto":es_producto_valido(fila["producto"],productos_tienda),
            "valor":es_valor_valido(fila["valor"])}
        
        for columna,datos in columnas.items():
            match datos[0]:
                case False:
                    errores_detectados.append({"fila":fila,"columna":columna,"valor":fila[columna],"motivo":datos[1]})
                case True:
                    pass
    
    ventas_sin_errores = fuente.copy()

    for fila in errores_detectados:
        if fila["fila"] in ventas_sin_errores:
            ventas_sin_errores.remove(fila["fila"])
    
    with open(archivo_log,"w",encoding="utf-8") as errores:
        ahora = datetime.now()
        for error in errores_detectados:
            errores.write(f"[{ahora.strftime("%Y-%m-%d %H:%M:%S")}] ERROR | Fila: {fuente.index(error["fila"])+1} | Campo: {error["columna"]} | Valor: '{error["valor"]}' | Motivo: {error["motivo"]}\n")

    return ventas_sin_errores

def crear_resumen(fuente,archivo_json):
    total_ventas = len(fuente)
    total_ingresos = sum([int(fila["valor"]) for fila in fuente])
    ventas_por_mes = {}

    for fila in fuente:
        mes = fila["fecha"][:7]
        vendedor = fila["vendedor"]
        valor = int(fila["valor"])

        ventas_por_mes.setdefault(mes, {
            "total_ventas":0,
            "ingresos":0,
            "vendedores":{}
        })

        ventas_por_mes[mes]["total_ventas"] += 1
        ventas_por_mes[mes]["ingresos"] += valor

        ventas_por_mes[mes]["vendedores"].setdefault(vendedor, {"cantidad_ventas": 0, "ingresos": 0})

        ventas_por_mes[mes]["vendsedores"][vendedor]["cantidad_ventas"] += 1
        ventas_por_mes[mes]["vendedores"][vendedor]["ingresos"] += valor


    estructura = {
        "resumen":
            {
                "total_ventas":total_ventas,
                "total_ingresos":total_ingresos,
                "ventas_por_mes":ventas_por_mes
                }
            }

    with open(archivo_json,"w",encoding="utf-8") as resumen:
        json.dump(estructura,resumen,indent=4)

def main():
    ventas = leer_csv(os.path.join(DIR_PATH,"ventas.csv"))
    ventas_limpio = errores_detectados(ventas,os.path.join(DIR_PATH,"errores.log"))
    crear_resumen(ventas_limpio,os.path.join(DIR_PATH,"resumen.json"))


if __name__ == '__main__':
    main()