import logging
from pathlib import Path

from connection import obtener_dataframe
from transformador import transformar_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

BASE_DIR = Path(__file__).resolve().parent
QUERY_FILE = BASE_DIR / "query.txt"
OUTPUT_FILE = BASE_DIR / "resultados.xlsx"

PLACEHOLDER_VALUES = {
    "<schema>": "main",
    "<tabla>": "costos_materiales",
    "<campo_identificador>": "id_hash",
    "<campo_clave>": "tabla_hash",
    "<campo_fecha>": "fecha",
    "<campo_precio>": "precio",
    "<campo_moneda>": "moneda",
    "<campo_codigo>": "codigo_hash",
    "<campo_descripcion>": "elemento_hash",
    "<campo_unidad>": "unidad",
    "<alias_identificador>": "ObjID",
    "<alias_clave>": "ObjID_TBCustoMat",
    "<alias_fecha>": "DataRef",
    "<alias_precio>": "PrecoRevenda",
    "<alias_moneda>": "IdMoeda",
    "<alias_codigo>": "CodTabela",
    "<alias_descripcion>": "Descricao",
    "<alias_unidad>": "UnidadeCusto",
}


def render_query_template(template_text: str) -> str:
    """Reemplaza placeholders del archivo de consulta por valores de ejemplo."""
    query = template_text
    for token, value in PLACEHOLDER_VALUES.items():
        query = query.replace(token, value)
    return query


def main():
    """Ejecuta la consulta SQL desde el archivo query.txt."""
    try:
        query_template = QUERY_FILE.read_text(encoding="utf-8")
        query = render_query_template(query_template)

        logging.info("Ejecutando consulta desde %s...", QUERY_FILE)

        df = obtener_dataframe(query)
        df_transformado = transformar_dataframe(df)

        print("\n=== Resultados de la Consulta ===")
        print(df_transformado)
        print(f"\nTotal de registros: {len(df_transformado)}")

        df_transformado.to_excel(OUTPUT_FILE, index=False, sheet_name="Resultados")
        logging.info("Resultados guardados en %s", OUTPUT_FILE)

        return df_transformado

    except FileNotFoundError:
        logging.error("El archivo query.txt no fue encontrado.")
        raise
    except Exception as e:
        logging.error(f"Error al ejecutar la consulta: {str(e)}")
        raise


if __name__ == "__main__":
    main()
