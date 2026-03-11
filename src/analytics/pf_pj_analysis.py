import pandas as pd


PJ_TO_PF_TYPES = {"transferencia_pj_pf", "dividendos", "pro_labore"}
PF_TO_PJ_TYPES = {"transferencia_pf_pj", "aporte_pf_pj", "emprestimo_pf_pj"}


def summarize_pf_pj_direction(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append(
        {
            "direction": "pj_to_pf",
            "amount": float(df[df["transaction_type"].isin(PJ_TO_PF_TYPES)]["amount"].sum()),
        }
    )
    rows.append(
        {
            "direction": "pf_to_pj",
            "amount": float(df[df["transaction_type"].isin(PF_TO_PJ_TYPES)]["amount"].sum()),
        }
    )
    return pd.DataFrame(rows)
