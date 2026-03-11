from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "nome_entidade",
    "data",
    "descricao",
    "categoria",
    "tipo_transacao",
    "valor",
    "conta_origem",
]


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes: {missing}")
    return df[EXPECTED_COLUMNS]
