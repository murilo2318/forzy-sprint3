"""
Sprint 3 — Painel de Alertas e Estados (pagina inicial).

Esta e a home da aplicacao: exibe, ANTES da selecao de equipamento, o
panorama de alertas operacionais de toda a frota. Consome exclusivamente o
alert_provider (camada desacoplada) — nao acessa rules_engine nem nlp_summary
diretamente.

Requisitos cobertos:
  - Resumos inteligentes (NLP, hoje simulado, estrutura pronta)
  - Apoio inicial a decisao (cards de recomendacao)
  - Botao de atualizar + timer opcional (auto-refresh)
  - Gestao de estado dinamica (Saudavel -> Atencao -> Critico)
  - Notificacao simulada ao atualizar
  - Historico de eventos da sessao
"""

from datetime import datetime

import streamlit as st

import providers.alert_provider as alert_provider
from components import alert_card, recommendation_card, state_badge, event_history


def _init_estado_painel():
    """Inicializa as chaves de session_state usadas so por esta pagina."""
    if "painel_eventos" not in st.session_state:
        st.session_state.painel_eventos = []       # historico de eventos da sessao
    if "painel_notif_idx" not in st.session_state:
        st.session_state.painel_notif_idx = 0       # indice ciclico de notificacao
    if "painel_auto" not in st.session_state:
        st.session_state.painel_auto = False        # timer ligado?
    if "painel_ultima_att" not in st.session_state:
        st.session_state.painel_ultima_att = None


def _disparar_atualizacao():
    """
    Simula a chegada de uma nova notificacao e registra no historico.
    Chamado pelo botao Atualizar e pelo timer.
    """
    notif = alert_provider.proxima_notificacao(st.session_state.painel_notif_idx)
    st.session_state.painel_notif_idx += 1
    st.session_state.painel_eventos.append(notif)
    st.session_state.painel_ultima_att = datetime.now().strftime("%H:%M:%S")
    return notif


def _injetar_css():
    st.markdown(state_badge.css(), unsafe_allow_html=True)
    st.markdown(alert_card.css(), unsafe_allow_html=True)
    st.markdown(recommendation_card.css(), unsafe_allow_html=True)
    st.markdown(event_history.css(), unsafe_allow_html=True)
    st.markdown("""
    <style>
      .sec-title { font-size:10px; text-transform:uppercase; letter-spacing:1.5px;
                   color:#8B949E; border-bottom:1px solid #21262D;
                   padding-bottom:4px; margin:18px 0 10px 0; }
      .painel-hero { font-size:13px; color:#8B949E; margin-bottom:4px; }
    </style>
    """, unsafe_allow_html=True)


def _render_contadores(resumo: dict):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Motores monitorados", resumo["total"])
    c2.metric("Criticos", resumo["criticos"],
              delta="URGENTE" if resumo["criticos"] else None,
              delta_color="inverse" if resumo["criticos"] else "normal")
    c3.metric("Em atencao", resumo["atencao"],
              delta="verificar" if resumo["atencao"] else None,
              delta_color="inverse" if resumo["atencao"] else "normal")
    c4.metric("Saudaveis", resumo["saudavel"])


def _corpo_painel():
    """Renderiza o conteudo do painel (separado para reuso no fragment/timer)."""
    # ── Dados vindos da camada desacoplada ─────────────────────────────────
    alertas = alert_provider.listar_alertas()
    resumo  = alert_provider.resumo_frota(alertas)

    _render_contadores(resumo)

    # ── Barra de controle: atualizar + timer + ultima atualizacao ──────────
    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.4, 3])
    with ctrl1:
        atualizar = st.button("Atualizar", use_container_width=True, type="primary")
    with ctrl2:
        st.session_state.painel_auto = st.toggle(
            "Auto (10s)", value=st.session_state.painel_auto,
            help="Atualiza o painel automaticamente a cada 10 segundos.",
        )
    with ctrl3:
        if st.session_state.painel_ultima_att:
            st.caption(f"Ultima atualizacao: {st.session_state.painel_ultima_att}")
        else:
            st.caption("Clique em Atualizar para buscar novas notificacoes.")

    # ── Disparo manual: gera notificacao simulada ──────────────────────────
    if atualizar:
        notif = _disparar_atualizacao()
        icone = {"critico": "error", "atencao": "warning"}.get(notif["estado"], "info")
        getattr(st, "toast", st.info)(
            f"[{notif['equipamento_id']}] {notif['titulo']}",
            icon="🔴" if notif["estado"] == "critico" else "🟡",
        )

    # ── Alertas ativos por estado ──────────────────────────────────────────
    criticos = [a for a in alertas if a["estado"] == "critico"]
    atencoes = [a for a in alertas if a["estado"] == "atencao"]
    normais  = [a for a in alertas if a["estado"] in ("saudavel", "manutencao")]

    if criticos:
        st.markdown('<div class="sec-title">Alertas Criticos</div>', unsafe_allow_html=True)
        for a in criticos:
            alert_card.render(a, key=f"crit_{a['equipamento_id']}")

    if atencoes:
        st.markdown('<div class="sec-title">Em Atencao</div>', unsafe_allow_html=True)
        for a in atencoes:
            alert_card.render(a, key=f"aten_{a['equipamento_id']}")

    st.markdown('<div class="sec-title">Operando dentro do baseline</div>', unsafe_allow_html=True)
    if normais:
        for a in normais:
            alert_card.render(a, mostrar_acao=(a["estado"] != "manutencao"),
                              key=f"norm_{a['equipamento_id']}")
    else:
        st.success("Nenhum motor em estado normal no momento.")

    # ── Historico de eventos da sessao ─────────────────────────────────────
    st.markdown('<div class="sec-title">Historico de Eventos (sessao)</div>', unsafe_allow_html=True)
    event_history.render(st.session_state.painel_eventos)


def render():
    _init_estado_painel()
    _injetar_css()

    st.title("Painel de Alertas e Estados")
    st.markdown(
        '<div class="painel-hero">Inteligencia operacional da frota — '
        'acompanhe desvios de comportamento antes de selecionar um equipamento.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Timer automatico (Streamlit >= 1.33 via st.fragment) ───────────────
    # Se o toggle estiver ligado, o corpo do painel roda dentro de um fragment
    # que se re-executa a cada 10s sem recarregar a pagina inteira. Caso a
    # versao do Streamlit nao suporte, cai no modo manual (botao).
    if st.session_state.painel_auto and hasattr(st, "fragment"):
        @st.fragment(run_every=10)
        def _auto():
            # A cada tick do timer, tambem dispara uma notificacao simulada.
            _disparar_atualizacao()
            _corpo_painel()
        _auto()
    else:
        _corpo_painel()
