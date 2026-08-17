"""
Sprint 2 — Dashboard Operacional de Ativos.
Integrado com os providers da Sprint 1 (equipamento_provider + sensor_provider).
"""

import streamlit as st
import pandas as pd

import providers.equipamento_provider as eq_provider
import providers.sensor_provider as sensor_provider
from features.dashboard.charts import (
    SENSORES, COR,
    time_series_multi, gauge, scatter_saude, barras_corrente,
)

# ─── Constantes visuais ─────────────────────────────────────────────────────

_STATUS_EQ = {
    "Operacional":  ("verde",   "#3FB950"),
    "Em Manutencao":("amarelo", "#D29922"),
    "Desligado":    ("preto",   "#8B949E"),
}

_COND_SENSOR = {
    "normal":     {"label": "SAUDAVEL",   "cor": "#3FB950", "icone": "verde"},
    "alerta":     {"label": "ATENCAO",    "cor": "#D29922", "icone": "amarelo"},
    "critico":    {"label": "CRITICO",    "cor": "#F85149", "icone": "vermelho"},
    "manutencao": {"label": "MANUTENCAO", "cor": "#8B949E", "icone": "cinza"},
}

_LABELS_SENSOR = {
    "temp_c":       "Temperatura (°C)",
    "vibracao_mms": "Vibracao (mm/s)",
    "corrente_a":   "Corrente (A)",
    "tensao_v":     "Tensao (V)",
    "rotacao_rpm":  "Rotacao (RPM)",
}

_LIMITES = {
    "temp_c":       {"warning": 75, "critical": 90},
    "vibracao_mms": {"warning": 4.5,"critical": 7.1},
    "corrente_a":   {"warning": 46, "critical": 51},
}


# ─── Helpers ────────────────────────────────────────────────────────────────

def _parse_local(local: str) -> tuple[str, str]:
    """'Planta A — Linha 1' → ('Planta A', 'Linha 1')"""
    partes = local.split("—")
    if len(partes) >= 2:
        return partes[0].strip(), partes[1].strip()
    return local.strip(), "Geral"


def _condicao_leitura(leitura: dict) -> str:
    """Determina condicao de saude a partir dos valores atuais do sensor."""
    if leitura["rotacao_rpm"] == 0 and leitura["corrente_a"] == 0:
        return "manutencao"
    for campo in ("temp_c", "vibracao_mms", "corrente_a"):
        lim = _LIMITES.get(campo, {})
        if leitura.get(campo, 0) >= lim.get("critical", 9999):
            return "critico"
    for campo in ("temp_c", "vibracao_mms", "corrente_a"):
        lim = _LIMITES.get(campo, {})
        if leitura.get(campo, 0) >= lim.get("warning", 9999):
            return "alerta"
    return "normal"


def _cor_kpi(campo: str, valor: float) -> str:
    lim = _LIMITES.get(campo, {})
    if valor >= lim.get("critical", 9999):
        return COR["critico"]
    if valor >= lim.get("warning", 9999):
        return COR["alerta"]
    return COR["saudavel"]


def _alertas_do_historico(df: pd.DataFrame, tag: str) -> list[dict]:
    """Extrai momentos em que o historico cruzou os limites."""
    alertas = []
    ultima = df.iloc[-1]
    for campo, lim in _LIMITES.items():
        val = ultima[campo]
        if val >= lim["critical"]:
            alertas.append({
                "sev": "CRITICO", "campo": campo,
                "msg": f"{_LABELS_SENSOR[campo]} acima do limite critico",
                "val": f"{val:.2f}", "ts": ultima["timestamp"],
            })
        elif val >= lim["warning"]:
            alertas.append({
                "sev": "ATENCAO", "campo": campo,
                "msg": f"{_LABELS_SENSOR[campo]} proximo ao limite de atencao",
                "val": f"{val:.2f}", "ts": ultima["timestamp"],
            })
    return alertas


# ─── Renderizacao da placa tecnica ──────────────────────────────────────────

