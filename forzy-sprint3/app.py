import streamlit as st
from state.session import init_session
from ui.sidebar import render_sidebar
import features.lista.page as lista_page
import features.cadastro.page as cadastro_page
import features.sensores.page as sensores_page
import features.dashboard.page as dashboard_page      # Sprint 2
import features.alertas.page as alertas_page          # Sprint 3

st.set_page_config(
    page_title="Forzy · Digital Twin",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
render_sidebar()

page = st.session_state.page

if page == "alertas":               # Sprint 3 — pagina inicial
    alertas_page.render()
elif page == "lista":
    lista_page.render()
elif page == "cadastro":
    cadastro_page.render()
elif page == "sensores":
    sensores_page.render()
elif page == "dashboard":           # Sprint 2
    dashboard_page.render()
