from src.domain.enums import EntityType, TransactionType


def validate_flow_direction(
    transaction_type: TransactionType,
    source_entity_type: EntityType,
    destination_entity_type: EntityType,
) -> None:
    """Valida que a direção do fluxo é compatível com o tipo de transação.

    Levanta ValueError quando a combinação origem/destino contradiz o tipo
    declarado, evitando persistência silenciosa de dados inconsistentes.
    """
    if transaction_type in {
        TransactionType.TRANSFERENCIA_PF_PJ,
        TransactionType.APORTE_PF_PJ,
        TransactionType.EMPRESTIMO_PF_PJ,
    }:
        if source_entity_type != EntityType.PF or destination_entity_type != EntityType.PJ:
            raise ValueError("Transacao exige fluxo PF -> PJ")

    if transaction_type in {
        TransactionType.TRANSFERENCIA_PJ_PF,
        TransactionType.DIVIDENDOS,
        TransactionType.PRO_LABORE,
    }:
        if source_entity_type != EntityType.PJ or destination_entity_type != EntityType.PF:
            raise ValueError("Transacao exige fluxo PJ -> PF")
