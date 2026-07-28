import streamlit as st
import sys
import os
import base64
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener variables de entorno
LOCAL_HOST = os.getenv('LOCAL_HOST', 'localhost')
REMOTE_HOST = os.getenv('REMOTE_HOST', '10.1.1.34')

COSTOS_PORT = os.getenv('COSTOS_PORT', '8889')
REPORTE_OPS_PORT = os.getenv('REPORTE_OPS_PORT', '8890')
REPORTE_EXPEDICION_PORT = os.getenv('REPORTE_EXPEDICION_PORT', '9876')

# Agregar ruta para importar módulos compartidos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Suite Bolsapel",
    layout="wide",
    page_icon="../compartido/src/bolsapel.webp"
)

# =========================================
# CSS
# =========================================

st.markdown("""
<style>

.button-container {
    text-align: center;
    margin: 20px 0;
}

.button-desc {
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)

st.title("Suite Bolsapel")

st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>Gestiona tus procesos de forma eficiente</p>", unsafe_allow_html=True)

# =========================================
# SECCIÓN COSTOS
# =========================================

st.subheader("📊 Costos", divider="gray")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.markdown(
        f'<a href="http://{LOCAL_HOST}:{COSTOS_PORT}" target="_self" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#7CB342; color:white; border:none; border-radius:6px; font-size:18px; font-weight:bold; cursor:pointer;">📊 Gestor de Costos</button></a>',
        unsafe_allow_html=True
    )
    st.markdown('<p class="button-desc">Carga y procesa archivos de precios</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.markdown(
        f'<a href="http://{LOCAL_HOST}:{REPORTE_OPS_PORT}" target="_self" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#5DADE2; color:white; border:none; border-radius:6px; font-size:18px; font-weight:bold; cursor:pointer;">📈 Reporte OPs</button></a>',
        unsafe_allow_html=True
    )
    st.markdown('<p class="button-desc">Visualiza análisis y reportes</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================
# SECCIÓN DEPÓSITO
# =========================================

st.subheader("📦 Depósito", divider="gray")

st.markdown('<div class="button-container">', unsafe_allow_html=True)
st.markdown(
    f'<a href="http://{REMOTE_HOST}:{REPORTE_EXPEDICION_PORT}" target="_self" style="text-decoration:none;"><button style="width:100%; padding:12px; background-color:#FF9800; color:white; border:none; border-radius:6px; font-size:18px; font-weight:bold; cursor:pointer;">📤 Reporte Expedición</button></a>',
    unsafe_allow_html=True
)
st.markdown('<p class="button-desc">Gestión de bobinas y despachos</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =========================================
# LOGO
# =========================================

st.divider()

try:
    logo_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "compartido/src/bolsapel.webp"
    )
    
    with open(logo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/webp;base64,{data}" width="180">
        </div>
        """,
        unsafe_allow_html=True
    )

except:
    st.markdown(
        "<p style='font-size: 0.85rem; color: #a0a0a0;'>Logo no encontrado</p>",
        unsafe_allow_html=True
    )

# =========================================
# FOOTER
# =========================================

st.markdown(
    """
    <div style='text-align: center; margin-top: 30px;'>
        <p style='font-size: 0.9rem; color: #808080;'>
            Equipo de desarrollo SISTEMAS 2026
        </p>
    </div>
    """,
    unsafe_allow_html=True
)