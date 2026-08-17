import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.title("Forzy")
        st.caption("Digital Twin · Motores")
        st.markdown("---")

        # ── Sprint 3: painel de alertas (home) ──────────────────────────
        if st.button("Painel de Alertas", use_container_width=True, type="primary"):
            st.session_state.page = "alertas"

        if st.button("Equipamentos", use_container_width=True):
            st.session_state.page = "lista"

        if st.button("Novo Equipamento", use_container_width=True):
            st.session_state.tag_selecionada = None
            st.session_state.modo_cadastro = "novo"
            st.session_state.page = "cadastro"

        # ── Sprint 2: dashboard operacional ─────────────────────────────
        if st.button("Dashboard Operacional", use_container_width=True):
            st.session_state.page = "dashboard"

        st.markdown("---")
        st.caption("Sprint 3 — Inteligencia Operacional")
