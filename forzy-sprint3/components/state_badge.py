"""
Sprint 3 — Componente reutilizavel: Badge de Estado Operacional.

Cores semanticas consistentes com a Sprint 2:
    saudavel  -> verde   (#3FB950)
    atencao   -> amarelo (#D29922)
    critico   -> vermelho(#F85149)  [pulsa]
    manutencao-> cinza   (#8B949E)
"""

import streamlit as st

# Metadados de cada estado (cor, rotulo, classe CSS)
ESTADO_INFO: dict[str, dict[str, str]] = {
    "saudavel":   {"label": "SAUDAVEL",   "cor": "#3FB950", "cls": "badge-saudavel"},
    "atencao":    {"label": "ATENCAO",    "cor": "#D29922", "cls": "badge-alerta"},
    "critico":    {"label": "CRITICO",    "cor": "#F85149", "cls": "badge-critico"},
    "manutencao": {"label": "MANUTENCAO", "cor": "#8B949E", "cls": "badge-manutencao"},
}


def css() -> str:
    """CSS compartilhado pelos badges (injetado uma vez pela pagina)."""
    return """
    <style>
      .cond-badge {
        display: inline-block; padding: 3px 12px; border-radius: 100px;
        font-size: 11px; font-weight: 700; letter-spacing: 1px;
      }
      .badge-saudavel   { background:rgba(63,185,80,0.15);  color:#3FB950; border:1px solid rgba(63,185,80,0.4);  }
      .badge-alerta     { background:rgba(210,153,34,0.15); color:#D29922; border:1px solid rgba(210,153,34,0.4); }
      .badge-critico    { background:rgba(248,81,73,0.15);  color:#F85149; border:1px solid rgba(248,81,73,0.4);
                          animation: pulso 1.5s infinite; }
      .badge-manutencao { background:rgba(139,148,158,0.15);color:#8B949E; border:1px solid rgba(139,148,158,0.4);}
      @keyframes pulso  { 0%,100%{box-shadow:0 0 0 0 rgba(248,81,73,.3)} 50%{box-shadow:0 0 0 6px rgba(248,81,73,0)} }
    </style>
    """


def badge_html(estado: str) -> str:
    """Retorna o HTML de um badge para o estado dado (para compor em markdown)."""
    info = ESTADO_INFO.get(estado, ESTADO_INFO["saudavel"])
    return f'<span class="cond-badge {info["cls"]}">{info["label"]}</span>'


def render(estado: str):
    """Renderiza o badge diretamente na pagina."""
    st.markdown(badge_html(estado), unsafe_allow_html=True)


def cor(estado: str) -> str:
    return ESTADO_INFO.get(estado, ESTADO_INFO["saudavel"])["cor"]
