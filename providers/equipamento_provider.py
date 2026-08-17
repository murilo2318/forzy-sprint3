from datetime import datetime
from typing import Optional

# ─── Base de dados em memória (Sprint 1 + motores adicionados para Sprint 2) ─

_DB: dict[str, dict] = {
    "MTR-001": {
        "tag":                "MTR-001",
        "modelo":             "WEG W22 160L",
        "fabricante":         "WEG",
        "potencia_cv":        25.0,
        "tensao_v":           380,
        "corrente_nominal_a": 42.5,
        "rotacao_rpm":        1760,
        "fator_potencia":     0.86,
        "classe_isolamento":  "F",
        "ip":                 "IP55",
        "peso_kg":            145.0,
        "local":              "Planta A — Linha 1",
        "status":             "Operacional",
        "cadastrado_em":      "2024-11-10",
    },
    "MTR-002": {
        "tag":                "MTR-002",
        "modelo":             "Siemens 1LE1 200L",
        "fabricante":         "Siemens",
        "potencia_cv":        50.0,
        "tensao_v":           440,
        "corrente_nominal_a": 80.0,
        "rotacao_rpm":        1775,
        "fator_potencia":     0.88,
        "classe_isolamento":  "F",
        "ip":                 "IP55",
        "peso_kg":            280.0,
        "local":              "Planta A — Linha 2",
        "status":             "Em Manutenção",
        "cadastrado_em":      "2024-12-01",
    },
    # ── Sprint 2: motores adicionais para demo de navegação e alertas ──
    "MTR-003": {
        "tag":                "MTR-003",
        "modelo":             "WEG W22 200L",
        "fabricante":         "WEG",
        "potencia_cv":        60.0,
        "tensao_v":           380,
        "corrente_nominal_a": 65.0,
        "rotacao_rpm":        1760,
        "fator_potencia":     0.87,
        "classe_isolamento":  "F",
        "ip":                 "IP55",
        "peso_kg":            210.0,
        "local":              "Planta A — Linha 3",
        "status":             "Operacional",
        "cadastrado_em":      "2025-03-15",
    },
    "MTR-004": {
        "tag":                "MTR-004",
        "modelo":             "ABB M2BAX 200MLA",
        "fabricante":         "ABB",
        "potencia_cv":        30.0,
        "tensao_v":           380,
        "corrente_nominal_a": 51.0,
        "rotacao_rpm":        1775,
        "fator_potencia":     0.85,
        "classe_isolamento":  "F",
        "ip":                 "IP55",
        "peso_kg":            175.0,
        "local":              "Planta B — Compressores",
        "status":             "Operacional",
        "cadastrado_em":      "2025-05-20",
    },
}


def listar_todos() -> list[dict]:
    return [dict(eq) for eq in _DB.values()]


def buscar_por_tag(tag: str) -> Optional[dict]:
    entry = _DB.get(tag.strip().upper())
    return dict(entry) if entry else None


def salvar(dados: dict) -> tuple[bool, str]:
    tag = dados.get("tag", "").strip().upper()
    if not tag:
        return False, "TAG de identificacao e obrigatoria."
    if not dados.get("modelo", "").strip():
        return False, "Modelo do equipamento e obrigatorio."
    if not dados.get("fabricante", "").strip():
        return False, "Fabricante e obrigatorio."
    eh_novo = tag not in _DB
    data_cadastro = (
        _DB[tag]["cadastrado_em"] if not eh_novo
        else datetime.now().strftime("%Y-%m-%d")
    )
    _DB[tag] = {
        **dados,
        "tag":           tag,
        "cadastrado_em": data_cadastro,
        "status":        dados.get("status", "Operacional"),
    }
    acao = "cadastrado" if eh_novo else "atualizado"
    return True, f"Equipamento {tag} {acao} com sucesso."


def tags_disponiveis() -> list[str]:
    return sorted(_DB.keys())
