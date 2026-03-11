import pandas as pd


def read_xlsx(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)
