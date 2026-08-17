import streamlit as st
import pandas as pd
import pipelines.equipamento_pipeline as pipeline
import providers.equipamento_provider as eq_provider

LIMITES = {
    "temp_c":       {"aviso": 75,  "critico": 90},
    "vibracao_mms": {"aviso": 4.5, "critico": 7.1},
}


def _icone(grandeza: str, valor: float) -> str:
    limites = LIMITES.get(grandeza)
    if not limites:
        return "verde"
    if valor >= limites["critico"]:
        return "vermelho"
    if valor >= limites["aviso"]:
        return "amarelo"
    return "verde"


def render():
    st.title("Dados dos Sensores")

    if st.button("Voltar para Equipamentos"):
        st.session_state.page = "lista"
        st.rerun()

    st.markdown("---")

    tags = eq_provider.tags_disponiveis()
    tag_atual = st.session_state.get("tag_selecionada")
    tag_idx = tags.index(tag_atual) if tag_atual in tags else 0
    tag = st.selectbox("Equipamento (TAG)", tags, index=tag_idx)

    col1, col2 = st.columns(2)
    with col1:
        atualizar = st.button("Leitura Atual", type="primary", use_container_width=True)
    with col2:
        historico_btn = st.button("Historico 24h", use_container_width=True)

    st.markdown("---")

    if atualizar:
        with st.spinner("Lendo sensores..."):
            leitura = pipeline.leitura_atual(tag)

        st.subheader("Leitura em Tempo Real")
        st.caption(f"Timestamp: {leitura['timestamp']}")

        col1, col2, col3 = st.columns(3)
        temp_val = leitura["temp_c"]
        vib_val  = leitura["vibracao_mms"]

        col1.metric("Tensao (V)",      f"{leitura['tensao_v']} V")
        col2.metric("Corrente (A)",    f"{leitura['corrente_a']} A")
        col3.metric("Temperatura (°C)", f"{temp_val} °C",
                    delta="Atencao" if temp_val >= 75 else None,
                    delta_color="inverse")
        col4, col5 = st.columns(2)
        col4.metric("Vibracao (mm/s)", f"{vib_val} mm/s",
                    delta="Atencao" if vib_val >= 4.5 else None,
                    delta_color="inverse")
        col5.metric("Rotacao (RPM)",   f"{leitura['rotacao_rpm']} RPM")

    if historico_btn:
        dados = pipeline.leitura_sensores_para_tabela(tag)
        df = pd.DataFrame(dados, columns=pipeline.COLUNAS_SENSORES)
        st.subheader("Historico das Ultimas 24 Horas")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.line_chart(df.set_index("Timestamp")[["Temp (°C)", "Vibracao (mm/s)"]])
