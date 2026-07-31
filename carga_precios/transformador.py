import pandas as pd


def transformar_dataframe(df: pd.DataFrame, renombres: dict | None = None) -> pd.DataFrame:
    """Transforma un DataFrame a un formato más amigable usando un mapeo configurable."""

    df_transformado = df.copy()

    columnas_a_eliminar = [
        col for col in ("<columna_innecesaria_1>", "<columna_innecesaria_2>")
        if col in df_transformado.columns
    ]
    if columnas_a_eliminar:
        df_transformado = df_transformado.drop(columns=columnas_a_eliminar, errors="ignore")

    renombres_base = {
        "ObjID": "ObjID",
        "ObjID_TBCustoMat": "ObjID_TBCustoMat",
        "DataRef": "Mes",
        "PrecoRevenda": "Precio",
        "IdMoeda": "Moneda",
        "CodTabela": "CodProducto",
        "Descricao": "Descripción",
        "UnidadeCusto": "Unidad",
    }
    if renombres is not None:
        renombres_base.update(renombres)

    renombrados = {
        columna: alias
        for columna, alias in renombres_base.items()
        if columna in df_transformado.columns
    }
    if renombrados:
        df_transformado = df_transformado.rename(columns=renombrados)

    if "Mes" in df_transformado.columns:
        try:
            df_transformado["Mes"] = pd.to_datetime(df_transformado["Mes"], errors="coerce").dt.strftime("%Y-%m")
        except Exception:
            pass

    return df_transformado
