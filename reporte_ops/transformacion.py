import pandas as pd
import numpy as np
import unicodedata
from difflib import SequenceMatcher
from db import ejecutar_consulta


def transformar_df(df):

    df = df.copy()

    # ---------------------------------
    # Limpiar nombres de columnas
    # ---------------------------------

    df.columns = (
        df.columns
        .str.strip()
    )

    # ---------------------------------
    # Renombrar columnas
    # ---------------------------------

    columnas_renombrar = {
        "Qtde": "Cantidad",
        "NumOrdem": "OP",
        "NomeCliente": "Nombre Cliente",
        "Descricao": "Descripción Insumo",
        "Natureza": "Insumo",
        "CodSubConta": "Tipo Insumo",
        "TipoLancamento": "Tipo",
        "TituloOP": "Descripción OP",
        "QtdPrevista": "cantidad prevista",
        "QtdTotalProduzida": "cantidad real"
    }

    columnas_existentes_rename = {
        k: v
        for k, v in columnas_renombrar.items()
        if k in df.columns
    }

    df = df.rename(
        columns=columnas_existentes_rename
    )

    # ---------------------------------
    # Crear ValorUnitario
    # ---------------------------------

    if (
        "Valor" in df.columns
        and "Cantidad" in df.columns
    ):

        df["ValorUnitario"] = np.where(
            df["Cantidad"] != 0,
            df["Valor"] / df["Cantidad"],
            0
        )

    # ---------------------------------
    # Crear columnas previstas/reales
    # ---------------------------------

    df["Cantidad Prevista"] = np.where(
        df["Tipo"] == "P",
        df["Cantidad"],
        np.nan
    )

    df["UMP"] = np.where(
        df["Tipo"] == "P",
        df["UnidadeFisica"],
        np.nan
    )

    df["Valor Unitario Previsto"] = np.where(
        df["Tipo"] == "P",
        df["ValorUnitario"],
        np.nan
    )

    df["Valor Total Previsto"] = np.where(
        df["Tipo"] == "P",
        df["Valor"],
        np.nan
    )

    df["Cantidad Real"] = np.where(
        df["Tipo"] == "R",
        df["Cantidad"],
        np.nan
    )

    df["UMR"] = np.where(
        df["Tipo"] == "R",
        df["UnidadeFisica"],
        np.nan
    )

    df["Valor Unitario Real"] = np.where(
        df["Tipo"] == "R",
        df["ValorUnitario"],
        np.nan
    )

    df["Valor Total Real"] = np.where(
        df["Tipo"] == "R",
        df["Valor"],
        np.nan
    )

    # ---------------------------------
    # Eliminar columnas innecesarias
    # ---------------------------------

    columnas_eliminar = [
        "ConjuntoLancamento",
        "ObjID_ContasDeCusto",
        "Lote",
        "SourceID",
        "Usr_Edicao",
        "Usr_Presupuesto",
        "Usr_Tecnico",
        "TipoProduto",
        "WOStatusName",
        "Situacao",
        "Acabamentos",
        "QtdPaginas",
        "ImagensCad",
        "Embalagem",
        "QtdNoPacote",
        "User3",
        "User4",
        "FormatoFechado",
        "FormatoAberto",
        "usr_Liberacion",
        "usr_Responsable",
        "usr_FechaLib",
        "usr_observacion",
        "USR_PlanillaTecnicaP",
        "USR_ImagenPDF",
        "usr_RespLiberacion",
        "usr_FechaLiberacion",
        "DtReferencia",
        "DtRefCustos",
        "QtdFaturado",
        "ValorUnitarioFaturado",
        "ValorTotalFaturado",
        "CustoUnitarioReal",
        "Estado",
        "Cantidad",
        "ValorUnitario",
        "Valor",
        "UnidadeFisica",
        "DEBCRED",
        "DtEncerramento",
        "ValorUnitarioPrevisto",
        "ValorTotalPrevisto",
        "CustoUnitarioPrevisto",
        "CustoTotalPrevisto",
        "CustoTotalReal",
        "PercCusto1",
        "PercCusto2",
        "PercCusto3",
        "PercCusto4",
        "PercCusto5",
        "Producto"
    ]

    columnas_existentes = [
        col for col in columnas_eliminar
        if col in df.columns
    ]

    df = df.drop(
        columns=columnas_existentes
    )

    # ---------------------------------
    # Separar TituloOP
    # ELIMINADO: Ahora TituloOP se usa como
    # Descripcion sin separación
    # ---------------------------------

    # ---------------------------------
    # Separar previstos y reales
    # ---------------------------------

    df_p = df[
        df["Tipo"] == "P"
    ].copy()

    df_r = df[
        df["Tipo"] == "R"
    ].copy()

    # ---------------------------------
    # Agrupar SIN similitud
    # SOLO por:
    # OP + Tipo Insumo
    # ---------------------------------

    grupos_p = (
        df_p.groupby(
            ["OP", "Tipo Insumo"],
            dropna=False
        )
    )

    grupos_r = (
        df_r.groupby(
            ["OP", "Tipo Insumo"],
            dropna=False
        )
    )

    claves = set(
        list(grupos_p.groups.keys())
        +
        list(grupos_r.groups.keys())
    )

    # ---------------------------------
    # FUNCIÓN DE NORMALIZACIÓN
    # ---------------------------------

    def normalizar_descripcion(texto):
        """
        Normaliza una descripción para matching:
        - Mayúsculas
        - Sin acentos
        - Espacios limpios
        """
        if pd.isna(texto):
            return ""

        texto = str(texto).strip().upper()

        # Eliminar acentos
        texto_sin_acentos = ""
        for char in texto:
            try:
                nfd = unicodedata.normalize('NFD', char)
                if unicodedata.category(nfd[0]) != 'Mn':
                    texto_sin_acentos += nfd[0]
            except:
                texto_sin_acentos += char

        # Reemplazar múltiples espacios
        texto_sin_acentos = " ".join(
            texto_sin_acentos.split()
        )

        return texto_sin_acentos

    # ---------------------------------
    # ALGORITMO DE MATCHING JERÁRQUICO
    # ---------------------------------

    filas_finales = []

    for clave in claves:

        if clave in grupos_p.groups:
            previstos = (
                grupos_p
                .get_group(clave)
                .reset_index(drop=True)
            )
        else:
            previstos = pd.DataFrame()

        if clave in grupos_r.groups:
            reales = (
                grupos_r
                .get_group(clave)
                .reset_index(drop=True)
            )
        else:
            reales = pd.DataFrame()

        # ---------------------------------
        # Mantener registro de matches
        # ---------------------------------

        indices_previsto_usados = set()
        indices_real_usados = set()
        matches = []  # (idx_previsto, idx_real)

        # ---------------------------------
        # NIVEL 1: Match exacto normalizado
        # ---------------------------------

        for idx_p, row_p in previstos.iterrows():

            if idx_p in indices_previsto_usados:
                continue

            desc_p_norm = normalizar_descripcion(
                row_p.get("Descripción Insumo", "")
            )

            if not desc_p_norm:
                continue

            for idx_r, row_r in reales.iterrows():

                if idx_r in indices_real_usados:
                    continue

                desc_r_norm = normalizar_descripcion(
                    row_r.get("Descripción Insumo", "")
                )

                if desc_p_norm == desc_r_norm:
                    matches.append((idx_p, idx_r))
                    indices_previsto_usados.add(idx_p)
                    indices_real_usados.add(idx_r)
                    break

        # ---------------------------------
        # NIVEL 2: Match por similitud
        # ---------------------------------

        for idx_p, row_p in previstos.iterrows():

            if idx_p in indices_previsto_usados:
                continue

            desc_p_norm = normalizar_descripcion(
                row_p.get("Descripción Insumo", "")
            )

            if not desc_p_norm:
                continue

            mejor_coincidencia = None
            mejor_similitud = 0

            for idx_r, row_r in reales.iterrows():

                if idx_r in indices_real_usados:
                    continue

                desc_r_norm = normalizar_descripcion(
                    row_r.get("Descripción Insumo", "")
                )

                if not desc_r_norm:
                    continue

                similitud = SequenceMatcher(
                    None,
                    desc_p_norm,
                    desc_r_norm
                ).ratio()

                if (
                    similitud >= 0.85
                    and similitud > mejor_similitud
                ):
                    mejor_similitud = similitud
                    mejor_coincidencia = idx_r

            if mejor_coincidencia is not None:
                matches.append((idx_p, mejor_coincidencia))
                indices_previsto_usados.add(idx_p)
                indices_real_usados.add(mejor_coincidencia)

        # ---------------------------------
        # NIVEL 3: Fallback por posición
        # ---------------------------------

        previstos_sin_match = [
            idx for idx in previstos.index
            if idx not in indices_previsto_usados
        ]

        reales_sin_match = [
            idx for idx in reales.index
            if idx not in indices_real_usados
        ]

        cantidad_fallback = min(
            len(previstos_sin_match),
            len(reales_sin_match)
        )

        for i in range(cantidad_fallback):
            idx_p = previstos_sin_match[i]
            idx_r = reales_sin_match[i]
            matches.append((idx_p, idx_r))
            indices_previsto_usados.add(idx_p)
            indices_real_usados.add(idx_r)

        # ---------------------------------
        # NIVEL 4: Construir filas finales
        # ---------------------------------

        # Procesar matches emparejados
        for idx_p, idx_r in matches:

            row_p = previstos.loc[idx_p]
            row_r = reales.loc[idx_r]

            fila = {}

            # Copiar datos previstos
            fila["OP"] = row_p["OP"]

            fila["Nombre Cliente"] = row_p.get(
                "Nombre Cliente",
                np.nan
            )

            fila["Descripción OP"] = row_p.get(
                "Descripción OP",
                np.nan
            )

            fila["Insumo"] = row_p.get(
                "Insumo",
                np.nan
            )

            fila["Tipo Insumo"] = row_p.get(
                "Tipo Insumo",
                np.nan
            )

            fila["Descripción Prevista"] = (
                row_p["Descripción Insumo"]
            )

            fila["Cantidad Prevista"] = (
                row_p["Cantidad Prevista"]
            )

            fila["UMP"] = row_p["UMP"]

            fila["Valor Unitario Previsto"] = (
                row_p["Valor Unitario Previsto"]
            )

            fila["Valor Total Previsto"] = (
                row_p["Valor Total Previsto"]
            )

            fila["cantidad prevista"] = row_p.get(
                "cantidad prevista",
                np.nan
            )

            # Copiar datos reales
            fila["Descripción Real"] = (
                row_r["Descripción Insumo"]
            )

            fila["Cantidad Real"] = (
                row_r["Cantidad Real"]
            )

            fila["UMR"] = row_r["UMR"]

            fila["Valor Unitario Real"] = (
                row_r["Valor Unitario Real"]
            )

            fila["Valor Total Real"] = (
                row_r["Valor Total Real"]
            )

            fila["cantidad real"] = row_r.get(
                "cantidad real",
                np.nan
            )

            filas_finales.append(fila)

        # Procesar previstos sin match
        for idx_p in previstos_sin_match:

            if idx_p in indices_previsto_usados:
                continue

            row_p = previstos.loc[idx_p]

            fila = {}

            fila["OP"] = row_p["OP"]

            fila["Nombre Cliente"] = row_p.get(
                "Nombre Cliente",
                np.nan
            )

            fila["Descripción OP"] = row_p.get(
                "Descripción OP",
                np.nan
            )

            fila["Insumo"] = row_p.get(
                "Insumo",
                np.nan
            )

            fila["Tipo Insumo"] = row_p.get(
                "Tipo Insumo",
                np.nan
            )

            fila["Descripción Prevista"] = (
                row_p["Descripción Insumo"]
            )

            fila["Cantidad Prevista"] = (
                row_p["Cantidad Prevista"]
            )

            fila["UMP"] = row_p["UMP"]

            fila["Valor Unitario Previsto"] = (
                row_p["Valor Unitario Previsto"]
            )

            fila["Valor Total Previsto"] = (
                row_p["Valor Total Previsto"]
            )

            fila["cantidad prevista"] = row_p.get(
                "cantidad prevista",
                np.nan
            )

            # Sin datos reales
            fila["Descripción Real"] = np.nan
            fila["Cantidad Real"] = np.nan
            fila["UMR"] = np.nan
            fila["Valor Unitario Real"] = np.nan
            fila["Valor Total Real"] = np.nan
            fila["cantidad real"] = np.nan

            filas_finales.append(fila)

        # Procesar reales sin match
        for idx_r in reales_sin_match:

            if idx_r in indices_real_usados:
                continue

            row_r = reales.loc[idx_r]

            fila = {}

            fila["OP"] = row_r["OP"]

            fila["Nombre Cliente"] = row_r.get(
                "Nombre Cliente",
                np.nan
            )

            fila["Descripción OP"] = row_r.get(
                "Descripción OP",
                np.nan
            )

            fila["Insumo"] = row_r.get(
                "Insumo",
                np.nan
            )

            fila["Tipo Insumo"] = row_r.get(
                "Tipo Insumo",
                np.nan
            )

            # Sin datos previstos
            fila["Descripción Prevista"] = np.nan
            fila["Cantidad Prevista"] = np.nan
            fila["UMP"] = np.nan
            fila["Valor Unitario Previsto"] = np.nan
            fila["Valor Total Previsto"] = np.nan
            fila["cantidad prevista"] = np.nan

            # Copiar datos reales
            fila["Descripción Real"] = (
                row_r["Descripción Insumo"]
            )

            fila["Cantidad Real"] = (
                row_r["Cantidad Real"]
            )

            fila["UMR"] = row_r["UMR"]

            fila["Valor Unitario Real"] = (
                row_r["Valor Unitario Real"]
            )

            fila["Valor Total Real"] = (
                row_r["Valor Total Real"]
            )

            fila["cantidad real"] = row_r.get(
                "cantidad real",
                np.nan
            )

            filas_finales.append(fila)

    # ---------------------------------
    # Crear dataframe final
    # ---------------------------------

    df_final = pd.DataFrame(
        filas_finales
    )

    # ---------------------------------
    # Consolidar reales cuando
    # Descripción Prevista está vacía
    # ---------------------------------

    df_final = df_final.reset_index(drop=True)

    indices_eliminar = []

    grupos = df_final.groupby(
        ["OP", "Tipo Insumo"],
        dropna=False
    )

    for (_, _), grupo in grupos:

        grupo = grupo.reset_index()

        # Registros vacíos de previsto
        vacios = grupo[
            grupo["Descripción Prevista"].isna()
            |
            (
                grupo["Descripción Prevista"]
                .astype(str)
                .str.strip()
                == ""
            )
        ]

        for _, row_vacio in vacios.iterrows():

            desc_real = row_vacio["Descripción Real"]

            if pd.isna(desc_real):
                continue

            # Buscar coincidencias
            coincidencias = grupo[
                grupo["Descripción Real"] == desc_real
            ]

            # Debe existir otro registro
            if len(coincidencias) <= 1:
                continue

            # Priorizar el que tenga previsto
            coincidencias_con_prev = coincidencias[
                ~(
                    coincidencias["Descripción Prevista"].isna()
                    |
                    (
                        coincidencias["Descripción Prevista"]
                        .astype(str)
                        .str.strip()
                        == ""
                    )
                )
            ]

            if len(coincidencias_con_prev) == 0:
                continue

            idx_destino = (
                coincidencias_con_prev.iloc[0]["index"]
            )

            idx_origen = row_vacio["index"]

            if idx_destino == idx_origen:
                continue

            # -----------------------------
            # Sumar cantidades reales
            # -----------------------------

            cantidad_destino = (
                df_final.at[
                    idx_destino,
                    "Cantidad Real"
                ]
                if pd.notna(
                    df_final.at[
                        idx_destino,
                        "Cantidad Real"
                    ]
                )
                else 0
            )

            cantidad_origen = (
                df_final.at[
                    idx_origen,
                    "Cantidad Real"
                ]
                if pd.notna(
                    df_final.at[
                        idx_origen,
                        "Cantidad Real"
                    ]
                )
                else 0
            )

            nuevo_cantidad = (
                cantidad_destino
                + cantidad_origen
            )

            # -----------------------------
            # Sumar valor total real
            # -----------------------------

            valor_destino = (
                df_final.at[
                    idx_destino,
                    "Valor Total Real"
                ]
                if pd.notna(
                    df_final.at[
                        idx_destino,
                        "Valor Total Real"
                    ]
                )
                else 0
            )

            valor_origen = (
                df_final.at[
                    idx_origen,
                    "Valor Total Real"
                ]
                if pd.notna(
                    df_final.at[
                        idx_origen,
                        "Valor Total Real"
                    ]
                )
                else 0
            )

            nuevo_valor = (
                valor_destino
                + valor_origen
            )

            # -----------------------------
            # Recalcular unitario
            # -----------------------------

            if nuevo_cantidad != 0:

                nuevo_unitario = (
                    nuevo_valor
                    / nuevo_cantidad
                )

            else:

                nuevo_unitario = 0

            # -----------------------------
            # Actualizar destino
            # -----------------------------

            df_final.at[
                idx_destino,
                "Cantidad Real"
            ] = nuevo_cantidad

            df_final.at[
                idx_destino,
                "Valor Total Real"
            ] = nuevo_valor

            df_final.at[
                idx_destino,
                "Valor Unitario Real"
            ] = nuevo_unitario

            # -----------------------------
            # Marcar origen para eliminar
            # -----------------------------

            indices_eliminar.append(
                idx_origen
            )

    # ---------------------------------
    # Eliminar duplicados consolidados
    # ---------------------------------

    indices_eliminar = list(
        set(indices_eliminar)
    )

    df_final = df_final.drop(
        index=indices_eliminar
    )

    df_final = df_final.reset_index(
        drop=True
    )

    # ---------------------------------
    # Propagar valores por OP
    # Si una OP tiene un único valor de
    # cantidad prevista/real, propagarlo
    # a todas las filas de esa OP
    # ---------------------------------

    if "cantidad prevista" in df_final.columns:

        for op_key in df_final["OP"].unique():

            indices_op = df_final[
                df_final["OP"] == op_key
            ].index

            # Propagar cantidad prevista
            valores_prevista = df_final.loc[
                indices_op,
                "cantidad prevista"
            ]

            valores_prevista_no_nulos = valores_prevista[
                pd.notna(valores_prevista)
            ].unique()

            if len(valores_prevista_no_nulos) == 1:

                valor_unico = valores_prevista_no_nulos[0]

                df_final.loc[
                    indices_op,
                    "cantidad prevista"
                ] = valor_unico

    if "cantidad real" in df_final.columns:

        for op_key in df_final["OP"].unique():

            indices_op = df_final[
                df_final["OP"] == op_key
            ].index

            # Propagar cantidad real
            valores_real = df_final.loc[
                indices_op,
                "cantidad real"
            ]

            valores_real_no_nulos = valores_real[
                pd.notna(valores_real)
            ].unique()

            if len(valores_real_no_nulos) == 1:

                valor_unico = valores_real_no_nulos[0]

                df_final.loc[
                    indices_op,
                    "cantidad real"
                ] = valor_unico

    # ---------------------------------
    # Orden Tipo Insumo
    # ---------------------------------

    def obtener_orden_subconta(valor):

        valor = str(valor).upper()

        if "SOPORTES" in valor:
            return 0

        elif "ADHESIVOS" in valor:
            return 1

        elif "TINTAS" in valor:
            return 2

        elif "MP AUXILIARES" in valor:
            return 3

        return 4

    df_final["orden_subconta"] = (
        df_final["Tipo Insumo"]
        .apply(obtener_orden_subconta)
    )

    # ---------------------------------
    # Ordenar dataframe
    # ---------------------------------

    df_final = df_final.sort_values(
        by=[
            "OP",
            "orden_subconta",
            "Tipo Insumo"
        ],
        ascending=True
    )

    # ---------------------------------
    # Eliminar auxiliares
    # ---------------------------------

    columnas_auxiliares = [
        "orden_subconta",
        "Descripción Insumo"
    ]

    columnas_auxiliares_existentes = [
        col
        for col in columnas_auxiliares
        if col in df_final.columns
    ]

    df_final = df_final.drop(
        columns=columnas_auxiliares_existentes
    )

    # ---------------------------------
    # Orden columnas
    # ---------------------------------

    columnas_principales = [
        "OP",
        "Nombre Cliente",
        "Descripción OP",
        "Insumo",
        "Tipo Insumo",
        "cantidad prevista",
        "Descripción Prevista",
        "Cantidad Prevista",
        "UMP",
        "Valor Unitario Previsto",
        "Valor Total Previsto",
        "cantidad real",
        "Descripción Real",
        "Cantidad Real",
        "UMR",
        "Valor Unitario Real",
        "Valor Total Real"
    ]

    restantes = [
        col
        for col in df_final.columns
        if col not in columnas_principales
        and col != "Tipo"
    ]

    columnas_finales = (
        columnas_principales
        + restantes
        + ["Tipo"]
    )

    columnas_finales_existentes = [
        col
        for col in columnas_finales
        if col in df_final.columns
    ]

    df_final = df_final[
        columnas_finales_existentes
    ]



    return df_final

    
