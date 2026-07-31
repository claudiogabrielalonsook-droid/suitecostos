import hashlib
import os
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_ENTRADA = os.getenv("CSV_ENTRADA", str(BASE_DIR / "Resultados.csv")).strip()
SQLITE_SALIDA = os.getenv("SQLITE_SALIDA", str(BASE_DIR.parent / "costos.db")).strip()

COLUMNAS_BASE = [
    os.getenv("COL_IDENTIFICADOR", "ObjID"),
    os.getenv("COL_CLAVE", "ObjID_TBCustoMat"),
    os.getenv("COL_FECHA", "DataRef"),
    os.getenv("COL_PRECIO", "PrecoRevenda"),
    os.getenv("COL_MONEDA", "IdMoeda"),
    os.getenv("COL_CODIGO", "CodTabela"),
    os.getenv("COL_DESCRIPCION", "Descricao"),
    os.getenv("COL_UNIDAD", "UnidadeCusto"),
]


def hash_text(valor):
    \"\"\"Devuelve un valor SHA256 hexadecimal.\"\"\"
    if pd.isna(valor):
        return None
    return hashlib.sha256(str(valor).encode("utf-8")).hexdigest()


# Leer CSV usando un esquema configurable

df = pd.read_csv(
    CSV_ENTRADA,
    sep=";",
    decimal=",",
    header=None,
    names=COLUMNAS_BASE,
)

# Hashear columnas sensibles

df["id_hash"] = df[COLUMNAS_BASE[0]].apply(hash_text)
df["tabla_hash"] = df[COLUMNAS_BASE[1]].apply(hash_text)
df["codigo_hash"] = df[COLUMNAS_BASE[5]].apply(hash_text)
df["elemento_hash"] = df[COLUMNAS_BASE[6]].apply(hash_text)

# Seleccionar columnas finales

df_final = df[
    [
        "id_hash",
        "tabla_hash",
        "codigo_hash",
        "elemento_hash",
        COLUMNAS_BASE[2],
        COLUMNAS_BASE[3],
        COLUMNAS_BASE[4],
        COLUMNAS_BASE[7],
    ]
].rename(
    columns={
        COLUMNAS_BASE[2]: "fecha",
        COLUMNAS_BASE[3]: "precio",
        COLUMNAS_BASE[4]: "moneda",
        COLUMNAS_BASE[7]: "unidad",
    }
)

# Crear SQLite
conn = sqlite3.connect(SQLITE_SALIDA)
df_final.to_sql("costos_materiales", conn, if_exists="replace", index=False)
conn.close()

print("SQLite generado:", SQLITE_SALIDA)
