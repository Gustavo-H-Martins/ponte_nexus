from pathlib import Path


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}


def detect_format(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato nao suportado: {ext}")
    return ext
