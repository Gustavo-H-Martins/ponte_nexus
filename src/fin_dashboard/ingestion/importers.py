from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "source",
    "occurred_on",
    "description",
    "category",
    "tx_type",
    "amount",
    "account",
]


def read_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatorias ausentes: {missing}")
    return df[EXPECTED_COLUMNS]
