import pandas as pd


PJ_TO_PF_TYPES = {"transfer_pj_to_pf", "dividend_distribution", "pro_labore"}
PF_TO_PJ_TYPES = {"transfer_pf_to_pj", "investment_pf_to_pj", "loan_pf_to_pj"}


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