def _renderizar_placa(eq: dict):
    st.markdown("**Placa Tecnica (Nameplate)**")
    rows = [
        ("Fabricante",          eq.get("fabricante", "—")),
        ("Modelo",              eq.get("modelo", "—")),
        ("Potencia",            f"{eq.get('potencia_cv','—')} cv"),
        ("Tensao Nominal",      f"{eq.get('tensao_v','—')} V"),
        ("Corrente Nominal",    f"{eq.get('corrente_nominal_a','—')} A"),
        ("Rotacao Nominal",     f"{eq.get('rotacao_rpm','—')} RPM"),
        ("Fator de Potencia",   eq.get("fator_potencia", "—")),
        ("Classe de Isolamento",eq.get("classe_isolamento", "—")),
        ("Grau de Protecao",    eq.get("ip", "—")),
        ("Peso",                f"{eq.get('peso_kg','—')} kg"),
        ("Norma",               "NBR 17094-1 / IEC 60034"),
        ("Cadastrado em",       eq.get("cadastrado_em", "—")),
    ]
    for nome, val in rows:
        c1, c2 = st.columns([2, 3])
        c1.caption(nome)
        c2.markdown(f"**{val}**")


# ─── Pagina principal ────────────────────────────────────────────────────────

def render():
    # CSS minimo — compativel com o tema padrao do Streamlit
    st.markdown("""
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
      .sec-title { font-size:10px; text-transform:uppercase; letter-spacing:1.5px;
                   color:#8B949E; border-bottom:1px solid #21262D; padding-bottom:4px; margin:18px 0 10px 0; }
    </style>
    """, unsafe_allow_html=True)

    st.title("Dashboard Operacional")

    # ── Navegacao de volta ─────────────────────────────────────────────────
    if st.button("Voltar para Equipamentos"):
        st.session_state.page = "lista"
        st.rerun()

    st.markdown("---")

    # ── Tabs: motor individual / visao geral ───────────────────────────────
    tab_motor, tab_planta = st.tabs(["Motor — Telemetria", "Visao Geral da Planta"])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1 — Dashboard do motor
    # ═══════════════════════════════════════════════════════════════════════
    with tab_motor:

        # ── Navegacao por Planta / Area / TAG ─────────────────────────────
        todos = eq_provider.listar_todos()

        # Monta hierarquia: {planta: {area: [tags]}}
        hierarquia: dict[str, dict[str, list[str]]] = {}
        for eq in todos:
            planta, area = _parse_local(eq.get("local", "Sem local"))
            hierarquia.setdefault(planta, {}).setdefault(area, []).append(eq["tag"])

        col_p, col_a, col_t, col_w = st.columns([2, 2, 2, 2])

        with col_p:
            planta_sel = st.selectbox("Planta", sorted(hierarquia.keys()), key="dash_planta")
        with col_a:
            areas_disp = sorted(hierarquia.get(planta_sel, {}).keys())
            area_sel = st.selectbox("Area / Linha", areas_disp, key="dash_area")
        with col_t:
            tags_disp = hierarquia.get(planta_sel, {}).get(area_sel, [])
            # Prioriza a tag que veio da pagina de lista
            tag_pre = st.session_state.get("tag_selecionada")
            tag_idx = tags_disp.index(tag_pre) if tag_pre in tags_disp else 0
            tag_sel = st.selectbox("TAG do Motor", tags_disp, index=tag_idx, key="dash_tag")
        with col_w:
            horas = st.select_slider("Janela", options=[6, 12, 24, 48], value=24,
                                     format_func=lambda x: f"{x}h", key="dash_horas")

        if not tag_sel:
            st.info("Nenhum motor disponivel nesta area.")
            return

        # ── Dados do motor ─────────────────────────────────────────────────
        eq        = eq_provider.buscar_por_tag(tag_sel) or {}
        historico = sensor_provider.historico_com_tendencia(tag_sel, horas=horas)
        df        = pd.DataFrame(historico)
        ultima    = historico[-1] if historico else {}
        condicao  = _condicao_leitura(ultima) if ultima else "normal"
        cond_info = _COND_SENSOR[condicao]

        # Badge de condicao
        badge_cls = {
            "normal": "badge-saudavel", "alerta": "badge-alerta",
            "critico": "badge-critico", "manutencao": "badge-manutencao",
        }.get(condicao, "badge-saudavel")

        # ── Header do motor ────────────────────────────────────────────────
        c_info, c_placa = st.columns([3, 2])

        with c_info:
            st.subheader(f"{tag_sel} — {eq.get('modelo','—')}")
            st.markdown(
                f'<span class="cond-badge {badge_cls}">{cond_info["icone"]} {cond_info["label"]}</span>',
                unsafe_allow_html=True,
            )
            st.caption(
                f"{planta_sel} › {area_sel}  |  "
                f"Status cadastro: {eq.get('status','—')}  |  "
                f"{eq.get('fabricante','—')}"
            )

        with c_placa:
            with st.expander("Ver placa tecnica", expanded=False):
                _renderizar_placa(eq)

        # ── KPIs ──────────────────────────────────────────────────────────
        st.markdown('<div class="sec-title">Leituras Atuais</div>', unsafe_allow_html=True)

        campos_kpi = ["temp_c", "vibracao_mms", "corrente_a", "tensao_v", "rotacao_rpm"]
        cols_kpi   = st.columns(5)

        for col, campo in zip(cols_kpi, campos_kpi):
            val   = ultima.get(campo, 0.0)
            info  = SENSORES[campo]
            cor   = _cor_kpi(campo, val)
            delta = None
            delta_cor = "normal"
            lim = _LIMITES.get(campo, {})
            if lim.get("critical") and val >= lim["critical"]:
                delta, delta_cor = "Critico", "inverse"
            elif lim.get("warning") and val >= lim["warning"]:
                delta, delta_cor = "Atencao", "inverse"
            col.metric(
                label=f"{info['label']} ({info['unit']})",
                value=f"{val:.1f}" if campo != "rotacao_rpm" else f"{val:.0f}",
                delta=delta,
                delta_color=delta_cor,
            )

        # ── Gauges ────────────────────────────────────────────────────────
        st.markdown('<div class="sec-title">Indicadores de Saude</div>', unsafe_allow_html=True)
        cols_g = st.columns(5)
        for col, campo in zip(cols_g, campos_kpi):
            with col:
                fig = gauge(float(ultima.get(campo, 0)), campo, height=190)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # ── Series temporais ──────────────────────────────────────────────
        st.markdown('<div class="sec-title">Historico de Telemetria</div>', unsafe_allow_html=True)

        opcoes = {v: k for k, v in _LABELS_SENSOR.items()}
        sel_labels = st.multiselect(
            "Sensores",
            options=list(_LABELS_SENSOR.values()),
            default=["Temperatura (°C)", "Vibracao (mm/s)", "Corrente (A)"],
            key="dash_sensores",
            label_visibility="collapsed",
        )
        campos_sel = [opcoes[l] for l in sel_labels if l in opcoes]

        if campos_sel and not df.empty:
            altura = max(300, 160 * len(campos_sel))
            fig = time_series_multi(df, campos_sel, height=altura)
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False, "responsive": True})
        elif not campos_sel:
            st.info("Selecione ao menos um sensor.")

        # ── Alertas ───────────────────────────────────────────────────────
        st.markdown('<div class="sec-title">Registro de Alertas</div>', unsafe_allow_html=True)
        alertas = _alertas_do_historico(df, tag_sel) if not df.empty else []

        if not alertas:
            st.success("Sem alertas ativos — motor operando dentro dos limites.")
        else:
            for a in alertas:
                cor_a   = COR["critico"] if a["sev"] == "CRITICO" else COR["alerta"]
                icone_a = "vermelho" if a["sev"] == "CRITICO" else "amarelo"
                st.markdown(
                    f"**{icone_a} [{a['sev']}]** {a['msg']} — "
                    f"Valor: **{a['val']} {SENSORES[a['campo']]['unit']}** "
                    f"| {a['ts']}",
                )

        # ── Exportar CSV ──────────────────────────────────────────────────
        with st.expander("Dados brutos / Exportar CSV"):
            if not df.empty:
                st.dataframe(df.tail(60), use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Baixar CSV completo",
                    data=csv,
                    file_name=f"{tag_sel}_historico_{horas}h.csv",
                    mime="text/csv",
                )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2 — Visao geral da planta
    # ═══════════════════════════════════════════════════════════════════════
    with tab_planta:

        # Monta dataframe resumo de todos os motores
        rows_resumo = []
        for eq in todos:
            tag = eq["tag"]
            hist = sensor_provider.historico_com_tendencia(tag, horas=1)
            ult  = hist[-1] if hist else {}
            cond = _condicao_leitura(ult) if ult else "normal"
            planta, area = _parse_local(eq.get("local", "—"))
            rows_resumo.append({
                "tag":         tag,
                "modelo":      eq.get("modelo", "—"),
                "planta":      planta,
                "area":        area,
                "condicao":    cond,
                "temp_c":      ult.get("temp_c", 0.0),
                "vibracao_mms":ult.get("vibracao_mms", 0.0),
                "corrente_a":  ult.get("corrente_a", 0.0),
                "status_eq":   eq.get("status", "—"),
            })
        df_res = pd.DataFrame(rows_resumo)

        # ── Contadores ────────────────────────────────────────────────────
        st.markdown('<div class="sec-title">Status Geral</div>', unsafe_allow_html=True)
        n = len(df_res)
        n_ok  = len(df_res[df_res["condicao"] == "normal"])
        n_av  = len(df_res[df_res["condicao"] == "alerta"])
        n_cr  = len(df_res[df_res["condicao"] == "critico"])
        n_mn  = len(df_res[df_res["condicao"] == "manutencao"])

        cv1, cv2, cv3, cv4 = st.columns(4)
        cv1.metric("Total de Motores",  n)
        cv2.metric("Saudaveis",         n_ok,  delta=f"{n_ok}/{n}" if n else None)
        cv3.metric("Em Atencao",        n_av,  delta="verificar"   if n_av else None, delta_color="inverse" if n_av else "normal")
        cv4.metric("Criticos",          n_cr,  delta="URGENTE"     if n_cr else None, delta_color="inverse" if n_cr else "normal")

        # ── Graficos de overview ───────────────────────────────────────────
        st.markdown('<div class="sec-title">Dispersao Temperatura x Vibracao</div>', unsafe_allow_html=True)
        st.plotly_chart(scatter_saude(df_res), use_container_width=True,
                        config={"displayModeBar": False})

        st.markdown('<div class="sec-title">Carga de Corrente por Motor</div>', unsafe_allow_html=True)
        st.plotly_chart(barras_corrente(df_res), use_container_width=True,
                        config={"displayModeBar": False})

        # ── Tabela de inventario ───────────────────────────────────────────
        st.markdown('<div class="sec-title">Inventario de Ativos</div>', unsafe_allow_html=True)
        cond_label = {"normal":"Saudavel","alerta":"Atencao","critico":"Critico","manutencao":"Manutencao"}
        df_tab = df_res.copy()
        df_tab["Condicao Sensor"] = df_tab["condicao"].map(cond_label)
        df_tab = df_tab.rename(columns={
            "tag": "TAG", "modelo": "Modelo", "planta": "Planta",
            "area": "Area", "temp_c": "Temp (°C)",
            "vibracao_mms": "Vibr (mm/s)", "corrente_a": "Corr (A)",
            "status_eq": "Status Cadastro",
        })
        st.dataframe(
            df_tab[["TAG","Modelo","Planta","Area","Temp (°C)","Vibr (mm/s)","Corr (A)","Status Cadastro","Condicao Sensor"]].style.format({
                "Temp (°C)":   "{:.1f}",
                "Vibr (mm/s)": "{:.2f}",
                "Corr (A)":    "{:.1f}",
            }),
            use_container_width=True,
            hide_index=True,
            height=300,
        )
