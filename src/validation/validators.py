from typing import Any

import pandas as pd
from pydantic import ValidationError

from src.validation.schemas import TransactionImportSchema

REQUIRED_COLUMNS = {
    "transaction_id",
    "date",
    "entity_type",
    "entity_name",
    "transaction_type",
    "category",
    "description",
    "amount",
    "currency",
    "source_account",
    "destination_account",
}


def validate_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        return [
            {
                "row_number": 0,
                "field_name": "columns",
                "error_code": "missing_columns",
                "error_message": f"Colunas obrigatorias ausentes: {sorted(missing)}",
            }
        ]

    for idx, row in enumerate(df.to_dict(orient="records"), start=1):
        try:
            payload: dict[str, Any] = {str(k): v for k, v in row.items()}
            TransactionImportSchema(**payload)
        except ValidationError as exc:
            for issue in exc.errors():
                errors.append(
                    {
                        "row_number": idx,
                        "field_name": ".".join(str(loc) for loc in issue.get("loc", [])),
                        "error_code": issue.get("type", "validation_error"),
                        "error_message": issue.get("msg", "Valor invalido"),
                    }
                )

    return errors
