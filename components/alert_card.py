"""
Sprint 3 — Componente reutilizavel: Card de Alerta.

Renderiza um alerta operacional completo: identificacao do motor, badge de
estado, resumo textual do NLP e (opcionalmente) botao de navegacao para o
dashboard do equipamento.

Recebe um objeto Alert (contrato definido em providers/alert_provider.py) e
nao acessa regras nem NLP diretamente — apenas exibe.
"""

import streamlit as st

from components import state_badge
from components.recommendation_card import render as render_recomendacao


# Borda lateral por estado (reforco visual da urgencia)
_BORDA = {
    "critico":    "#F85149",
    "atencao":    "#D29922",
    "saudavel":   "#3FB950",
    "manutencao": "#8B949E",
}


def css() -> str:
    return """
    <style>
      .alert-card {
        border-left: 4px solid var(--borda);
        background: rgba(255,255,255,0.02);
        border-radius: 6px; padding: 14px 16px; margin-bottom: 6px;
      }
      .alert-head { font-size: 15px; font-weight: 700; margin-bottom: 2px; }
      .alert-sub  { font-size: 12px; color:#8B949E; margin-bottom: 8px; }
      .alert-body { font-size: 13px; line-height: 1.5; }
      .nlp-flag {
        display:inline-block; font-size:9px; letter-spacing:1px;
        text-transform:uppercase; color:#8B949E; border:1px solid #30363D;
        border-radius:4px; padding:1px 6px; margin-left:8px;
      }
    </style>
    """


def render(alerta: dict, mostrar_acao: bool = True, key: str | None = None):
    """
    Renderiza um card de alerta.

    Args:
        alerta:       objeto Alert do alert_provider.
        mostrar_acao: se True, exibe botao "Abrir no Dashboard".
        key:          chave unica para o botao (necessaria em loops).
    """
    estado = alerta.get("estado", "saudavel")
    borda  = _BORDA.get(estado, "#8B949E")

    flag_html = ""
    if alerta.get("origem_texto") == "template":
        flag_html = '<span class="nlp-flag">NLP · simulado</span>'

    with st.container():
        st.markdown(
            f"""
            <div class="alert-card" style="--borda:{borda}">
              <div class="alert-head">
                {alerta.get('equipamento_id','—')} · {alerta.get('titulo','—')}
                {state_badge.badge_html(estado)}
              </div>
              <div class="alert-sub">
                {alerta.get('modelo','—')} — {alerta.get('local','—')}
                &nbsp;|&nbsp; {alerta.get('timestamp','')}
              </div>
              <div class="alert-body">
                {alerta.get('resumo_nlp','')}{flag_html}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Apoio a decisao (card de recomendacao), so para nao-saudaveis
        if estado in ("atencao", "critico") and alerta.get("recomendacao"):
            render_recomendacao(
                alerta["recomendacao"],
                prazo=alerta.get("prazo", ""),
                estado=estado,
            )

        # Acao de navegacao
        if mostrar_acao and estado != "manutencao":
            if st.button(
                f"Abrir dashboard de {alerta.get('equipamento_id','')}",
                key=key or f"open_{alerta.get('equipamento_id','')}",
                use_container_width=False,
            ):
                st.session_state.tag_selecionada = alerta.get("equipamento_id")
                st.session_state.page = "dashboard"
                st.rerun()
