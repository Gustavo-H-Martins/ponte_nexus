import pandas as pd


class AnalyticsService:
    def summarize_income_expense(self, df: pd.DataFrame) -> pd.DataFrame | pd.Series:
        summary = df.groupby(["entity_type", "transaction_type"], as_index=False)["amount"].sum()
        return summary
