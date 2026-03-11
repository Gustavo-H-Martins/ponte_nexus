from src.ingestion.pipeline import IngestionPipeline

_INVALID_CSV = "id,data,tipo,valor\n1,10-01-2026,PJ,abc\n"

_VALID_CSV = (
    "id_lancamento,data,tipo_entidade,nome_entidade,tipo_transacao,"
    "categoria,descricao,valor,moeda,conta_origem,conta_destino\n"
    "tx-001,2026-01-05,PJ,Empresa X,receita,vendas,Recebimento,15000.00,BRL,Conta Empresa,Conta Empresa\n"
)


def test_pipeline_fails_with_invalid_schema(tmp_path):
    file_path = tmp_path / "invalid.csv"
    file_path.write_text(_INVALID_CSV, encoding="utf-8")

    result = IngestionPipeline().run(str(file_path))
    assert result["status"] == "failed"
    assert result["records_valid"] == 0


def test_pipeline_processes_valid_csv(tmp_path):
    file_path = tmp_path / "valid.csv"
    file_path.write_text(_VALID_CSV, encoding="utf-8")

    result = IngestionPipeline().run(str(file_path))
    assert result["status"] == "processed"
    assert result["records_valid"] == 1
    assert result["errors"] == []


def test_pipeline_run_upload_valid():
    result, df = IngestionPipeline().run_upload("test.csv", _VALID_CSV.encode("utf-8"))
    assert result["status"] == "processed"
    assert df is not None
    assert len(df) == 1


def test_pipeline_run_upload_invalid():
    result, df = IngestionPipeline().run_upload("test.csv", _INVALID_CSV.encode("utf-8"))
    assert result["status"] == "failed"
    assert df is None
