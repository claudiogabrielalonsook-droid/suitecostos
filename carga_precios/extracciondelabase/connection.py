import logging
import os
from contextlib import contextmanager

import pandas as pd
import pyodbc
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("SQL_SERVER", "").strip()
PORT = os.getenv("SQL_PORT", "").strip()
DATABASE = os.getenv("SQL_DATABASE", "").strip()
USER = os.getenv("SQL_USER", "").strip()
PWD = os.getenv("SQL_PASSWORD", "").strip()
ODBC_DRIVER = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server").strip()


def construir_cadena_conexion() -> str:
    """Construye una cadena de conexión usando variables de entorno."""
    if not SERVER or not DATABASE:
        raise RuntimeError("Faltan variables de entorno: SQL_SERVER o SQL_DATABASE")

    server = f"{SERVER},{PORT}" if PORT else SERVER
    if USER and PWD:
        auth = f"UID={USER};PWD={PWD};"
    else:
        auth = "Trusted_Connection=yes;"

    return f"DRIVER={{{ODBC_DRIVER}}};SERVER={server};DATABASE={DATABASE};{auth}"


def obtener_conexion():
    """Devuelve una conexión pyodbc lista para usar."""
    conn_str = construir_cadena_conexion()
    logging.getLogger(__name__).info("Creando conexión a la base de datos")
    return pyodbc.connect(conn_str)


@contextmanager
def conexion_contextual():
    """Permite usar: with conexion_contextual() as conn:"""
    conn = obtener_conexion()
    try:
        yield conn
    finally:
        conn.close()


def obtener_dataframe(sql: str, chunksize: int = None):
    """Ejecuta una consulta SQL y devuelve un DataFrame o un generador si se solicita chunksize."""
    if not sql.strip():
        logging.getLogger(__name__).error("La consulta SQL no puede estar vacía.")
        raise ValueError("La consulta SQL no puede estar vacía.")

    logging.getLogger(__name__).info("Ejecutando consulta SQL en la base de datos...")
    with obtener_conexion() as conn:
        df = pd.read_sql(sql, conn, chunksize=chunksize)

    return df
