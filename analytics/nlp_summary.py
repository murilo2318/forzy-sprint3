"""
Sprint 3 — Camada de Processamento de Linguagem Natural (NLP).

Gera os RESUMOS TEXTUAIS dos alertas e das descricoes de estado operacional
exibidos no Painel de Alertas.

IMPORTANTE — ponto de integracao futura:
    A funcao publica `gerar_resumo(...)` e o CONTRATO que o modelo de NLP real
    (ex.: um LLM ou um summarizer treinado) devera respeitar. Hoje ela produz
    um resumo baseado em template ("fake NLP"), mas a assinatura e a estrutura
    de retorno ja estao prontas. Quando o NLP real existir, basta substituir o
    corpo desta funcao — nada no front-end precisa mudar.

    Para deixar explicito na interface que o texto ainda e simulado, cada
    resumo carrega a flag `origem: "template"` (troque para "modelo" quando
    o NLP real for plugado).
"""

from analytics import rules_engine as rules

# Flag global de origem do texto. Vira "modelo" quando o NLP real for plugado.
ORIGEM_NLP = "template"

# ─── Frases de recomendacao por nivel e metrica (apoio a decisao) ───────────

_RECOMENDACAO: dict[str, dict[str, str]] = {
    "critico": {
        "temp_c":       "Reduzir carga imediatamente e inspecionar sistema de "
                        "ventilacao/refrigeracao. Risco de dano ao isolamento.",
        "vibracao_mms": "Parar o motor e inspecionar rolamentos e alinhamento "
                        "do eixo. Vibracao em nivel de falha iminente.",
        "corrente_a":   "Verificar sobrecarga mecanica e conexoes eletricas. "
                        "Corrente acima do limite de projeto.",
    },
    "atencao": {
        "temp_c":       "Monitorar temperatura de perto e checar ventilacao "
                        "nas proximas horas.",
        "vibracao_mms": "Agendar inspecao preventiva de rolamentos. Tendencia "
                        "de vibracao em elevacao.",
        "corrente_a":   "Acompanhar consumo de corrente; avaliar condicao de "
                        "carga do equipamento.",
    },
}

_PRAZO = {
    "critico": "em ate 24h",
    "atencao": "nos proximos dias",
}


def _descreve_desvios(desvios: list[dict]) -> str:
    """Monta a parte textual que enumera as metricas fora do baseline."""
    partes = []
    for d in desvios:
        excesso = ""
        if d["limite"]:
            pct = (d["valor"] - d["limite"]) / d["limite"] * 100
            if pct > 0:
                excesso = f" ({pct:.0f}% acima do limite)"
        partes.append(
            f"{d['label']} em {d['valor']} {d['unidade']}{excesso}"
        )
    if not partes:
        return ""
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " e " + partes[-1]


def gerar_resumo(tag: str, diagnostico: dict, modelo_eq: str = "") -> dict:
    """
    CONTRATO DE NLP.
    Recebe a TAG, o diagnostico do rules_engine e (opcional) o modelo do motor.
    Devolve o pacote textual usado pelo front-end.

    Retorno:
        {
          "titulo":        "Vibracao critica detectada",
          "resumo":        "<paragrafo em linguagem natural>",
          "recomendacao":  "<acao sugerida para manutencao>",
          "prazo":         "em ate 24h",
          "origem":        "template",   # ou "modelo" quando o NLP real entrar
        }
    """
    estado  = diagnostico["estado"]
    desvios = diagnostico["desvios"]
    ident   = f"{tag}" + (f" ({modelo_eq})" if modelo_eq else "")

    # ── Estado saudavel ────────────────────────────────────────────────────
    if estado == "saudavel":
        return {
            "titulo":       "Operacao normal",
            "resumo":       f"O motor {ident} opera dentro dos parametros de "
                            f"baseline. Nenhum desvio significativo identificado "
                            f"na ultima leitura.",
            "recomendacao": "Manter rotina de monitoramento padrao.",
            "prazo":        "",
            "origem":       ORIGEM_NLP,
        }

    # ── Estado de manutencao ───────────────────────────────────────────────
    if estado == "manutencao":
        return {
            "titulo":       "Equipamento em manutencao",
            "resumo":       f"O motor {ident} encontra-se parado (rotacao e "
                            f"corrente nulas), consistente com intervencao de "
                            f"manutencao programada.",
            "recomendacao": "Confirmar ordem de servico e previsao de retorno "
                            "a operacao.",
            "prazo":        "",
            "origem":       ORIGEM_NLP,
        }

    # ── Estados de atencao / critico ───────────────────────────────────────
    metrica_principal = max(
        desvios,
        key=lambda d: (d["nivel"] == "critico", d["valor"]),
    )
    campo_prin = metrica_principal["campo"]
    texto_desvios = _descreve_desvios(desvios)

    if estado == "critico":
        titulo = f"{rules.LABELS.get(campo_prin, campo_prin)} em nivel critico"
        abertura = (f"Anomalia severa detectada no motor {ident}. ")
    else:
        titulo = f"Desvio em {rules.LABELS.get(campo_prin, campo_prin)}"
        abertura = (f"Desvio de comportamento identificado no motor {ident}. ")

    resumo = (
        abertura
        + f"Leitura atual: {texto_desvios}. "
        + ("Recomenda-se acao imediata da equipe de manutencao."
           if estado == "critico"
           else "Recomenda-se acompanhamento preventivo.")
    )

    recomendacao = _RECOMENDACAO.get(estado, {}).get(
        campo_prin,
        "Encaminhar para avaliacao da equipe de manutencao.",
    )

    return {
        "titulo":       titulo,
        "resumo":       resumo,
        "recomendacao": recomendacao,
        "prazo":        _PRAZO.get(estado, ""),
        "origem":       ORIGEM_NLP,
    }
