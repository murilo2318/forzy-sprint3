"""
Sprint 3 — Componente reutilizavel: Card de Recomendacao (apoio a decisao).

Exibe a acao sugerida para a equipe de manutencao, com destaque visual
proporcional a urgencia (critico x atencao). E o elemento de "apoio inicial
a tomada de decisao" exigido na Sprint.
"""

import streamlit as st

_ESTILO = {
    "critico": {"icone": "AÇÃO IMEDIATA", "cor": "#F85149",
                "bg": "rgba(248,81,73,0.08)"},
    "atencao": {"icone": "ACOMPANHAR",     "cor": "#D29922",
                "bg": "rgba(210,153,34,0.08)"},
}


def css() -> str:
    return """
    <style>
      .rec-card {
        border: 1px solid var(--rec-cor);
        background: var(--rec-bg);
        border-radius: 6px; padding: 10px 14px; margin: 4px 0 10px 0;
      }
      .rec-tag {
        font-size: 10px; font-weight: 700; letter-spacing: 1px;
        color: var(--rec-cor); text-transform: uppercase;
      }
      .rec-text { font-size: 13px; margin-top: 3px; }
      .rec-prazo {
        font-size: 11px; color:#8B949E; margin-top: 4px;
      }
    </style>
    """


def render(recomendacao: str, prazo: str = "", estado: str = "atencao"):
    """Renderiza um card de recomendacao de manutencao."""
    est = _ESTILO.get(estado, _ESTILO["atencao"])
    prazo_html = (
        f'<div class="rec-prazo">Prazo sugerido: {prazo}</div>' if prazo else ""
    )
    st.markdown(
        f"""
        <div class="rec-card" style="--rec-cor:{est['cor']}; --rec-bg:{est['bg']}">
          <div class="rec-tag">{est['icone']} · Recomendacao de manutencao</div>
          <div class="rec-text">{recomendacao}</div>
          {prazo_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
