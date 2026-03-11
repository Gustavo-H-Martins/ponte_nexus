import pandas as pd


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [c.strip() for c in normalized.columns]
    if "currency" in normalized.columns:
        normalized["currency"] = normalized["currency"].astype(str).str.upper().str.strip()
    if "entity_type" in normalized.columns:
        normalized["entity_type"] = normalized["entity_type"].astype(str).str.upper().str.strip()
    if "transaction_type" in normalized.columns:
        normalized["transaction_type"] = normalized["transaction_type"].astype(str).str.lower().str.strip()
    return normalized
