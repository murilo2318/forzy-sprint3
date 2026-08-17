"""
Sprint 3 — Componente reutilizavel: Historico de Eventos.

Renderiza a lista cronologica de eventos/notificacoes que foram disparados
durante a sessao (via botao Atualizar ou timer). Cada entrada segue o mesmo
padrao de cores semanticas dos demais componentes.
"""

import streamlit as st

from components import state_badge

_ICONE_LINHA = {
    "critico":    "#F85149",
    "atencao":    "#D29922",
    "saudavel":   "#3FB950",
    "manutencao": "#8B949E",
}


def css() -> str:
    return """
    <style>
      .evt-row {
        display:flex; align-items:center; gap:10px;
        padding:8px 4px; border-bottom:1px solid #21262D; font-size:13px;
      }
      .evt-dot { width:8px; height:8px; border-radius:50%; flex:none; }
      .evt-time { font-size:11px; color:#8B949E; width:64px; flex:none; }
      .evt-tag  { font-weight:700; width:72px; flex:none; }
      .evt-msg  { color:#C9D1D9; }
    </style>
    """


def render(eventos: list[dict], vazio_msg: str = "Nenhum evento registrado nesta sessao."):
    """
    Renderiza o historico de eventos.

    Args:
        eventos: lista de dicts com chaves:
                 equipamento_id, estado, titulo, timestamp.
    """
    if not eventos:
        st.caption(vazio_msg)
        return

    # Mais recentes primeiro
    for evt in reversed(eventos):
        cor = _ICONE_LINHA.get(evt.get("estado", "saudavel"), "#8B949E")
        st.markdown(
            f"""
            <div class="evt-row">
              <div class="evt-dot" style="background:{cor}"></div>
              <div class="evt-time">{evt.get('timestamp','')}</div>
              <div class="evt-tag">{evt.get('equipamento_id','—')}</div>
              <div class="evt-msg">
                {evt.get('titulo','—')}
                {state_badge.badge_html(evt.get('estado','saudavel'))}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
