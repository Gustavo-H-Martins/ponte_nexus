from src.ingestion.pipeline import IngestionPipeline
from src.services.ingestion_service import IngestionService

_VALID_CSV = (
    "id_lancamento,data,tipo_entidade,nome_entidade,tipo_transacao,"
    "categoria,descricao,valor,moeda,conta_origem,conta_destino\n"
    "tx-001,2026-01-05,PJ,Empresa X,receita,vendas,Recebimento,15000.00,BRL,Conta Empresa,Conta Empresa\n"
    "tx-002,2026-01-10,PJ,Empresa X,pro_labore,remuneracao,Pro-labore,4000.00,BRL,Conta Empresa,Conta Pessoal\n"
)


def _make_service(session_factory) -> IngestionService:
    return IngestionService(
        pipeline=IngestionPipeline(), session_factory=session_factory
    )


def test_ingestion_service_persists_valid_records(in_memory_session_factory):
    service = _make_service(in_memory_session_factory)
    result = service.ingest_upload("test.csv", _VALID_CSV.encode("utf-8"))

    assert result["status"] == "processed"
    assert result["records_inserted"] == 2
    assert result["records_skipped"] == 0


def test_ingestion_service_skips_duplicate(in_memory_session_factory):
    service = _make_service(in_memory_session_factory)
    result1 = service.ingest_upload("test.csv", _VALID_CSV.encode("utf-8"))
    result2 = service.ingest_upload("test.csv", _VALID_CSV.encode("utf-8"))

    assert result1["records_inserted"] == 2
    assert result2["records_inserted"] == 0
    assert result2["records_skipped"] == 2


def test_ingestion_service_fails_with_invalid_csv(in_memory_session_factory):
    service = _make_service(in_memory_session_factory)
    result = service.ingest_upload(
        "bad.csv", b"id,data,tipo\n1,errado,PJ\n"
    )
    assert result["status"] == "failed"
    assert result["records_inserted"] == 0
