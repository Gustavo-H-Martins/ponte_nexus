from src.domain.enums import EntityType, TransactionType


def validate_flow_direction(
    transaction_type: TransactionType,
    source_entity_type: EntityType,
    destination_entity_type: EntityType,
) -> None:
    if transaction_type in {
        TransactionType.TRANSFER_PF_TO_PJ,
        TransactionType.INVESTMENT_PF_TO_PJ,
        TransactionType.LOAN_PF_TO_PJ,
    }:
        if source_entity_type != EntityType.PF or destination_entity_type != EntityType.PJ:
            raise ValueError("Transacao exige fluxo PF -> PJ")

    if transaction_type in {
        TransactionType.TRANSFER_PJ_TO_PF,
        TransactionType.DIVIDEND_DISTRIBUTION,
        TransactionType.PRO_LABORE,
    }:
        if source_entity_type != EntityType.PJ or destination_entity_type != EntityType.PF:
            raise ValueError("Transacao exige fluxo PJ -> PF")
