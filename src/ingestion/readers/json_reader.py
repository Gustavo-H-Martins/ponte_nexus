import pandas as pd


def read_json(file_path: str) -> pd.DataFrame:
    return pd.read_json(file_path)
