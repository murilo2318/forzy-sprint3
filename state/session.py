import streamlit as st

def init_session():
    # Sprint 3: pagina inicial passa a ser o Painel de Alertas
    if "page" not in st.session_state:
        st.session_state.page = "alertas"
    if "tag_selecionada" not in st.session_state:
        st.session_state.tag_selecionada = None
    if "modo_cadastro" not in st.session_state:
        st.session_state.modo_cadastro = "novo"
