import logging
from connection import obtener_dataframe
from transformador import transformar_dataframe

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Ejecuta la consulta SQL desde el archivo query.txt"""
    try:
        # Cargar la consulta del archivo
        with open('query.txt', 'r', encoding='utf-8') as f:
            query = f.read()
        
        logging.info("Ejecutando consulta desde query.txt...")
        
        # Ejecutar la consulta
        df = obtener_dataframe(query)
        
        # Transformar el dataframe para presentarlo mejor
        df_transformado = transformar_dataframe(df)
        
        # Mostrar resultados
        print("\n=== Resultados de la Consulta ===")
        print(df_transformado)
        print(f"\nTotal de registros: {len(df_transformado)}")
        
        # Guardar en Excel
        output_file = "resultados.xlsx"
        df_transformado.to_excel(output_file, index=False, sheet_name="Resultados")
        logging.info(f"Resultados guardados en {output_file}")
        
        return df_transformado
        
    except FileNotFoundError:
        logging.error("El archivo query.txt no fue encontrado.")
        raise
    except Exception as e:
        logging.error(f"Error al ejecutar la consulta: {str(e)}")
        raise

if __name__ == "__main__":
    main()