def agregar_gramatura(
    df,
    archivo_query
):

    df = df.copy()

    if "OP" not in df.columns:
        raise ValueError(
            "No existe la columna 'OP'."
        )

    if "Descripción Prevista" not in df.columns:
        raise ValueError(
            "No existe la columna 'Descripción Prevista'."
        )

    # Valor por defecto
    df["Gramatura"] = 0

    resultados = []

    # Ejecutar una consulta por cada OP
    for op in (
        df["OP"]
        .dropna()
        .astype(str)
        .unique()
    ):

        try:

            df_op = ejecutar_consulta(
                op=op,
                archivo_query=archivo_query
            )

            if not df_op.empty:
                resultados.append(df_op)

        except Exception as e:

            logging.warning(
                f"Error obteniendo gramaturas para OP {op}: {e}"
            )

    if not resultados:
        return df

    df_gramaturas = pd.concat(
        resultados,
        ignore_index=True
    )

    # Normalización
    df["__op"] = (
        df["OP"]
        .astype(str)
        .str.strip()
    )

    df["__desc"] = (
        df["Descripción Prevista"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df_gramaturas["__op"] = (
        df_gramaturas["NumOrdem"]
        .astype(str)
        .str.strip()
    )

    df_gramaturas["__desc"] = (
        df_gramaturas["DescMaterial"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Diccionario (OP, Descripción) -> Gramatura
    mapa = (
        df_gramaturas
        .drop_duplicates(["__op", "__desc"])
        .set_index(["__op", "__desc"])["Gramatura"]
        .to_dict()
    )

    df["Gramatura"] = (
        df.apply(
            lambda x: mapa.get(
                (
                    x["__op"],
                    x["__desc"]
                ),
                0
            ),
            axis=1
        )
    )

    df.drop(
        columns=[
            "__op",
            "__desc"
        ],
        inplace=True
    )

    return df