import logging
import os
from pathlib import Path

import pandas as pd
import pyodbc
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("SQL_SERVER", "").strip()
PORT = os.getenv("SQL_PORT", "").strip()
DATABASE = os.getenv("SQL_DATABASE", "").strip()
USER = os.getenv("SQL_USER", "").strip()
PWD = os.getenv("SQL_PASSWORD", "").strip()

ODBC_DRIVER = os.getenv(
    "ODBC_DRIVER",
    "SQL Server Native Client 11.0"
).strip()


def construir_cadena_conexion():

    if not SERVER or not DATABASE:
        raise RuntimeError(
            "Faltan variables de entorno"
        )

    server = f"{SERVER},{PORT}" if PORT else SERVER

    if USER and PWD:
        auth = f"UID={USER};PWD={PWD};"
    else:
        auth = "Trusted_Connection=yes;"

    return (
        f"DRIVER={{{ODBC_DRIVER}}};"
        f"SERVER={server};"
        f"DATABASE={DATABASE};"
        f"{auth}"
    )


def obtener_conexion():

    conn_str = construir_cadena_conexion()

    logging.info(
        "Conectando a SQL Server..."
    )

    return pyodbc.connect(conn_str)


def leer_query(nombre_archivo="query.txt"):

    ruta_query = Path(nombre_archivo)

    if not ruta_query.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {nombre_archivo}"
        )

    with open(
        ruta_query,
        "r",
        encoding="utf-8"
    ) as archivo:

        return archivo.read()


def ejecutar_consulta(
    op,
    archivo_query="query.txt"
):

    query_template = leer_query(
        archivo_query
    )

    query = query_template.format(
        op=op
    )

    logging.info(
        f"Ejecutando consulta para OP {op} usando {archivo_query}"
    )

    with obtener_conexion() as conn:

        df = pd.read_sql(
            query,
            conn
        )

    return df