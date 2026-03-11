from typing import Any


def build_error_report(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(errors, key=lambda e: (e.get("row_number", 0), e.get("field_name", "")))
