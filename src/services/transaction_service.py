from src.repositories.transaction_repository import TransactionRepository


class TransactionService:
    """Servico de operacoes sobre transacoes.

    O ciclo de vida da sessao e responsabilidade do chamador:

        with SessionLocal() as session:
            service = TransactionService(TransactionRepository(session))
            total = service.count()
    """

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self.transaction_repository = transaction_repository

    def count(self) -> int:
        return self.transaction_repository.count()
