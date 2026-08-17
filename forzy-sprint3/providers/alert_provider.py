"""
Sprint 3 — Provedor de Alertas (camada desacoplada).

Este e o UNICO ponto de contato do front-end com a inteligencia analitica.
Ele orquestra:
    sensor_provider (Sprint 1/2)  -> telemetria
    rules_engine    (Sprint 3)    -> estado operacional
    nlp_summary     (Sprint 3)    -> resumo textual

e devolve objetos `Alert` prontos para renderizacao. O front-end nao conhece
regras nem NLP: consome apenas a estrutura padronizada abaixo.

Contrato do objeto Alert:
    {
      "equipamento_id": "MTR-004",
      "modelo":         "ABB M2BAX 200MLA",
      "local":          "Planta B — Compressores",
      "estado":         "critico",          # saudavel|atencao|critico|manutencao
      "severidade":     2,                   # 0..2
      "titulo":         "Vibracao em nivel critico",
      "resumo_nlp":     "Anomalia severa detectada...",
      "recomendacao":   "Parar o motor e inspecionar rolamentos...",
      "prazo":          "em ate 24h",
      "origem_texto":   "template",          # template | modelo
      "desvios":        [ {campo, valor, nivel, limite, label, unidade}, ... ],
      "timestamp":      "2026-08-17 14:32",
    }
"""

from datetime import datetime

import providers.equipamento_provider as eq_provider
import providers.sensor_provider as sensor_provider
from analytics import rules_engine as rules
from analytics import nlp_summary as nlp


def _montar_alerta(tag: str) -> dict:
    """Monta o objeto Alert completo para uma TAG."""
    eq        = eq_provider.buscar_por_tag(tag) or {}
    historico = sensor_provider.historico_com_tendencia(tag, horas=1)
    ultima    = historico[-1] if historico else {}

    diagnostico = rules.avaliar(ultima) if ultima else \
        {"estado": "saudavel", "severidade": 0, "desvios": []}

    texto = nlp.gerar_resumo(tag, diagnostico, eq.get("modelo", ""))

    return {
        "equipamento_id": tag,
        "modelo":         eq.get("modelo", "—"),
        "local":          eq.get("local", "—"),
        "estado":         diagnostico["estado"],
        "severidade":     diagnostico["severidade"],
        "titulo":         texto["titulo"],
        "resumo_nlp":     texto["resumo"],
        "recomendacao":   texto["recomendacao"],
        "prazo":          texto["prazo"],
        "origem_texto":   texto["origem"],
        "desvios":        diagnostico["desvios"],
        "timestamp":      ultima.get("timestamp",
                                     datetime.now().strftime("%Y-%m-%d %H:%M")),
    }


def listar_alertas() -> list[dict]:
    """
    Retorna a lista de alertas de TODOS os equipamentos, ordenada por
    severidade (criticos primeiro). E o que a home consome.
    """
    alertas = [_montar_alerta(tag) for tag in eq_provider.tags_disponiveis()]
    # Ordena: critico (2) > atencao (1) > saudavel/manutencao (0)
    alertas.sort(key=lambda a: a["severidade"], reverse=True)
    return alertas


def resumo_frota(alertas: list[dict] | None = None) -> dict:
    """Contadores agregados para o cabecalho do painel."""
    if alertas is None:
        alertas = listar_alertas()
    return {
        "total":    len(alertas),
        "criticos": sum(1 for a in alertas if a["estado"] == "critico"),
        "atencao":  sum(1 for a in alertas if a["estado"] == "atencao"),
        "saudavel": sum(1 for a in alertas if a["estado"] == "saudavel"),
        "manutencao": sum(1 for a in alertas if a["estado"] == "manutencao"),
    }


# ─── Simulacao de nova notificacao (botao Atualizar / timer) ────────────────
# Como o projeto ainda nao esta ligado a uma base de eventos real, este bloco
# simula a chegada de um novo alerta a cada atualizacao, permitindo demonstrar
# a transicao de estado (Saudavel -> Atencao -> Critico) exigida na Sprint.

_EVENTOS_SIMULADOS = [
    {
        "equipamento_id": "MTR-003",
        "estado":         "atencao",
        "titulo":         "Elevacao de temperatura detectada",
        "resumo_nlp":     "Tendencia de aquecimento identificada no motor "
                          "MTR-003. Temperatura cruzou o limite de atencao "
                          "durante a ultima janela de leitura.",
        "recomendacao":   "Monitorar temperatura e checar ventilacao nas "
                          "proximas horas.",
        "prazo":          "nos proximos dias",
    },
    {
        "equipamento_id": "MTR-001",
        "estado":         "atencao",
        "titulo":         "Vibracao acima do baseline",
        "resumo_nlp":     "Aumento pontual de vibracao registrado no motor "
                          "MTR-001. Ainda dentro da faixa de atencao, sem "
                          "criticidade imediata.",
        "recomendacao":   "Agendar inspecao preventiva de rolamentos.",
        "prazo":          "nos proximos dias",
    },
    {
        "equipamento_id": "MTR-004",
        "estado":         "critico",
        "titulo":         "Pico de vibracao — falha iminente",
        "resumo_nlp":     "Novo pico de vibracao registrado no motor MTR-004, "
                          "reforcando o diagnostico de degradacao acelerada de "
                          "rolamento.",
        "recomendacao":   "Parar o motor e acionar manutencao corretiva "
                          "imediatamente.",
        "prazo":          "em ate 24h",
    },
]


def proxima_notificacao(indice: int) -> dict:
    """
    Retorna uma notificacao simulada com base num indice ciclico.
    Usada pelo painel a cada clique em 'Atualizar' ou disparo do timer.
    """
    evento = dict(_EVENTOS_SIMULADOS[indice % len(_EVENTOS_SIMULADOS)])
    evento["timestamp"]    = datetime.now().strftime("%H:%M:%S")
    evento["origem_texto"] = nlp.ORIGEM_NLP
    return evento
