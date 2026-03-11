import pandas as pd

from src.validation.validators import validate_dataframe

_VALID_ROW = {
    "transaction_id": "tx-001",
    "date": "2026-01-05",
    "entity_type": "PJ",
    "entity_name": "Empresa X",
    "transaction_type": "income",
    "category": "vendas",
    "description": "Recebimento",
    "amount": "15000.00",
    "currency": "BRL",
    "source_account": "Conta Empresa",
    "destination_account": "Conta Empresa",
}


def test_missing_columns_returns_error():
    df = pd.DataFrame([{"foo": 1}])
    errors = validate_dataframe(df)
    assert errors
    assert errors[0]["error_code"] == "missing_columns"


def test_valid_dataframe_returns_no_errors():
    df = pd.DataFrame([_VALID_ROW])
    errors = validate_dataframe(df)
    assert errors == []


def test_invalid_amount_returns_error():
    df = pd.DataFrame([{**_VALID_ROW, "amount": "-100.00"}])
    errors = validate_dataframe(df)
    assert any(e.get("field_name") == "amount" for e in errors)


def test_invalid_entity_type_returns_error():
    df = pd.DataFrame([{**_VALID_ROW, "entity_type": "SA"}])
    errors = validate_dataframe(df)
    assert errors
