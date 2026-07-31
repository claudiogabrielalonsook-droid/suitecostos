import os
import sys

import pandas as pd
import streamlit as st

# Agregar ruta para importar módulos compartidos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from compartido.navbar import render_navbar
from main import main as ejecutar_consulta

IDENTIFICADOR_COL = os.getenv("IDENTIFICADOR_COL", "ObjID")

# =========================================
# CONFIGURACIÓN
# =========================================

st.set_page_config(
    page_title="Gestor de Costos y Precios",
    page_icon="../compartido/src/bolsapel.webp",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Renderizar navbar
render_navbar()

# =========================================
# CSS
# =========================================

st.markdown("""
<style>

.small-text {
    font-size: 0.85rem;
    color: #a0a0a0;
    margin: 5px 0;
}

/* Botón descarga verde */
div[data-testid="stDownloadButton"] button {
    background-color: #28a745 !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background-color: #218838 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================

st.title("💰 Gestor de Costos y Precios")

# =========================================
# SESSION STATE
# =========================================

if "estado_log" not in st.session_state:
    st.session_state.estado_log = []

if "df_anterior" not in st.session_state:
    st.session_state.df_anterior = None

if "df_cambios" not in st.session_state:
    st.session_state.df_cambios = None

if "excel_data" not in st.session_state:
    st.session_state.excel_data = None

# =========================================
# DESCARGAR DATOS
# =========================================

st.header("Descargar Datos")

col1, col2, col3 = st.columns([1, 1, 5])

with col1:

    if st.button("Descargar Excel", key="btn_descargar"):

        try:

            with st.spinner("Generando datos..."):

                st.session_state.estado_log.append(
                    "Ejecutando consulta a base de datos..."
                )

                ejecutar_consulta()

                st.session_state.estado_log.append(
                    "Datos generados exitosamente"
                )

            with open("resultados.xlsx", "rb") as file:
                st.session_state.excel_data = file.read()

        except Exception as e:

            st.session_state.estado_log.append(
                f"Error: {str(e)}"
            )

with col2:

    if st.session_state.excel_data:

        st.download_button(
            label="Descargar resultados.xlsx",
            data=st.session_state.excel_data,
            file_name="resultados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# =========================================
# CARGAR ARCHIVO
# =========================================

st.header("Cargar y Procesar Archivo")

uploaded_file = st.file_uploader(
    "Arrastra o selecciona un archivo Excel",
    type=["xlsx", "xls"],
    key="file_uploader"
)

if uploaded_file is not None:

    try:

        df_actual = pd.read_excel(uploaded_file)

        # =========================================
        # VALIDAR OBJID
        # =========================================

        if IDENTIFICADOR_COL not in df_actual.columns:

            st.error(f"El archivo no contiene la columna {IDENTIFICADOR_COL}")
            st.stop()

        st.markdown(
            f"<p class='small-text'>Archivo cargado: "
            f"{uploaded_file.name}</p>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<p class='small-text'>"
            f"Filas: {len(df_actual)} | "
            f"Columnas: {len(df_actual.columns)}"
            f"</p>",
            unsafe_allow_html=True
        )

        # =========================================
        # COMPARAR CONTRA EXCEL ANTERIOR
        # =========================================

        cambios_detectados = []

        if st.session_state.df_anterior is not None:

            df_anterior = st.session_state.df_anterior.copy()

            merge = df_actual.merge(
                df_anterior,
                on=IDENTIFICADOR_COL,
                how="inner",
                suffixes=("_nuevo", "_anterior")
            )

            columnas = []

            for c in merge.columns:

                if c.endswith("_nuevo"):

                    columnas.append(
                        c.replace("_nuevo", "")
                    )

            for _, row in merge.iterrows():

                objid = row["ObjID"]

                for columna in columnas:

                    nuevo = row[f"{columna}_nuevo"]
                    anterior = row[f"{columna}_anterior"]

                    if str(nuevo) != str(anterior):

                        cambio = {
                            IDENTIFICADOR_COL: objid,
                            "Campo": columna,
                            "Valor Anterior": anterior,
                            "Valor Nuevo": nuevo
                        }

                        cambios_detectados.append(cambio)

                        # =========================================
                        # PRINT CONSOLA
                        # =========================================

                        print("=" * 60)

                        print(f"{IDENTIFICADOR_COL}: {objid}")

                        if "ID_nuevo" in row:
                            print(f"ID Item: {row['ID_nuevo']}")

                        print(f"Campo modificado: {columna}")
                        print(f"Valor anterior: {anterior}")
                        print(f"Valor nuevo: {nuevo}")

        # =========================================
        # GUARDAR CAMBIOS
        # =========================================

        if cambios_detectados:

            st.session_state.df_cambios = pd.DataFrame(
                cambios_detectados
            )

        else:

            st.session_state.df_cambios = None

        # =========================================
        # TABS
        # =========================================

        tabs = ["Archivo Actual"]

        if st.session_state.df_cambios is not None:
            tabs.append("Cambios")

        pestañas = st.tabs(tabs)

        # =========================================
        # TAB ARCHIVO ACTUAL
        # =========================================

        with pestañas[0]:

            with st.expander(
                "Ver previa del archivo",
                expanded=True
            ):

                st.dataframe(
                    df_actual,
                    use_container_width=True
                )

        # =========================================
        # TAB CAMBIOS
        # =========================================

        if st.session_state.df_cambios is not None:

            with pestañas[1]:

                st.warning(
                    f"Se detectaron "
                    f"{len(st.session_state.df_cambios)} cambios"
                )

                with st.expander(
                    "Ver previa del archivo Cambios",
                    expanded=True
                ):

                    st.dataframe(
                        st.session_state.df_cambios,
                        use_container_width=True
                    )

        # =========================================
        # GUARDAR ACTUAL COMO ANTERIOR
        # =========================================

        st.session_state.df_anterior = df_actual.copy()

        # =========================================
        # BOTÓN PROCESAR
        # =========================================

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:

            if st.button("Procesar", key="btn_procesar"):

                st.session_state.estado_log.append(
                    "Procesando archivo..."
                )

                st.info("Procesando archivo...")

    except Exception as e:

        st.markdown(
            f"<p class='small-text' "
            f"style='color: #ff6b6b;'>"
            f"Error: {str(e)}"
            f"</p>",
            unsafe_allow_html=True
        )

else:

    st.markdown(
        "<p class='small-text'>"
        "Carga un archivo Excel para comenzar"
        "</p>",
        unsafe_allow_html=True
    )

# =========================================
# ESTADO
# =========================================

st.divider()

st.header("Estado")

estado_container = st.container(border=True)

with estado_container:

    logs = st.session_state.get("estado_log", [])

    if logs:

        for log in logs[-10:]:

            st.markdown(
                f"<p class='small-text'>✓ {log}</p>",
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            "<p class='small-text'>...</p>",
            unsafe_allow_html=True
        )