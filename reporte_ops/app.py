import getpass
import logging
import os
import socket
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

# Agregar ruta para importar módulos compartidos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from compartido.navbar import render_navbar
from db import obtener_conexion
from transformacion import transformar_df, agregar_gramatura

# ==========================================
# PAGE CONFIG (DEBE SER PRIMERO)
# ==========================================

st.set_page_config(
    page_title="Reporte OPs",
    page_icon="../compartido/src/bolsapel.webp",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Renderizar navbar
render_navbar()

# ==========================================
# CONFIG LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def get_request_context():
    user_agent = "desconocida"
    username = "desconocida"
    hostname = "desconocida"
    machine_name = "desconocida"

    try:
        context = getattr(st, "context", None)
        if isinstance(context, dict):
            headers = context.get("headers") or {}
        else:
            headers = getattr(context, "headers", None) or {}

        if isinstance(headers, dict):
            user_agent = headers.get("User-Agent", user_agent)
    except Exception:
        pass

    try:
        username = getpass.getuser() or os.getenv("USERNAME") or os.getenv("USER") or username
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        machine_name = hostname
    except Exception:
        pass

    return {
        "user_agent": user_agent,
        "username": username,
        "hostname": hostname,
        "machine_name": machine_name,
    }


def agregar_log(mensaje, request_context=None):

    if "logs" not in st.session_state:
        st.session_state.logs = []

    hora = datetime.now().strftime(
        "%H:%M:%S"
    )

    if request_context is None:
        request_context = get_request_context()

    detalle = (
        f" | username={request_context['username']}"
        f" | hostname={request_context['hostname']}"
        f" | machine={request_context['machine_name']}"
    )

    st.session_state.logs.append(
        f"[{hora}] {mensaje}{detalle}"
    )


def leer_query_sql():
    """
    Lee la consulta SQL desde query.txt
    """

    ruta_query = Path("query.txt")

    if not ruta_query.exists():
        raise FileNotFoundError(
            "No existe el archivo query.txt"
        )

    with open(
        ruta_query,
        "r",
        encoding="utf-8"
    ) as archivo:

        return archivo.read()


def ejecutar_consulta_con_fechas(
    fecha_inicio,
    fecha_cierre,
    request_context=None
):
    """
    Ejecuta consulta SQL con fechas.
    """

    query_template = leer_query_sql()

    query = query_template.format(
        fecha_inicio=fecha_inicio,
        fecha_cierre=fecha_cierre
    )

    if request_context is None:
        request_context = get_request_context()

    logging.info(
        "Ejecutando consulta SQL | fecha_inicio=%s | fecha_cierre=%s | username=%s | hostname=%s | machine=%s",
        fecha_inicio,
        fecha_cierre,
        request_context["username"],
        request_context["hostname"],
        request_context["machine_name"],
    )

    with obtener_conexion() as conn:

        df = pd.read_sql(
            query,
            conn
        )

    return df


# ==========================================
# MAIN
# ==========================================

def main():
    request_context = get_request_context()

    # ==========================================
    # SESSION STATE
    # ==========================================

    if "logs" not in st.session_state:
        st.session_state.logs = []

    # ==========================================
    # HEADER
    # ==========================================

    logging.info(
        "Página de Streamlit cargada | page=%s | username=%s | hostname=%s | machine=%s | user_agent=%s",
        "Reporte OPs",
        request_context["username"],
        request_context["hostname"],
        request_context["machine_name"],
        request_context["user_agent"],
    )

    st.title(
        "📊 Reporte OPs"
    )

    # ==========================================
    # SIDEBAR
    # ==========================================

    with st.sidebar:

        st.header(
            "⚙️ Parámetros"
        )

        col1, col2 = st.columns(2)

        with col1:

            fecha_inicio = st.date_input(
                "Fecha Inicio",
                format="DD/MM/YYYY"
            )

        with col2:

            fecha_cierre = st.date_input(
                "Fecha Cierre",
                format="DD/MM/YYYY"
            )

        st.divider()

        ejecutar = st.button(
            "🔄 Ejecutar Consulta",
            use_container_width=True,
            type="primary"
        )

    # ==========================================
    # VALIDACIÓN FECHAS
    # ==========================================

    if (
        fecha_inicio and
        fecha_cierre and
        fecha_inicio > fecha_cierre
    ):

        st.error(
            "❌ La fecha inicio "
            "debe ser menor o igual."
        )

        return

    # ==========================================
    # EJECUTAR
    # ==========================================

    if ejecutar:

        st.session_state.logs = []

        if (
            not fecha_inicio or
            not fecha_cierre
        ):

            st.error(
                "❌ Seleccione ambas fechas."
            )

            return

        log_container = st.empty()

        with st.spinner(
            "⏳ Ejecutando proceso..."
        ):

            try:

                # ==========================================
                # LOGS
                # ==========================================

                agregar_log(
                    "Iniciando ejecución...",
                    request_context=request_context
                )

                agregar_log(
                    f"Fechas seleccionadas: "
                    f"{fecha_inicio} -> {fecha_cierre}",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )

                # ==========================================
                # CONSULTA SQL
                # ==========================================

                agregar_log(
                    "Ejecutando consulta SQL...",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )

                df = ejecutar_consulta_con_fechas(
                    fecha_inicio.strftime(
                        "%Y-%m-%d"
                    ),
                    fecha_cierre.strftime(
                        "%Y-%m-%d"
                    ),
                    request_context=request_context
                )

                agregar_log(
                    f"Consulta completada. "
                    f"Registros: {len(df)}",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )

                if df.empty:

                    agregar_log(
                        "Sin resultados.",
                        request_context=request_context
                    )

                    st.warning(
                        "⚠️ No se encontraron registros."
                    )

                    return

                # ==========================================
                # TRANSFORMACIÓN
                # ==========================================

                agregar_log(
                    "Transformando dataframe...",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )

                df_OPs = transformar_df(
                    df
                )

                df_OPs = agregar_gramatura(
                    df_OPs,
                    "querygramaje.txt"
                )

                agregar_log(
                    "Transformación finalizada.",
                    request_context=request_context
                )

                # ==========================================
                # PROCESAMIENTO
                # ==========================================

                agregar_log(
                    "Procesando descripciones...",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )


                agregar_log(
                    "Procesamiento finalizado.",
                    request_context=request_context
                )

                # ==========================================
                # SESSION STATE
                # ==========================================

                agregar_log(
                    "Guardando resultados...",
                    request_context=request_context
                )

                st.session_state.df_OPs = (
                    df_OPs
                )

                st.session_state.fecha_inicio = (
                    fecha_inicio
                )

                st.session_state.fecha_cierre = (
                    fecha_cierre
                )

                agregar_log(
                    "Resultados guardados.",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )

                # LIMPIAR LOG TEMPORAL
                log_container.empty()

                st.success(
                    f"✅ Consulta ejecutada correctamente. "
                    f"Registros encontrados: {len(df)}"
                )

            except Exception as e:

                agregar_log(
                    f"ERROR: {str(e)}",
                    request_context=request_context
                )

                log_container.code(
                    "\n".join(
                        st.session_state.logs
                    ),
                    language="text"
                )

                # LIMPIAR LOG TEMPORAL
                log_container.empty()

                st.error(
                    f"❌ Error: {str(e)}"
                )

                logging.error(
                    "Error en Reporte OPs | username=%s | hostname=%s | machine=%s | error=%s",
                    request_context["username"],
                    request_context["hostname"],
                    request_context["machine_name"],
                    str(e),
                    exc_info=True,
                )

                return

    # ==========================================
    # RESULTADOS
    # ==========================================

    if "df_OPs" in st.session_state:

        df_OPs = (
            st.session_state.df_OPs
        )

        fecha_inicio_sesion = (
            st.session_state.fecha_inicio
        )

        fecha_cierre_sesion = (
            st.session_state.fecha_cierre
        )

        st.divider()

        st.subheader(
            "📥 Descargar Resultados"
        )

        agregar_log(
            "Creando archivo Excel...",
            request_context=request_context
        )

        # ==========================================
        # EXCEL
        # ==========================================

        fecha_inicio_str = (
            fecha_inicio_sesion.strftime(
                "%Y%m%d"
            )
        )

        fecha_cierre_str = (
            fecha_cierre_sesion.strftime(
                "%Y%m%d"
            )
        )

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            df_OPs.to_excel(
                writer,
                sheet_name="OPs",
                index=False
            )


        excel_buffer.seek(0)

        agregar_log(
            "Excel generado correctamente.",
            request_context=request_context
        )

        # ==========================================
        # DOWNLOAD BUTTON
        # ==========================================

        st.download_button(
            label="⬇️ Descargar Excel",
            data=excel_buffer,
            file_name=(
                f"reporte_costos_"
                f"{fecha_inicio_str}_"
                f"{fecha_cierre_str}.xlsx"
            ),
            mime=(
                "application/"
                "vnd.openxmlformats-"
                "officedocument."
                "spreadsheetml.sheet"
            )
        )

        # ==========================================
        # LOGS
        # ==========================================

        st.divider()

        st.subheader(
            "🖥️ Log de ejecución"
        )

        st.code(
            "\n".join(
                st.session_state.logs
            ),
            language="text"
        )


# ==========================================
# ENTRYPOINT
# ==========================================

if __name__ == "__main__":
    main()