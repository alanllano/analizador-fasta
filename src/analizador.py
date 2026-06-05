"""
Analizador de Secuencias FASTA

Este programa analiza archivos FASTA, calcula estadísticas de secuencias
y aplica filtros personalizados.
"""

import argparse


def parsear_argumentos():
    """
    Lee los argumentos de línea de comandos.

    Retorna un diccionario con:
    - input: ruta del archivo FASTA
    - output: ruta del archivo TSV de salida
    - min_len: longitud mínima (opcional)
    - max_len: longitud máxima (opcional)
    - min_gc: contenido GC mínimo (opcional)
    - max_gc: contenido GC máximo (opcional)
    """
    parser = argparse.ArgumentParser(
        description="Analiza un archivo FASTA y escribe estadísticas en TSV"
    )
    parser.add_argument("-i", "--input", required=True, help="Archivo FASTA de entrada")
    parser.add_argument("-o", "--output", required=True, help="Archivo TSV de salida")
    parser.add_argument(
        "--min-len", type=int, default=None, help="Longitud mínima de secuencia"
    )
    parser.add_argument(
        "--max-len", type=int, default=None, help="Longitud máxima de secuencia"
    )
    parser.add_argument(
        "--min-gc", type=float, default=None, help="Contenido GC mínimo (0-1)"
    )
    parser.add_argument(
        "--max-gc", type=float, default=None, help="Contenido GC máximo (0-1)"
    )

    args = parser.parse_args()
    return {
        "input": args.input,
        "output": args.output,
        "min_len": args.min_len,
        "max_len": args.max_len,
        "min_gc": args.min_gc,
        "max_gc": args.max_gc,
    }


def leer_fasta(ruta):
    """
    Lee un archivo FASTA y devuelve las secuencias.

    Retorna una lista de tuplas: (encabezado, secuencia)
    """
    secuencias = []
    encabezado_actual = None
    secuencia_actual = ""

    try:
        with open(ruta, "r") as archivo:
            for linea in archivo:
                linea = linea.strip()

                # Ignorar líneas vacías
                if not linea:
                    continue

                # Si es un encabezado
                if linea.startswith(">"):
                    # Guardar la secuencia anterior (si existe)
                    if encabezado_actual is not None:
                        secuencias.append((encabezado_actual, secuencia_actual))

                    # Iniciar nueva secuencia
                    encabezado_actual = linea[1:]  # Quitar el ">"
                    secuencia_actual = ""
                else:
                    # Agregar a la secuencia actual
                    secuencia_actual += linea.upper()

            # Guardar la última secuencia
            if encabezado_actual is not None:
                secuencias.append((encabezado_actual, secuencia_actual))

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta}'")
        return []

    return secuencias


def calcular_gc(secuencia):
    """
    Calcula el contenido GC de una secuencia.

    Retorna un número entre 0 y 1.
    """
    if len(secuencia) == 0:
        return 0.0

    gc_count = secuencia.count("G") + secuencia.count("C")
    return gc_count / len(secuencia)


def calcular_estadisticas(encabezado, secuencia):
    """
    Calcula longitud y contenido GC de una secuencia.

    Retorna un diccionario con:
    - encabezado
    - longitud
    - contenido_gc
    """
    return {
        "encabezado": encabezado,
        "longitud": len(secuencia),
        "contenido_gc": round(calcular_gc(secuencia), 4),
    }


def pasa_filtros(stats, args):
    """
    Determina si una secuencia cumple con los filtros.

    Retorna True si cumple, False si no.
    """
    longitud = stats["longitud"]
    gc = stats["contenido_gc"]

    # Filtro de longitud mínima
    if "min_len" in args and args["min_len"] is not None:
        if longitud < args["min_len"]:
            return False

    # Filtro de longitud máxima
    if "max_len" in args and args["max_len"] is not None:
        if longitud > args["max_len"]:
            return False

    # Filtro de GC mínimo
    if "min_gc" in args and args["min_gc"] is not None:
        if gc < args["min_gc"]:
            return False

    # Filtro de GC máximo
    if "max_gc" in args and args["max_gc"] is not None:
        if gc > args["max_gc"]:
            return False

    return True


def escribir_resultados(stats, ruta):
    """
    Escribe los resultados en un archivo TSV.

    Incluye encabezado: encabezado, longitud, contenido_gc
    """
    try:
        with open(ruta, "w") as archivo:
            archivo.write("encabezado\tlongitud\tcontenido_gc\n")
            for stat in stats:
                archivo.write(
                    f"{stat['encabezado']}\t{stat['longitud']}\t{stat['contenido_gc']}\n"
                )
    except IOError as error:
        print(f"Error al escribir el archivo '{ruta}': {error}")


def main():
    """
    Orquestador principal del programa.

    Coordina el flujo completo:
    1. Lee argumentos
    2. Lee archivo FASTA
    3. Calcula estadísticas
    4. Filtra secuencias
    5. Escribe resultados
    6. Muestra resumen
    """
    # Leer argumentos del usuario
    args = parsear_argumentos()

    # Leer archivo FASTA
    print(f"Leyendo archivo: {args['input']}")
    secuencias = leer_fasta(args["input"])

    if not secuencias:
        print("No se encontraron secuencias para procesar.")
        return

    # Calcular estadísticas para cada secuencia
    estadisticas_todas = []
    for encabezado, secuencia in secuencias:
        stats = calcular_estadisticas(encabezado, secuencia)
        estadisticas_todas.append(stats)

    # Filtrar secuencias que cumplan los criterios
    estadisticas_filtradas = []
    for stats in estadisticas_todas:
        if pasa_filtros(stats, args):
            estadisticas_filtradas.append(stats)

    # Escribir resultados en archivo TSV
    escribir_resultados(estadisticas_filtradas, args["output"])

    # Mostrar resumen
    print(f"  {len(estadisticas_todas)} secuencias encontradas")
    print(f"  {len(estadisticas_filtradas)} secuencias pasan los filtros")
    print(f"Resultados escritos en '{args['output']}'")


if __name__ == "__main__":
    main()
