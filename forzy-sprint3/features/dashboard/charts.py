"""
Sprint 2 — Componentes de graficos Plotly.
Usa os mesmos nomes de campo do sensor_provider da Sprint 1:
  temp_c, vibracao_mms, corrente_a, tensao_v, rotacao_rpm
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ─── Mapeamento de campos Sprint 1 → metadados visuais ─────────────────────

SENSORES = {
    "temp_c": {
        "label":    "Temperatura",
        "unit":     "°C",
        "cor":      "#FFA657",
        "warning":  75.0,
        "critical": 90.0,
        "range":    [15, 115],
    },
    "vibracao_mms": {
        "label":    "Vibracao",
        "unit":     "mm/s",
        "cor":      "#BC8CFF",
        "warning":  4.5,
        "critical": 7.1,
        "range":    [0, 12],
    },
    "corrente_a": {
        "label":    "Corrente",
        "unit":     "A",
        "cor":      "#58A6FF",
        "warning":  46.0,
        "critical": 51.0,
        "range":    [0, 60],
    },
    "tensao_v": {
        "label":    "Tensao",
        "unit":     "V",
        "cor":      "#3FB950",
        "warning":  None,
        "critical": None,
        "range":    [340, 430],
    },
    "rotacao_rpm": {
        "label":    "Rotacao",
        "unit":     "RPM",
        "cor":      "#FF7B72",
        "warning":  None,
        "critical": None,
        "range":    [0, 2000],
    },
}

# ─── Cores do tema ──────────────────────────────────────────────────────────

COR = {
    "bg":       "rgba(0,0,0,0)",
    "card":     "#161B22",
    "borda":    "#30363D",
    "saudavel": "#3FB950",
    "alerta":   "#D29922",
    "critico":  "#F85149",
    "texto":    "#E6EDF3",
    "muted":    "#8B949E",
}

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COR["texto"], size=11),
    margin=dict(l=10, r=10, t=28, b=10),
    hovermode="x unified",
    hoverlabel=dict(bgcolor=COR["card"], bordercolor=COR["borda"], font=dict(color=COR["texto"])),
)

_AXIS = dict(gridcolor=COR["borda"], linecolor=COR["borda"], tickfont=dict(color=COR["muted"]))


def _rgb(hex_cor: str) -> str:
    h = hex_cor.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _add_limites(fig, campo: str, row=None, col=None):
    info = SENSORES.get(campo, {})
    kw = dict(row=row, col=col) if row else {}
    if info.get("warning"):
        fig.add_hline(y=info["warning"], line_dash="dot", line_color=COR["alerta"],
                      line_width=1, opacity=0.7,
                      annotation_text="Atencao", annotation_font_color=COR["alerta"],
                      annotation_font_size=9, **kw)
    if info.get("critical"):
        fig.add_hline(y=info["critical"], line_dash="dash", line_color=COR["critico"],
                      line_width=1.5, opacity=0.85,
                      annotation_text="Critico", annotation_font_color=COR["critico"],
                      annotation_font_size=9, **kw)


# ─── Series temporais ───────────────────────────────────────────────────────

def time_series_multi(df: pd.DataFrame, campos: list[str], height: int = 420) -> go.Figure:
    """Subplots verticais, um por sensor selecionado."""
    n = len(campos)
    titulos = [f"{SENSORES[c]['label']} ({SENSORES[c]['unit']})" for c in campos]
    fig = make_subplots(rows=n, cols=1, shared_xaxes=True,
                        vertical_spacing=0.04, subplot_titles=titulos)

    for i, campo in enumerate(campos, start=1):
        info = SENSORES[campo]
        cor  = info["cor"]
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"], y=df[campo],
                fill="tozeroy",
                fillcolor=f"rgba({_rgb(cor)}, 0.09)",
                line=dict(color=cor, width=1.8),
                name=info["label"],
                hovertemplate=f"<b>{info['label']}</b>: %{{y:.2f}} {info['unit']}<extra></extra>",
            ),
            row=i, col=1,
        )
        _add_limites(fig, campo, row=i, col=1)
        fig.update_yaxes(**_AXIS, row=i, col=1)
        fig.update_xaxes(**_AXIS, row=i, col=1)

    # Colorir titulos dos subplots
    for ann, campo in zip(fig.layout.annotations, campos):
        ann.font.color = SENSORES[campo]["cor"]
        ann.font.size  = 11

    base = {k: v for k, v in _LAYOUT.items() if k not in ("xaxis", "yaxis", "margin")}
    fig.update_layout(**base, height=height, showlegend=False,
                      margin=dict(l=10, r=10, t=20, b=10))
    return fig


# ─── Gauge ──────────────────────────────────────────────────────────────────

def gauge(valor: float, campo: str, height: int = 210) -> go.Figure:
    """Velocimetro Plotly com faixas de limite."""
    info  = SENSORES.get(campo, {})
    label = f"{info.get('label','?')} ({info.get('unit','')})"
    r     = info.get("range", [0, 100])
    warn  = info.get("warning")
    crit  = info.get("critical")

    # Cor da barra
    if crit and valor >= crit:
        cor_barra = COR["critico"]
    elif warn and valor >= warn:
        cor_barra = COR["alerta"]
    else:
        cor_barra = COR["saudavel"]

    steps = []
    if warn and crit:
        steps = [
            dict(range=[r[0], warn], color="rgba(63,185,80,0.06)"),
            dict(range=[warn, crit], color="rgba(210,153,34,0.08)"),
            dict(range=[crit, r[1]], color="rgba(248,81,73,0.08)"),
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        gauge=dict(
            axis=dict(range=r, tickfont=dict(color=COR["muted"], size=9), tickcolor=COR["borda"]),
            bar=dict(color=cor_barra, thickness=0.55),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=1, bordercolor=COR["borda"],
            steps=steps,
            threshold=dict(line=dict(color=COR["critico"], width=2), thickness=0.75,
                           value=crit or r[1]) if crit else {},
        ),
        number=dict(font=dict(size=22, color=cor_barra), suffix=f" {info.get('unit','')}"),
        title=dict(text=info.get("label",""), font=dict(size=10, color=COR["muted"])),
    ))
    base = {k: v for k, v in _LAYOUT.items() if k not in ("xaxis","yaxis","hovermode","hoverlabel","margin")}
    fig.update_layout(**base, height=height, margin=dict(l=8, r=8, t=8, b=4))
    return fig


# ─── Scatter saude da planta ─────────────────────────────────────────────────

def scatter_saude(df: pd.DataFrame) -> go.Figure:
    """Temperatura x Vibracao de todos os motores, colorido por condicao."""
    mapa = {
        "critico":    (COR["critico"], "Critico"),
        "alerta":     (COR["alerta"],  "Atencao"),
        "manutencao": (COR["muted"],   "Manutencao"),
        "normal":     (COR["saudavel"],"Saudavel"),
    }
    fig = go.Figure()
    for cond, (cor, nome) in mapa.items():
        sub = df[df["condicao"] == cond]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["temp_c"], y=sub["vibracao_mms"],
            mode="markers+text",
            marker=dict(size=14, color=cor, line=dict(width=1.5, color="#0D1117")),
            text=sub["tag"], textposition="top center",
            textfont=dict(size=9, color=cor),
            name=nome,
            customdata=sub[["modelo", "corrente_a"]].values,
            hovertemplate=(
                "<b>%{text}</b><br>%{customdata[0]}<br>"
                "Temp: %{x:.1f}°C<br>Vibr: %{y:.2f} mm/s<br>"
                "Corrente: %{customdata[1]:.1f} A<extra></extra>"
            ),
        ))

    # Zonas de limite
    fig.add_hrect(y0=4.5, y1=7.1,  fillcolor="rgba(210,153,34,0.07)", line_width=0)
    fig.add_hrect(y0=7.1, y1=12,   fillcolor="rgba(248,81,73,0.07)",  line_width=0)
    fig.add_vrect(x0=75,  x1=90,   fillcolor="rgba(210,153,34,0.07)", line_width=0)
    fig.add_vrect(x0=90,  x1=115,  fillcolor="rgba(248,81,73,0.07)",  line_width=0)

    base = {k: v for k, v in _LAYOUT.items() if k not in ("margin",)}
    fig.update_layout(**base, height=370,
                      xaxis=dict(**_AXIS, title="Temperatura (°C)"),
                      yaxis=dict(**_AXIS, title="Vibracao (mm/s)"),
                      legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COR["texto"])),
                      margin=dict(l=20, r=10, t=10, b=30))
    return fig


# ─── Barras corrente ─────────────────────────────────────────────────────────

def barras_corrente(df: pd.DataFrame) -> go.Figure:
    """Ranking de corrente por motor."""
    mapa_cor = {"critico": COR["critico"], "alerta": COR["alerta"],
                "manutencao": COR["muted"], "normal": COR["saudavel"]}
    df_s = df.sort_values("corrente_a", ascending=True)
    cores = [mapa_cor.get(c, COR["saudavel"]) for c in df_s["condicao"]]

    fig = go.Figure(go.Bar(
        x=df_s["corrente_a"], y=df_s["tag"],
        orientation="h",
        marker=dict(color=cores, line=dict(width=0)),
        text=[f"{v:.1f} A" for v in df_s["corrente_a"]],
        textposition="outside",
        textfont=dict(size=9, color=COR["muted"]),
        hovertemplate="<b>%{y}</b><br>Corrente: %{x:.1f} A<extra></extra>",
    ))
    fig.add_vline(x=46, line_dash="dot",  line_color=COR["alerta"],  line_width=1, opacity=0.7)
    fig.add_vline(x=51, line_dash="dash", line_color=COR["critico"], line_width=1.5, opacity=0.8)

    base = {k: v for k, v in _LAYOUT.items() if k not in ("margin",)}
    fig.update_layout(**base, height=260,
                      xaxis=dict(**_AXIS, title="Corrente (A)", range=[0, 65]),
                      yaxis=dict(**_AXIS),
                      margin=dict(l=10, r=50, t=10, b=30), bargap=0.3)
    return fig
