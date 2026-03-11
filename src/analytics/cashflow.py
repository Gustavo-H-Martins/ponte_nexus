import pandas as pd


FLOW_TYPES = {
    "transferencia_pf_pj",
    "transferencia_pj_pf",
    "aporte_pf_pj",
    "emprestimo_pf_pj",
    "dividendos",
    "pro_labore",
}


def pf_pj_flow(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["transaction_type"].isin(FLOW_TYPES)].copy()
