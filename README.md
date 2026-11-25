# Forzy — Sprint 3: Painel de Alertas e Estados

## Versões do projeto

- **Sprint 3**. O código na raiz contém o dashboard operacional, o painel de alertas e as telas de cadastro. Consulte as instruções abaixo para executar esta versão.
- **CP2 de Observabilidade**. O [guia do CP2](cp2-observabilidade/README.md) explica como executar a API de sensores e a interface Streamlit e reúne as capturas de Leitura atual, Histórico e Observabilidade.
- **Documentação final da Sprint 4**. A comparação entre as versões está disponível em [PDF](cp2-observabilidade/docs/Forzy_Sprint4_Documentacao_Final.pdf) e [Word](cp2-observabilidade/docs/Forzy_Sprint4_Documentacao_Final.docx).
- **Referência histórica**. O [commit `4a011c0`](https://github.com/murilo2318/forzy-sprint3/tree/4a011c0888b5510bdade60e73856f4786593d1fe) registra o estado imediatamente anterior à consolidação. O commit `11d5570` é a entrega original citada no documento.

Camada visual de inteligencia operacional e apoio a decisao para a plataforma
Forzy (Digital Twin de motores industriais). Da continuidade as Sprints 1
(cadastro de equipamentos) e 2 (dashboard operacional), adicionando a camada
analitica: deteccao de desvios, estados operacionais, resumos textuais (NLP) e
recomendacoes de manutencao.

## O que a Sprint 3 entrega

- **Painel de Alertas** como pagina inicial (antes da selecao de equipamento),
  com o panorama de toda a frota.
- **Resumos inteligentes (NLP)** dos alertas e estados. O texto e gerado pela
  camada `analytics/nlp_summary.py`. Hoje usa templates ("NLP simulado",
  sinalizado na interface); a assinatura da funcao ja e o contrato do modelo
  real — basta trocar o corpo quando o NLP treinado existir.
- **Apoio a decisao** via cards de recomendacao de manutencao, com prazo
  sugerido e destaque proporcional a urgencia.
- **Atualizacao** por botao manual e por **timer automatico** (auto-refresh a
  cada 10s). A cada atualizacao, uma notificacao simulada e injetada e o
  historico de eventos da sessao e alimentado.
- **Gestao de estado dinamica**: Saudavel -> Atencao -> Critico, com cores
  semanticas consistentes (verde / amarelo / vermelho).

## Arquitetura (desacoplada)

O front-end consome **apenas** o `alert_provider`. Ele nunca acessa as regras
ou o NLP diretamente — essa e a garantia de desacoplamento exigida na Sprint.

```
sensor_provider (Sprint 1/2)  ── telemetria (temp_c, vibracao_mms, ...)
        │
        ▼
analytics/rules_engine.py     ── classifica estado (fake ML / thresholds)
        │
        ▼
analytics/nlp_summary.py      ── gera resumo textual (fake NLP / contrato)
        │
        ▼
providers/alert_provider.py   ── monta o objeto Alert (orquestrador)
        │
        ▼
components/ + features/alertas ── camada visual (so consome)
```

### Objeto `Alert` (contrato consumido pelo front-end)

```python
{
  "equipamento_id": "MTR-004",
  "modelo": "ABB M2BAX 200MLA",
  "local": "Planta B — Compressores",
  "estado": "critico",          # saudavel | atencao | critico | manutencao
  "severidade": 2,              # 0..2
  "titulo": "Temperatura em nivel critico",
  "resumo_nlp": "Anomalia severa detectada no motor MTR-004 ...",
  "recomendacao": "Reduzir carga imediatamente e inspecionar ...",
  "prazo": "em ate 24h",
  "origem_texto": "template",   # template (simulado) | modelo (NLP real)
  "desvios": [ {campo, valor, nivel, limite, label, unidade}, ... ],
  "timestamp": "2026-08-17 14:32",
}
```

## Estrutura de pastas

```
forzy-sprint3/
├── app.py                          # entrypoint + roteamento (home = alertas)
├── analytics/
│   ├── rules_engine.py             # NOVO — regras de estado (thresholds)
│   └── nlp_summary.py              # NOVO — resumos textuais (NLP simulado)
├── components/                     # NOVO — componentes reutilizaveis
│   ├── alert_card.py
│   ├── state_badge.py
│   ├── recommendation_card.py
│   └── event_history.py
├── features/
│   ├── alertas/page.py             # NOVO — Painel de Alertas (home)
│   ├── dashboard/                  # Sprint 2
│   ├── cadastro/  lista/  sensores/# Sprint 1
├── providers/
│   ├── alert_provider.py           # NOVO — orquestrador desacoplado
│   ├── equipamento_provider.py     # Sprint 1/2 (inalterado)
│   └── sensor_provider.py          # Sprint 1/2 (inalterado)
├── pipelines/  state/  ui/
└── requirements.txt
```

## Estados simulados da frota

A condicao de cada motor vem do `sensor_provider` das sprints anteriores
(`_CONDICAO_SENSOR`), garantindo consistencia entre dashboard e painel:

| TAG     | Condicao   | Estado no painel |
|---------|------------|------------------|
| MTR-001 | normal     | Saudavel         |
| MTR-002 | manutencao | Manutencao       |
| MTR-003 | alerta     | Atencao          |
| MTR-004 | critico    | Critico          |

## Como rodar (Mac)

```bash
python3.13 -m pip install -r requirements.txt
python3.13 -m streamlit run app.py
```

## Demonstracao sugerida (video)

1. Abrir o app na home — Painel de Alertas com a frota classificada.
2. Ler o resumo textual (NLP) do motor critico (MTR-004) e sua recomendacao.
3. Clicar em **Atualizar** (ou ligar o **Auto 10s**) e ver a notificacao nova
   aparecer e alimentar o Historico de Eventos — transicao de estado.
4. Clicar em **Abrir dashboard** de um alerta e navegar para o dashboard da
   Sprint 2 (integracao entre sprints).

## Stack

Python · Streamlit · Pandas · NumPy · Plotly
