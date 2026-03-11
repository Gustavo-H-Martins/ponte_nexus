import io
from typing import Any

import pandas as pd

from src.ingestion.normalizer import normalize_dataframe
from src.ingestion.parser import detect_format
from src.ingestion.readers.csv_reader import read_csv
from src.ingestion.readers.json_reader import read_json
from src.ingestion.readers.xlsx_reader import read_xlsx
from src.validation.error_report import build_error_report
from src.validation.validators import validate_dataframe


class IngestionPipeline:
    def run(self, file_path: str) -> dict[str, Any]:
        """Executa o pipeline a partir de um caminho de arquivo."""
        file_format = detect_format(file_path)

        if file_format == ".csv":
            df = read_csv(file_path)
        elif file_format == ".xlsx":
            df = read_xlsx(file_path)
        else:
            df = read_json(file_path)

        result, _ = self._process(df)
        return result

    def run_upload(
        self, filename: str, file_bytes: bytes
    ) -> tuple[dict[str, Any], pd.DataFrame | None]:
        """Executa o pipeline a partir de bytes (upload Streamlit).

        Retorna (resultado, dataframe_valido | None).
        O dataframe e retornado apenas quando status == 'processed'.
        """
        file_format = detect_format(filename)

        if file_format == ".csv":
            df = read_csv(io.StringIO(file_bytes.decode("utf-8")))
        elif file_format == ".xlsx":
            df = read_xlsx(io.BytesIO(file_bytes))
        else:
            df = read_json(io.StringIO(file_bytes.decode("utf-8")))

        return self._process(df)

    def _process(
        self, df: pd.DataFrame
    ) -> tuple[dict[str, Any], pd.DataFrame | None]:
        df = normalize_dataframe(df)
        errors = validate_dataframe(df)

        if errors:
            return {
                "status": "failed",
                "errors": build_error_report(errors),
                "records_total": len(df),
                "records_valid": 0,
                "records_inserted": 0,
                "records_skipped": 0,
            }, None

        return {
            "status": "processed",
            "errors": [],
            "records_total": len(df),
            "records_valid": len(df),
            "records_inserted": 0,
            "records_skipped": 0,
        }, df
