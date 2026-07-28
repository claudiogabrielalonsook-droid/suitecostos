import pandas as pd
from datetime import datetime

def transformar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma el dataframe para presentarlo de manera legible al usuario.
    
    Cambios realizados:
    - Elimina columnas: ObjID, ObjID_TBCustoMat
    - DataRef → Mes
    - PrecoRevenda → Precio
    - IdMoeda → Moneda
    - CodTabela → CodProducto
    - Descricao → Descripción
    - UnidadeCusto → Unidad
    """
    
    # Crear una copia para no modificar el original
    df_transformado = df.copy()
    
    # Eliminar columnas innecesarias
    columnas_a_eliminar = ['ObjID_TBCustoMat']
    df_transformado = df_transformado.drop(columns=columnas_a_eliminar, errors='ignore')
    
    # Renombrar columnas
    renombrados = {
        'DataRef': 'Mes',
        'PrecoRevenda': 'Precio',
        'IdMoeda': 'Moneda',
        'CodTabela': 'CodProducto',
        'Descricao': 'Descripción',
        'UnidadeCusto': 'Unidad'
    }
    
    df_transformado = df_transformado.rename(columns=renombrados)
    
    # Convertir DataRef a formato de mes legible (si es timestamp)
    if 'Mes' in df_transformado.columns:
        try:
            df_transformado['Mes'] = pd.to_datetime(df_transformado['Mes']).dt.strftime('%Y-%m')
        except:
            pass  # Si no se puede convertir, dejar como está
    
    return df_transformado
