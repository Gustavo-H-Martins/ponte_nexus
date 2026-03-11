import pandas as pd


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [c.strip() for c in normalized.columns]
    if "moeda" in normalized.columns:
        normalized["moeda"] = normalized["moeda"].astype(str).str.upper().str.strip()
    if "tipo_entidade" in normalized.columns:
        normalized["tipo_entidade"] = normalized["tipo_entidade"].astype(str).str.upper().str.strip()
    if "tipo_transacao" in normalized.columns:
        normalized["tipo_transacao"] = normalized["tipo_transacao"].astype(str).str.lower().str.strip()
    return normalized
