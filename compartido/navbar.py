
import streamlit as st
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Obtener variables de entorno
LOCAL_HOST = os.getenv('LOCAL_HOST', 'localhost')
REMOTE_HOST = os.getenv('REMOTE_HOST', '10.1.1.34')

SUITE_PORT = os.getenv('SUITE_PORT', '8888')
COSTOS_PORT = os.getenv('COSTOS_PORT', '8889')
REPORTE_OPS_PORT = os.getenv('REPORTE_OPS_PORT', '8890')
REPORTE_EXPEDICION_PORT = os.getenv('REPORTE_EXPEDICION_PORT', '9876')

def render_navbar():pass

'''
def render_navbar():
    """Renderiza el navbar con expanders para navegación"""
    
    col1, col2, col3 = st.columns([1.5, 1, 1])
    
    # Suite button
    with col1:
        st.link_button(
            "🏠 Suite Bolsapel",
            f"http://{LOCAL_HOST}:{SUITE_PORT}",
            use_container_width=True
        )
    
    # Costos expander
    with col2:
        with st.expander("📊 Costos", expanded=False):
            st.link_button(
                "Actualización de Costos",
                f"http://{LOCAL_HOST}:{COSTOS_PORT}/",
                use_container_width=True,
                key="btn_costos_navbar"
            )
            st.link_button(
                "Reporte OPs",
                f"http://{LOCAL_HOST}:{REPORTE_OPS_PORT}/",
                use_container_width=True,
                key="btn_reporte_ops_navbar"
            )
    
    # Depósito expander
    with col3:
        with st.expander("📦 Depósito", expanded=False):
            st.link_button(
                "Reporte Expedición",
                f"http://{REMOTE_HOST}:{REPORTE_EXPEDICION_PORT}/",
                use_container_width=True,
                key="btn_expedicion_navbar"
            )
    
    st.divider()
'''