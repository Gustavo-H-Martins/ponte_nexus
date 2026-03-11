import pandas as pd


FLOW_TYPES = {
    "transfer_pf_to_pj",
    "transfer_pj_to_pf",
    "investment_pf_to_pj",
    "loan_pf_to_pj",
    "dividend_distribution",
    "pro_labore",
}


def pf_pj_flow(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["transaction_type"].isin(FLOW_TYPES)].copy()
